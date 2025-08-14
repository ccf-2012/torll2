
import time
from loguru import logger
from myconfig import CONFIG

from models import db, TorDownload, AcceptStatus, SiteTorrent
from qbfunc import QbitClient
from utils import genhash, nomalizeSitename
from rssfilter import RssFilter
from dlhelper import checkAutoCategory, QbitConfigFactory, addTorrent, checkMediaDbDupe
from siteparser import fillDbitemWithTMDbParser, fillDetailWithSiteDetailPage
from humanbytes import HumanBytes
from rssoptickmgr import OptimalPickManager


class ActionFactory:
    def __init__(self):
        pass

    def createAction(self, action):
        if action == "download":
            return RssDownloadAction()
        elif action == "sitetorrent":
            return RssSiteTorAction()
        else:
            return None


class RssActions:
    def __init__(self):
        pass
    def prepare(self, rssfeed):
        pass
    def check(self, dbrssitem, detail, rssfilter):
        pass
    def action(self, dbrssitem, detail, rssfilter):
        pass


class RssDownloadAction(RssActions):
    def __init__(self):
        super().__init__()
        self.size_storage_space = 0
        self.qbconfig = None
        self.qbclient = None

    def prepare(self, rssfeed):
        super().prepare(rssfeed)
        self.getQbitClient(rssfeed.qbitname)
        self.rssfeed = rssfeed
        if not self.qbclient:
            logger.error("Qbit client not found")
            return
        self.size_storage_space = self.qbclient.getFreeSpace()

    def getQbitClient(self, qbitname):
        qbconfig = QbitConfigFactory.get_qbitconfig(qbitname)
        if qbconfig:
            self.qbconfig = qbconfig
            self.qbclient = QbitClient(self.qbconfig)
        

    def check(self, dbrssitem, detail, rssfilter):
        """检查 RSS 条目是否符合下载条件"""
        reason = rssfilter.applyFilters(dbrssitem)
        # 首先检查rssentry 中能提取的信息： title, subtitle, size, tag, cat, hr 
        if reason == "DL":
            if self.rssfeed.getDetail:
                # 取 detail 页面信息
                detail = fillDetailWithSiteDetailPage(
                    detail, self.rssfeed.site, dbrssitem.info_link, self.rssfeed.cookie
                )
                if not detail:
                    reason = "取站点页面出错"
                    dbrssitem.update_status(AcceptStatus.REJECTED, reason)
                    logger.error(f"fillDetailWithSiteDetailPage() error")
                    return False

                # 检查 detail 中的信息，当前有：rate_min
                reason = rssfilter.applyDetailFilter(detail)
                if reason != "DL":
                    logger.info(
                        f"Detail 检查未过： {self.rssfeed.name}, {dbrssitem.title}, imdb={detail.imdbval}, douban={detail.doubanval}"
                    )
                    dbrssitem.update_status(AcceptStatus.REJECTED, reason)
                    db.session.commit()
                    return False
            # 查重
            dupe, code = checkMediaDbDupe(
                dbrssitem.title, detail, infolink=dbrssitem.info_link
            )
            if dupe:
                dbrssitem.update_status(AcceptStatus.DUPE, code)
                db.session.commit()
                return False
            # 然后检查是否需要择优，需要择优的根据算法决定是否下载
            if self.rssfeed.optpick:
                op = OptimalPickManager(config_path=self.rssfeed.optpick)
                if not op.should_download(dbrssitem):
                    logger.info(
                        f"   {self.rssfeed.name}, OPT PICK - reject: {dbrssitem.title} "
                    )
                    dbrssitem.update_status(AcceptStatus.OPTPICK, "择优淘汰")
                    db.session.commit()
                    return False
            
            return True
        else:
            dbrssitem.update_status(AcceptStatus.REJECTED, reason)
            return False

    def action(self, dbrssitem, detail, rssfilter):
        self.download(dbrssitem, detail, rssfilter)

    def download(self, dbrssitem, detail, rssfilter):
        # 准备添加下载
        if rssfilter:
            filter_qbitname = rssfilter.getMatchQbitName()
            # 当 filter 中配置了 qbitname 时, 以 filter 中配置的 qbitname 为准
            if filter_qbitname:
                self.getQbitClient(filter_qbitname)

        if not self.qbclient:
            dbrssitem.update_status(AcceptStatus.ERROR, "qbit config err")
            return False
        
        t = TorDownload(
            torname=dbrssitem.title,
            tor_detail=detail,
            src="RSS",
            site=dbrssitem.site,
            subtitle=dbrssitem.subtitle,
            torimdb=detail.imdbstr,
            infolink=dbrssitem.info_link,
            downloadlink=dbrssitem.download_link,
            size=dbrssitem.size,
            qbid=genhash(dbrssitem.title),
            auto_cat=checkAutoCategory(dbrssitem.title, dbrssitem.subtitle),
            qbitname=self.qbconfig.qbitname,
        )
        db.session.add(t)
        db.session.commit()

        # Check if the configured Qbittorrent client has enough free space to download the torrent.
        enoughSpace = self.qbclient.enoughSpaceForTorrent(
            dbrssitem.size, self.size_storage_space, self.qbconfig.auto_delete
        )
        if not enoughSpace and CONFIG.autodelFailSkip:
            dbrssitem.update_status(
                AcceptStatus.IGNORED, "腾不出空间，跳过"
            )
            return False
        # Add the torrent to the client.
        r = addTorrent(
            downitem=t,
            checkspace=False,
            moretag=rssfilter.tag,
            rssAddPause=(not enoughSpace),
            qbitname=self.qbconfig.qbitname,
        )
        self.size_storage_space -= dbrssitem.size
        time.sleep(1)

        if r == 201:
            dbrssitem.update_status(AcceptStatus.ACCEPTED, 'DL')
            return True
        else:
            dbrssitem.update_status(AcceptStatus.ERROR, "qb err")
        return False


class RssSiteTorAction(RssActions):
    def __init__(self):
        pass
    def prepare(self, rssfeed):
        pass

    def check(self, dbrssitem, detail, rssfilter):
        return True
    
    def action(self, dbrssitem, detail, rssfilter):
        self.saveSiteTorrent(dbrssitem, detail)

    def saveSiteTorrent(self, dbrssitem, detail):
        dbrssitem.update_status(AcceptStatus.ACCEPTED, 'SiteTorrent')
        dbitem = SiteTorrent()
        dbitem.site = nomalizeSitename(dbrssitem.site)
        dbitem.tortitle = dbrssitem.title
        dbitem.infolink = dbrssitem.info_link
        dbitem.subtitle = dbrssitem.subtitle
        dbitem.downlink = dbrssitem.download_link
        dbitem.tordate = dbrssitem.pubdate
        dbitem.imdbstr = detail.imdbstr
        dbitem.torsizeint = dbrssitem.size
        # dbitem.torsizestr = HumanBytes.format(dbrssitem.size)
        # fillDbitemWithXPathParser(dbitem, row, cursite)
        fillDbitemWithTMDbParser(dbitem)
        logger.info(f"{dbitem.tortitle}, {dbitem.tordate}")

        db.session.add(dbitem)
        db.session.commit()


