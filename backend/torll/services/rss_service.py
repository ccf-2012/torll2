import re
from datetime import datetime, timezone
import feedparser
from sqlalchemy.orm import Session
from sqlalchemy import exists, and_

from torll.models import models
from torll.schemas import rss_schemas
from torll.services import tmdb_service
from torll.core.config import settings

from loguru import logger
from dateutil import parser

# --- Placeholder/Simplified functions for external dependencies ---
# In a real scenario, these would be properly implemented or integrated.

def nomalizeSitename(name: str) -> str:
    # Simplified for now
    return name.lower().replace(" ", "")

def tryint(value) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

import math # Added for HumanBytes

class HumanBytes:
    @staticmethod
    def format(size_bytes: int) -> str:
        if size_bytes is None: return "N/A"
        if size_bytes == 0: return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])


# --- End Placeholder/Simplified functions ---

def save_to_site_torrent(db: Session, rss_history_item: models.RSSHistory, tor_detail_item: models.TorDetail):
    """Saves or updates a SiteTorrent entry based on RSSHistory and TorDetail."""
    # Check if a SiteTorrent with the same infolink already exists
    existing_site_torrent = db.query(models.SiteTorrent).filter(
        models.SiteTorrent.infolink == rss_history_item.info_link
    ).first()

    if existing_site_torrent:
        # Update existing entry
        site_torrent = existing_site_torrent
        logger.info(f"Updating existing SiteTorrent: {site_torrent.tortitle}")
    else:
        # Create new entry
        site_torrent = models.SiteTorrent()
        logger.info(f"Creating new SiteTorrent: {rss_history_item.title}")
        db.add(site_torrent)

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

    db.commit()

class RssFeed:
    def __init__(self, taskconfig: rss_schemas.RssFeedConfigBase):
        self.name = taskconfig.name
        self.qbitname = taskconfig.qbitname
        self.enable = taskconfig.enable
        self.rssUrl = taskconfig.rssUrl
        self.filters = taskconfig.filters
        self.site = nomalizeSitename(taskconfig.site)
        self.qbCategory = taskconfig.qbCategory
        self.cookie = taskconfig.cookie # This will need proper handling later
        self.getDetail = taskconfig.getDetail
        self.optpick = taskconfig.optpick
        self.tag = taskconfig.tag
        self.action = taskconfig.action
        self.interval = taskconfig.interval
        # self.siteConfigJson = siteconfig.getSiteConfig(self.site) # External dependency

    # def loadSiteCookie(self):
    #     # This needs proper integration with siteconfig/cookie management
    #     pass

    def fetchRss(self):
        """Fetch and parse the RSS feed."""
        try:
            r = feedparser.parse(self.rssUrl)
            return r
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {self.rssUrl}: {e}")
            return None

    def existsInRssHistory(self, db: Session, torname: str, subtitle: str) -> bool:
        """Check if the given torrent name exists in the RSS history."""
        if not torname:
            raise ValueError("Empty torname")

        try:
            exists_query = db.query(exists().where(
                and_(
                    models.RSSHistory.title == torname,
                    models.RSSHistory.subtitle == subtitle
                )
            )).scalar()
            return exists_query
        except Exception as e:
            logger.error(f"An error occurred checking RSS history: {e}")
            return False

    def missFields(self, entry):
        fields = ["id", "title", "link", "links"]
        mislist = [z for z in fields if not hasattr(entry, z)]
        return len(mislist) > 0

    def processRssFeeds(self, db: Session):
        # 取得 RSS 条目
        logger.info(f"RSS {self.name} {self.site} - Fetching RSS feed")
        feed = self.fetchRss()
        if not feed:
            logger.error("RSS URL configuration error or fetch failed.")
            return
        rssFeedSum = len(feed.entries)
        logger.info(f"取得 RSS 条目： {rssFeedSum}")
        rssAccept = 0

        # Set TMDb API key
        tmdb_service.tmdb.API_KEY = settings.TMDB_API_KEY

        # 遍历 RSS 条目
        for i, rssentry in enumerate(feed.entries):
            # 缺关键字段，跳过
            if self.missFields(rssentry):
                logger.warning("Missing fields in RSS item, skipping.")
                continue

            # 解析 RSS 条目
            rssinfo = RssEntryInfo(rssentry)
            # 跳过 title, subtitle 有重复的
            if self.existsInRssHistory(db, rssinfo.title, rssinfo.subtitle):
                logger.info(f"Duplicate RSS entry found: {rssinfo.title} - {rssinfo.subtitle}, skipping.")
                continue

            # Create a new `RSSHistory` object with the parsed information.
            dbrssitem = models.RSSHistory(
                rssname=self.name,
                site=self.site,
                title=rssinfo.title,
                subtitle=rssinfo.subtitle,
                info_link=rssentry.link,
                download_link=rssinfo.download_link,
                size=rssinfo.size,
                rsstags=rssinfo.rsstagstr,
                # rsscatstr=rssinfo.cat, # This field is not in models.RSSHistory
                pubdate=rssinfo.published,
            )
            dbrssitem.accept = models.AcceptStatus.PENDING.value # Use enum value
            dbrssitem.reason = '待处理'

            # Use TMDb service to get TorDetail
            detail = models.TorDetail() # Initialize with empty TorDetail
            if rssinfo.title:
                tmdb_result = tmdb_service.search_tmdb(rssinfo.title, media_type="multi")
                if tmdb_result:
                    detail.media_title = tmdb_result.get('title') or tmdb_result.get('name')
                    detail.tmdbid = str(tmdb_result.get('id'))
                    detail.tmdbtype = tmdb_result.get('media_type')
                    detail.pubdate = tmdb_result.get('release_date') or tmdb_result.get('first_air_date')
                    # Populate other fields as needed from tmdb_result
            dbrssitem.tor_detail = detail

            db.add(dbrssitem)
            db.commit()
            db.refresh(dbrssitem)

            logger.info(
                f"   {self.name}, {i}   {dbrssitem.title}, {HumanBytes.format(rssinfo.size)}"
            )
            
            # Placeholder for rssfilter and feedaction
            # For now, we will just assume the item is accepted and save it to SiteTorrent
            dbrssitem.accept = models.AcceptStatus.ACCEPTED.value
            save_to_site_torrent(db, dbrssitem, detail)
            db.commit()

        logger.info(
            f"RSS {self.name} {self.site} - Total: {rssFeedSum}, Accepted: {rssAccept}"
        )


class RssEntryInfo:
    def __init__(self, rssentry):
        self.cat = ""
        self.title = ""
        self.subtitle = ""
        self.rsstagstr = ""
        self.size = 0
        self.extitle = ""
        self.download_link = ""
        self.published = None

        if 'published' in rssentry:
            try:
                self.published = parser.parse(rssentry["published"])
            except Exception as e:
                logger.warning(f"Could not parse published date: {rssentry.get('published')}. Error: {e}")
                self.published = datetime.now(timezone.utc) # Default to now if parsing fails
            self.parseRssEntry(rssentry)
        else:
            logger.warning("RSS entry has no 'published' field.")
            self.published = datetime.now(timezone.utc)
            self.parseRssEntry(rssentry)


    def __str__(self):
        return f"{self.cat} {self.title} {self.subtitle} {self.size} {self.extitle}"   
    
    def parseRssEntry(self, entry):
        self.parseRssTitle(entry.title)
        # self.parseRssSubtitle(self.subtitle) # This seems to modify self.extitle based on self.subtitle
        self.size = tryint(entry.links[1]["length"])
        self.download_link = entry.links[1]["href"]

    def parseRssTitle(self, rsstitle):
        self.cat, self.title, self.subtitle, self.tags = "", "", "", []
        match = re.search(r"^(\[[^\]]+\])?([^\[]+)(\[(.*)\]$)?", rsstitle.strip())
        if match:
            if match[1]:
                self.cat = match[1][1:-1]
            if match[2]:
                self.title = match[2].strip()
            if match[3]:
                self.subtitle = match[3].strip()
                m2 = re.search(
                    r"(\[((\d*\.\d+|\d+\.\d+|\d+)(\s*?)(bytes|kb|mb|gb|tb|b|k|m|g|t))\].*$",
                    self.subtitle,
                    re.I,
                )
                if m2:
                    # self.size = m2.group(2)  # size useless, cut directly
                    self.subtitle = self.subtitle[: m2.start(1)] + self.subtitle[m2.end(1) :]
                
                if m4 := re.search(r" \[((?:[^\\\\[\\]]|\\\\[^\\\\[\\]]*\\\\])*)\]", self.subtitle, re.I):
                    subtitle_left = self.subtitle[: m4.start(1) - 1] + self.subtitle[m4.end(1) + 1 :]
                    self.subtitle = m4[1].strip()

                m3 = re.search(r" \[([^[\\\\]]*?)\|([^[\\\\]]*?)(?:\\|([^[\\\\]]*?))*?\]\s*$", subtitle_left, re.I)
                if m3:
                    self.tags = [x.strip() for x in m3[1].split("|")]
                    self.rsstagstr = ",".join(self.tags)

    # The original parseRssSubtitle modifies self.extitle based on self.subtitle
    # This logic needs to be carefully reviewed and potentially moved or adapted.
    # For now, I'm simplifying it.
    # def parseRssSubtitle(self, subtitle):
    #     subtitle = subtitle.strip()
    #     subtitle = re.sub(r" \[.*连载\]|\s*点播\s*\|", "", subtitle)
    #     subtitle = re.sub(r"\w+剧[:：]", "", subtitle)
    #     m = re.search(r"[ \[【]?([^\r\n/\\ \[【|<>]+)\b", subtitle)
    #     if m:
    #         subtitle = m[1].strip()
    #         if m1 := re.search(r"(.*)第\s*[\w\-]+\s*季", subtitle, re.I):
    #             subtitle = m1[1]
    #         if m1 := re.search(r"(.*)[第|全]\s*[\d\-]+\s*集", subtitle, re.I):
    #             subtitle = m1[1]
    #         if m1 := re.search(r"\d+年\d+月\w+\s+(.+)", subtitle, re.I):
    #             subtitle = m1[1]
    #     self.extitle = subtitle
