import re
from time import mktime
from calendar import timegm
from datetime import datetime, timezone
import feedparser
import siteconfig
from myconfig import CONFIG
from utils import nomalizeSitename, tryint, genhash
from qbfunc import QbitClient
from humanbytes import HumanBytes
from optpick import TorrentParser, TorrentInfo, OptPickConfig
from models import db, RSSHistory, AcceptStatus, TorDownload, TorDetail
from dlhelper import (
    fillDetailWithNameParser,
    getSiteCookie
)
from dlhelper import checkMediaDbDupe, checkAutoCategory, addTorrent
from siteparser import fillDetailWithSiteDetailPage
from rssfilter import RssFilter
from rssactions import ActionFactory

from flask import current_app
from loguru import logger


import json
from torll.schemas.rss_schemas import RssFeedConfigBase

class RssFeed:
    def __init__(self, config: RssFeedConfigBase):
        self.name = config.name
        self.qbitname = config.qbitname if config.qbitname else ""
        self.enable = config.enable
        self.rssUrl = config.rssUrl
        self.filters = json.loads(config.filters) if config.filters else []
        self.site = nomalizeSitename(config.site)
        self.qbCategory = config.qbCategory if config.qbCategory else ""
        self.cookie = None # Cookie will be loaded dynamically
        self.getDetail = config.getDetail
        self.optpick = config.optpick if config.optpick else ""
        self.tag = config.tag if config.tag else ""
        self.action = config.action
        self.interval = config.interval
        self.siteConfigJson = siteconfig.getSiteConfig(self.site)

    def loadSiteCookie(self):
        with current_app.app_context():
            self.cookie = getSiteCookie(self.site)

    def to_dict(self):
        return {
            "name": self.name,
            "qbitname": self.qbitname,
            "enable": self.enable,
            "site": self.site,
            "get_detail": self.getDetail,
            "filter_count": len(self.filters),
            # 'tag': self.tag,
            "interval": self.interval,
        }

    def fetchRss(self):
        """Fetch and parse the RSS feed."""
        try:
            r = feedparser.parse(self.rssUrl)
            return r
        except:
            logger.error(f"url error")
            return None

    def existsInRssHistory(self, torname, subtitle):
        """Check if the given torrent name exists in the RSS history."""
        if not torname:
            raise ValueError("Empty torname")

        with current_app.app_context():
            try:
                exists = db.session.query(
                    db.exists().where(
                        db.and_(
                            RSSHistory.title == torname, RSSHistory.subtitle == subtitle
                        )
                    )
                ).scalar()
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                return False
        return exists

    def saveRssHistory(self, entry):
        with current_app.app_context():
            size_item = tryint(entry.links[1]["length"])
            dbrssitem = RSSHistory(
                site=self.site,
                title=entry.title,
                info_link=entry.link,
                download_link=entry.links[1]["href"],
                size=size_item,
            )
            db.session.add(dbrssitem)
            db.session.commit()
            return dbrssitem


    def missFields(self, entry):
        fields = ["id", "title", "link", "links"]
        mislist = [z for z in fields if not hasattr(entry, z)]
        return len(mislist) > 0

    def processRssFeeds(self):
        # 取得 RSS 条目
        logger.info(f"RSS {self.name} {self.site} - Fetching RSS feed")
        feed = self.fetchRss()
        if not feed:
            logger.error("rss url 配置错误")
            return
        rssFeedSum = len(feed.entries)
        logger.info(f"取得 RSS 条目： {rssFeedSum}")
        rssAccept = 0

        # 准备 action
        actionfactory = ActionFactory()
        feedaction = actionfactory.createAction(self.action)
        feedaction.prepare(self)

        # 准备 cookie
        self.loadSiteCookie()
        # 准备择优下载管理器
        # if self.optpick:
        #     optpick = OptimalPickManager(config_path=self.optpick)

        # 遍历 RSS 条目
        for i, rssentry in enumerate(feed.entries):
            # 缺关键字段，跳过
            if self.missFields(rssentry):
                logger.warning("miss field in rssitem, skip")
                continue

            # 解析 RSS 条目
            rssinfo = RssEntryInfo(rssentry)
            # 跳过 title, subtitle 有重复的
            if self.existsInRssHistory(rssinfo.title, rssinfo.subtitle):
                continue

            with current_app.app_context():
                # Create a new `RSSHistory` object with the parsed information.
                dbrssitem = RSSHistory(
                    rssname=self.name,
                    site=self.site,
                    title=rssinfo.title,
                    subtitle=rssinfo.subtitle,
                    info_link=rssentry.link,
                    download_link=rssinfo.download_link,
                    size=rssinfo.size,
                    rsstags=rssinfo.rsstagstr,
                    rsscatstr=rssinfo.cat,
                    pubdate=rssinfo.published,
                )
                dbrssitem.update_status(AcceptStatus.PENDING, '待处理')
                detail = fillDetailWithNameParser(rssinfo.title)
                if rssinfo.extitle:
                    detail.extitle = rssinfo.extitle  # 如果title 中能解析出片名
                dbrssitem.tor_detail = detail
                db.session.add(dbrssitem)
                db.session.commit()

                logger.info(
                    f"   {self.name}, {i}   {dbrssitem.title}, {HumanBytes.format(rssinfo.size)}"
                )
                
                rssfilter = RssFilter(self.filters)
                if feedaction.check(dbrssitem, detail, rssfilter):
                    feedaction.action(dbrssitem, detail, rssfilter)
                    rssAccept += 1
                    if dbrssitem.accept == AcceptStatus.ACCEPTED:
                        save_to_site_torrent(dbrssitem, detail)
                db.session.commit()
        logger.info(
            f"RSS {self.name} {self.site} - Total: {rssFeedSum}, Accepted: {rssAccept}"
        )

def save_to_site_torrent(rss_history_item: RSSHistory, tor_detail_item: TorDetail):
    """Saves or updates a SiteTorrent entry based on RSSHistory and TorDetail."""
    with current_app.app_context():
        # Check if a SiteTorrent with the same infolink already exists
        existing_site_torrent = db.session.query(SiteTorrent).filter(
            SiteTorrent.infolink == rss_history_item.info_link
        ).first()

        if existing_site_torrent:
            # Update existing entry
            site_torrent = existing_site_torrent
            logger.info(f"Updating existing SiteTorrent: {site_torrent.tortitle}")
        else:
            # Create new entry
            site_torrent = SiteTorrent()
            logger.info(f"Creating new SiteTorrent: {rss_history_item.title}")
            db.session.add(site_torrent)

        # Populate fields from RSSHistory
        site_torrent.addedon = rss_history_item.added_on
        site_torrent.site = rss_history_item.site
        site_torrent.tortitle = rss_history_item.title
        site_torrent.infolink = rss_history_item.info_link
        site_torrent.subtitle = rss_history_item.subtitle
        site_torrent.downlink = rss_history_item.download_link
        site_torrent.torsizeint = rss_history_item.size
        site_torrent.tordate = rss_history_item.pubdate

        # Populate fields from TorDetail
        if tor_detail_item:
            site_torrent.tmdbtitle = tor_detail_item.media_title
            site_torrent.tmdbcat = tor_detail_item.tmdbtype
            site_torrent.tmdbid = tryint(tor_detail_item.tmdbid)
            site_torrent.tmdbyear = tor_detail_item.year_int
            site_torrent.imdbstr = tor_detail_item.imdbstr
            site_torrent.imdbval = tor_detail_item.imdbval
            site_torrent.doubanid = tor_detail_item.doubanid
            site_torrent.doubanval = tor_detail_item.doubanval
            site_torrent.videocodec = tor_detail_item.videocodec
            site_torrent.audiocodec = tor_detail_item.audiocodec
            site_torrent.mediasource = tor_detail_item.mediasource
            site_torrent.resolution = tor_detail_item.resolution
            # Note: tmdbposter, genrestr, tmdboverview are not directly in TorDetail
            # and would require further TMDb lookup or parsing if needed.

        # Populate tag fields from RSSHistory.rsstags (if available and parsed)
        # This assumes rsstags is a comma-separated string of tags
        if rss_history_item.rsstags:
            tags = [tag.strip().lower() for tag in rss_history_item.rsstags.split(',')]
            site_torrent.taggy = "gy" in tags
            site_torrent.tagzz = "zz" in tags
            site_torrent.tagfree = "free" in tags
            site_torrent.tag2xfree = "2xfree" in tags
            site_torrent.tag50off = "50%" in tags or "50off" in tags
            # Add more tag mappings as needed

        # Default values for seednum, downnum, dlcount, torsizestr if not available
        site_torrent.seednum = site_torrent.seednum if site_torrent.seednum is not None else -1
        site_torrent.downnum = site_torrent.downnum if site_torrent.downnum is not None else -1
        site_torrent.dlcount = site_torrent.dlcount if site_torrent.dlcount is not None else 0
        site_torrent.torsizestr = HumanBytes.format(site_torrent.torsizeint) if site_torrent.torsizeint is not None else ""

        db.session.commit()



from dateutil import parser
class RssEntryInfo:
    def __init__(self, rssentry):
        self.cat = ""
        self.title = ""
        self.subtitle = ""
        self.rsstagstr = ""
        self.size = 0
        self.extitle = ""
        if 'published' in rssentry:
            self.published = parser.parse(rssentry["published"])
            # self.published = datetime.fromtimestamp(timegm(rssentry['published_parsed']), timezone.utc)
            self.parseRssEntry(rssentry)


    def __str__(self):
        return f"{self.cat} {self.title} {self.subtitle} {self.size} {self.extitle}"   
    
    def parseRssEntry(self, entry):
        self.parseRssTitle(entry.title)
        self.parseRssSubtitle(self.subtitle)
        self.size = tryint(entry.links[1]["length"])
        self.download_link = entry.links[1]["href"]

    def parseRssTitle(self, rsstitle):
        self.cat, self.title, self.subtitle, self.tags = "", "", "", []
        match = re.search(r"^(\[[^]]+\])?([^[]+)(\[(.*)\]$)?", rsstitle.strip())
        if match:
            if match[1]:
                self.cat = match[1][1:-1]
            if match[2]:
                self.title = match[2]
            if match[3]:
                self.subtitle = match[3]
                m2 = re.search(
                    r"(\[((\d*\.\d+|\d+\.\d*|\d+)(\s*?)(bytes|kb|mb|gb|tb|b|k|m|g|t))\]).*$",
                    self.subtitle,
                    re.I,
                )
                if m2:
                    self.size = m2.group(2)  # size无用，直接cut
                    self.subtitle = self.subtitle[: m2.start(1)] + self.subtitle[m2.end(1) :]
                """
                这个正则的解释：
                \[ - 匹配左方括号 [
                    ((?:[^\[\]]|\[[^\[\]]*\])*) - 捕获组，匹配：
                        (?:[^\[\]]|\[[^\[\]]*\])* - 非捕获组，重复匹配：
                            [^\[\]] - 非方括号字符，或者
                            \[[^\[\]]*\] - 一对完整的方括号及其内容（处理嵌套）
                \] - 匹配右方括号 ]
                """
                if m4 := re.search(r"\[((?:[^\[\]]|\[[^\[\]]*\])*)\]", self.subtitle, re.I):
                    subtitle_left = self.subtitle[: m4.start(1) - 1] + self.subtitle[m4.end(1) + 1 :]
                    self.subtitle = m4[1].strip()

                m3 = re.search(r"\[([^[\]]*\|[^[\]]*(?:\|[^[\]]*)*)\]\s*$", subtitle_left, re.I)
                if m3:
                    self.tags = [x.strip() for x in m3[1].split("|")]
                    self.rsstagstr = ",".join(self.tags)
                    # self.subtitle = self.subtitle[: (m3.start(0))]

    def parseRssSubtitle(self, subtitle):
        subtitle = subtitle.strip()
        subtitle = re.sub(r"\[.*连载\]|\s*点播\s*\|", "", subtitle)
        subtitle = re.sub(r"\w+剧[:：]", "", subtitle)
        m = re.search(r"[\[【]?([^\r\n/\\\[【|\<]+)\b", subtitle)
        # m = re.search(r'[\[【]?([\w \.\-]+)\b', subtitle)
        if m:
            subtitle = m[1].strip()
            if m1 := re.search(r"(.*)第\s*[\w\-]+\s*季", subtitle, re.I):
                subtitle = m1[1]
            if m1 := re.search(r"(.*)[第|全]\s*[\d\-]+\s*集", subtitle, re.I):
                subtitle = m1[1]
            if m1 := re.search(r"\d+年\d+月\w+\s+(.+)", subtitle, re.I):
                subtitle = m1[1]

        self.extitle = subtitle


