from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from humanbytes import HumanBytes
from utils import getfulllink
import siteconfig

db = SQLAlchemy()


class TorDetail(db.Model):
    __tablename__ = "tor_details"
    id = Column(Integer, primary_key=True)
    media_title = Column(String(255), index=True)
    extitle = Column(String(255), index=True)
    subtitle = Column(String(255))
    title_translation = Column(String(255))
    area = Column(String(50))
    year_int = Column(Integer, default=0)
    tmdbtype = Column(String(20), index=True)
    tmdbid = Column(String(20), index=True)
    season = Column(String(20))
    episode = Column(String(20))
    epnum = Column(String(20))
    fullseason = Column(Boolean)
    imdbstr = Column(String(20), index=True)
    doubanid = Column(String(20), index=True)
    imdbval = Column(Float, default=0.0)
    doubanval = Column(Float, default=0.0)
    resolution = Column(String(20))
    mediasource = Column(String(20))
    audiocodec = Column(String(20))
    videocodec = Column(String(20))
    group = Column(String(50), index=True)
    sizestr = Column(String(20))
    seednum = Column(Integer, default=-1)
    downnum = Column(Integer, default=-1)
    pubdate = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "media_title": self.media_title,
            "extitle": self.extitle,
            "subtitle": self.subtitle,
            "title_translation": self.title_translation,
            "area": self.area,
            "year_int": self.year_int,
            "tmdbtype": self.tmdbtype,
            "tmdbid": self.tmdbid,
            "season": self.season,
            "episode": self.episode,
            "epnum": self.epnum,
            "imdbstr": self.imdbstr,
            "doubanid": self.doubanid,
            "imdbval": self.imdbval,
            "doubanval": self.doubanval,
            "resolution": self.resolution,
            "mediasource": self.mediasource,
            "audiocodec": self.audiocodec,
            "videocodec": self.videocodec,
            "group": self.group,
            "sizestr": self.sizestr,
            "seednum": self.seednum,
            "downnum": self.downnum,
            "pubdate": self.pubdate,
        }


class TorMediaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    torname = db.Column(db.String(256), index=True)
    title = db.Column(db.String(256), index=True)
    torsite = db.Column(db.String(64))
    torsitecat = db.Column(db.String(20))
    torimdb = db.Column(db.String(20), index=True)
    torhash = db.Column(db.String(120))
    torsize = db.Column(db.BigInteger)
    tmdbid = db.Column(db.Integer)
    tmdbcat = db.Column(db.String(20))
    tmdbposter = db.Column(db.String(120))
    tmdbyear = db.Column(db.Integer)
    tmdbgenreids = db.Column(db.String(20))
    location = db.Column(db.String(256))
    plexid = db.Column(db.String(120))
    season = db.Column(db.String(128))
    episode = db.Column(db.String(128))
    fullseason = db.Column(db.Boolean, default=True)
    mediasource = db.Column(db.String(32))
    resolution = db.Column(db.String(16))
    tordownload_qbid = db.Column(db.String(64))
    subtitle = db.Column(db.String(255))
    group = db.Column(db.String(64))
    medianame = db.Column(db.String(256), index=True)
    infolink = db.Column(db.String(256))
    qbitname = db.Column(db.String(64))
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")

    def to_dict(self):
        return {
            "id": self.id,
            "torname": self.torname,
            "medianame": self.medianame,
            "title": self.title,
            "subtitle": self.subtitle,
            "addedon": self.addedon,
            "torabbrev": self.torsite,
            "torsite": self.torsite,
            "infolink": self.infolink,
            "qbitname": self.qbitname,
            "torhash": self.torhash,
            "torsitecat": self.torsitecat,
            "torimdb": self.torimdb,
            "tmdbid": self.tmdbid,
            "tmdbcat": self.tmdbcat,
            "tmdbposter": self.tmdbposter,
            "tmdbgenreids": self.tmdbgenreids,
            "tmdbyear": self.tmdbyear,
            "location": self.location,
            "season": self.season,
            "episode": self.episode,
            "mediasource": self.mediasource,
            "resolution": self.resolution,
            "group": self.group,
            "medianame": self.medianame,
            "sizestr": HumanBytes.format(self.torsize),
            "detail_imdbval": self.tor_detail.imdbval if self.tor_detail else 0,
            "detail_doubanval": self.tor_detail.doubanval if self.tor_detail else 0,
        }


class QbitConfig(db.Model):
    __tablename__ = "qbit_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qbitname = Column(String(50))
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(50))
    password = Column(String(100))
    docker_from = Column(String(200))
    docker_to = Column(String(200))
    link_dir = Column(String(200))
    auto_delete = Column(Boolean, default=False)
    islocal = Column(Boolean, default=True)
    run_torcp_by_api = Column(Boolean, default=False)
    disk_free_margin = Column(Integer, default=5)
    add_pause = Column(Boolean, default=False)
    default = Column(Boolean, default=False)
    after_dl_prog = Column(String(200))
    mroot_mount = Column(String(200))

    def to_dict(self):
        return {
            "qbitname": self.qbitname,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "docker_from": self.docker_from,
            "docker_to": self.docker_to,
            "link_dir": self.link_dir,
            "auto_delete": self.auto_delete,
            "islocal": self.islocal,
        }

    def isNull(self):
        return False

class TorDownload(db.Model):
    __tablename__ = "tor_download"

    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    src = db.Column(db.String(16))
    # 关联到 TorDetail 的外键
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")

    qbitname = db.Column(db.String(50), index=True)
    qbid = db.Column(db.String(128), index=True)
    torname = db.Column(db.String(256))
    site = db.Column(db.String(32))
    subtitle = db.Column(db.String(256))
    size = db.Column(db.BigInteger)
    torimdb = db.Column(db.String(20))
    infolink = db.Column(db.String(256))
    downloadlink = db.Column(db.String(256))
    taglist = db.Column(db.String(256))
    auto_cat = db.Column(db.String(64))
    torcped = db.Column(db.Boolean, default=False)
    torcped_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        result = {
            "id": self.id,
            "src": self.src,
            "qbitname": self.qbitname,
            "site": self.site,
            "qbid": self.qbid,
            "addedon": self.addedon,
            "torname": self.torname,
            "subtitle": self.subtitle,
            "torimdb": self.torimdb,
            "infolink": self.infolink,
            "downloadlink": self.downloadlink,
            "size": HumanBytes.format(self.size) if self.size else "",
            "auto_cat": self.auto_cat,
            "torcped": self.torcped,
            "torcped_at": self.torcped_at,
            "detail_media_title": (
                self.tor_detail.media_title if self.tor_detail else ""
            ),
            "detail_extitle": self.tor_detail.extitle if self.tor_detail else "",
            "detail_year": self.tor_detail.year_int if self.tor_detail else 0,
            "detail_area": self.tor_detail.area if self.tor_detail else "",
            "detail_title_translation": (
                self.tor_detail.title_translation if self.tor_detail else ""
            ),
            "detail_tmdbtype": self.tor_detail.tmdbtype if self.tor_detail else "",
            "detail_imdbstr": self.tor_detail.imdbstr if self.tor_detail else "",
            "detail_doubanid": self.tor_detail.doubanid if self.tor_detail else "",
            "detail_seednum": self.tor_detail.seednum if self.tor_detail else -1,
            "detail_downnum": self.tor_detail.downnum if self.tor_detail else -1,
            "detail_resolution": self.tor_detail.resolution if self.tor_detail else "",
            "detail_mediasource": (
                self.tor_detail.mediasource if self.tor_detail else ""
            ),
            "detail_audiocodec": self.tor_detail.audiocodec if self.tor_detail else "",
            "detail_videocodec": self.tor_detail.videocodec if self.tor_detail else "",
            "detail_group": self.tor_detail.group if self.tor_detail else "",
            "detail_season": self.tor_detail.season if self.tor_detail else "",
            "detail_episode": self.tor_detail.episode if self.tor_detail else "",
            "detail_imdbval": self.tor_detail.imdbval if self.tor_detail else 0,
            "detail_doubanval": self.tor_detail.doubanval if self.tor_detail else 0,
            "detail_pubdate": self.tor_detail.pubdate if self.tor_detail else "",
        }
        return result


class SiteTorrent(db.Model):
    __tablename__ = "site_torrent"

    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    site = db.Column(db.String(32))
    tortitle = db.Column(db.String(256))
    infolink = db.Column(db.String(256))
    subtitle = db.Column(db.String(256))
    downlink = db.Column(db.String(256))
    mediatype = db.Column(db.String(32))
    mediasource = db.Column(db.String(32))
    tmdbtitle = db.Column(db.String(256))
    tmdbcat = db.Column(db.String(32))
    tmdbid = db.Column(db.Integer)
    tmdbyear = db.Column(db.Integer)
    tmdbposter = db.Column(db.String(64))
    genrestr = db.Column(db.String(128))
    tmdboverview = db.Column(db.Text)
    tagspecial = db.Column(db.String(32))
    taggy = db.Column(db.Boolean)
    tagzz = db.Column(db.Boolean)
    tagfree = db.Column(db.Boolean)
    tag2xfree = db.Column(db.Boolean)
    tag50off = db.Column(db.Boolean)
    imdbstr = db.Column(db.String(16))
    imdbval = db.Column(db.Float, default=0.0)
    doubanval = db.Column(db.Float, default=0.0)
    doubanid = db.Column(db.String(16))
    seednum = db.Column(db.Integer)
    downnum = db.Column(db.Integer)
    torsizestr = db.Column(db.String(16))
    torsizeint = db.Column(db.BigInteger)
    tordate = db.Column(db.DateTime)
    dlcount = db.Column(db.Integer, default=0)
    videocodec = db.Column(db.String(16))
    audiocodec = db.Column(db.String(16))

    def to_dict(self):
        return {
            "id": self.id,
            "addedon": self.addedon,
            "site": self.site,
            "tortitle": self.tortitle,
            "infolink": getfulllink(self.site, self.infolink),
            "subtitle": self.subtitle,
            "downlink": self.downlink,
            "taggy": self.taggy,
            "tagzz": self.tagzz,
            "tagfree": self.tagfree,
            "tag2xfree": self.tag2xfree,
            "tag50off": self.tag50off,
            "imdbstr": self.imdbstr,
            "imdbval": self.imdbval,
            "doubanval": self.doubanval,
            "seednum": self.seednum,
            "downnum": self.downnum,
            "torsizestr": HumanBytes.format(int(self.torsizeint)),
            "torsizeint": self.torsizeint,
            "tordate": self.tordate,
            "tmdbtitle": self.tmdbtitle,
            "tmdbcat": self.tmdbcat,
            "tmdbid": self.tmdbid,
            "tmdbyear": self.tmdbyear,
            "tmdbposter": self.tmdbposter,
            "genrestr": self.genrestr,
            "dlcount": self.dlcount,
            # 'exists': torDbExists(self.tmdbcat, self.tmdbid),
            "mediasource": self.mediasource,
            "videocodec": self.videocodec,
            "audiocodec": self.audiocodec,
        }


def siteFullLink(sitename, siteNewLink):
    if not siteNewLink:
        siteNewLink = "torrents.php"
    site = siteconfig.getSiteConfig(sitename)
    return site["baseurl"] + siteNewLink


class PtSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    last_update = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    site = db.Column(db.String(32))
    auto_update = db.Column(db.Boolean)
    update_interval = db.Column(db.Integer, default=60)
    updateing = db.Column(db.Integer, default=0)
    icopath = db.Column(db.String(256))
    cookie = db.Column(db.String(1024))
    siteNewLink = db.Column(db.String(256))
    siteNewCheck = db.Column(db.Boolean, default=True)
    lastSearchCheck = db.Column(db.Boolean, default=False)
    lastResultCount = db.Column(db.Integer, default=0)
    newTorCount = db.Column(db.Integer, default=0)
    lastNewStatus = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "last_update": self.last_update,
            "site": self.site,
            "auto_update": self.auto_update, 
            "update_interval": self.update_interval,
            "updateing": self.updateing,
            "icopath": self.icopath,
            "cookie": self.cookie,
            "siteNewLink": siteFullLink(self.site, self.siteNewLink),
            "lastResultCount": self.lastResultCount
        }


def siteCount(sitename):
    return SiteTorrent.query.filter_by(site=sitename).count()


def siteCountToday(sitename):
    return (
        SiteTorrent.query.filter_by(site=sitename)
        .filter(SiteTorrent.addedon > datetime.now().date())
        .count()
    )


class TorrentCache(db.Model):
    __tablename__ = "torrent_cache"

    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    site = db.Column(db.String(32))
    searchword = db.Column(db.String(64))
    tortitle = db.Column(db.String(256))
    infolink = db.Column(db.String(256))
    subtitle = db.Column(db.String(256))
    downlink = db.Column(db.String(256))
    mediatype = db.Column(db.String(32))
    mediasource = db.Column(db.String(32))
    tmdbtitle = db.Column(db.String(256))
    tmdbcat = db.Column(db.String(16))
    tmdbid = db.Column(db.Integer)
    tmdbyear = db.Column(db.Integer)
    tmdbposter = db.Column(db.String(64))
    genrestr = db.Column(db.String(128))
    tmdboverview = db.Column(db.Text)
    tagspecial = db.Column(db.String(32))
    taggy = db.Column(db.Boolean)
    tagzz = db.Column(db.Boolean)
    tagfree = db.Column(db.Boolean)
    tag2xfree = db.Column(db.Boolean)
    tag50off = db.Column(db.Boolean)
    imdbstr = db.Column(db.String(16))
    imdbval = db.Column(db.Float, default=0.0)
    doubanval = db.Column(db.Float, default=0.0)
    doubanid = db.Column(db.String(16))
    seednum = db.Column(db.Integer)
    downnum = db.Column(db.Integer)
    torsizestr = db.Column(db.String(16))
    torsizeint = db.Column(db.BigInteger)
    tordate = db.Column(db.DateTime)
    dlcount = db.Column(db.Integer, default=0)
    videocodec = db.Column(db.String(16))
    audiocodec = db.Column(db.String(16))

    def to_dict(self):
        return {
            "id": self.id,
            "addedon": self.addedon,
            "site": self.site,
            "searchword": self.searchword,
            "tortitle": self.tortitle,
            "infolink": getfulllink(self.site, self.infolink),
            "subtitle": self.subtitle,
            "downlink": self.downlink,
            "taggy": self.taggy,
            "tagzz": self.tagzz,
            "tagfree": self.tagfree,
            "tag2xfree": self.tag2xfree,
            "tag50off": self.tag50off,
            "imdbstr": self.imdbstr,
            "imdbval": self.imdbval,
            "doubanval": self.doubanval,
            "seednum": self.seednum,
            "downnum": self.downnum,
            "torsizestr": self.torsizestr,
            "torsizeint": self.torsizeint,
            "tordate": self.tordate,
            "dlcount": self.dlcount,
            "videocodec": self.videocodec,
            "audiocodec": self.audiocodec,
        }


class AcceptStatus(enum.IntEnum):
    PENDING = 0  # 待处理
    ACCEPTED = 1  # 已接受
    REJECTED = 2  # 已拒绝
    IGNORED = 3  # 已忽略
    ERROR = 4  # 接受但出错
    OPTPICK = 5  # 优选淘汰
    DUPE = 6  # 查重


class RSSHistory(db.Model):
    __tablename__ = "rss_history"

    # 主键和基础信息
    id = Column(Integer, primary_key=True)
    site = Column(String(64), nullable=False, index=True)  # RSS来源站点

    # 关联到 TorDetail 的外键
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")

    # RSS原始信息
    title = Column(String(255))  # RSS原始标题
    subtitle = Column(String(255))  # RSS副标题
    tid = Column(Integer)  # 站点种子ID
    size = Column(BigInteger)  # 文件大小
    info_link = Column(String(255))  # 种子信息页面链接
    download_link = Column(String(255))  # 种子下载链接

    # 处理状态
    accept = Column(Integer, default=AcceptStatus.PENDING)  # 接受状态
    reason = Column(String(64))  # 处理原因/备注
    added_on = Column(DateTime, default=datetime.now)  # 添加时间
    rssname = Column(String(64))
    rsstags = Column(String(64))
    pubdate = Column(DateTime)

    # 内存变量
    rsscatstr = ""

    @property
    def accept_status(self) -> AcceptStatus:
        """获取接受状态的枚举值"""
        return AcceptStatus(self.accept)

    def update_status(self, status: AcceptStatus, reason: str = None):
        """更新处理状态"""
        self.accept = status.value
        if reason:
            self.reason = reason

    def to_dict(self):
        """转换为字典格式"""
        result = {
            "id": self.id,
            "site": self.site,
            "title": self.title,
            "subtitle": self.subtitle,
            "tid": self.tid,
            "size": HumanBytes.format(int(self.size)),
            "info_link": self.info_link,
            "download_link": self.download_link,
            "accept": self.accept,
            "accept_status": self.accept_status.name,
            "reason": self.reason,
            "added_on": self.added_on,
            "rssname": self.rssname,
            "rsstags": self.rsstags,
            "detail_media_title": (
                self.tor_detail.media_title if self.tor_detail else ""
            ),
            "detail_extitle": self.tor_detail.extitle if self.tor_detail else "",
            "detail_year": self.tor_detail.year_int if self.tor_detail else 0,
            "detail_area": self.tor_detail.area if self.tor_detail else "",
            "detail_title_translation": (
                self.tor_detail.title_translation if self.tor_detail else ""
            ),
            "detail_tmdbtype": self.tor_detail.tmdbtype if self.tor_detail else "",
            "detail_imdbstr": self.tor_detail.imdbstr if self.tor_detail else "",
            "detail_doubanid": self.tor_detail.doubanid if self.tor_detail else "",
            "detail_seednum": self.tor_detail.seednum if self.tor_detail else -1,
            "detail_downnum": self.tor_detail.downnum if self.tor_detail else -1,
            "detail_resolution": self.tor_detail.resolution if self.tor_detail else "",
            "detail_mediasource": (
                self.tor_detail.mediasource if self.tor_detail else ""
            ),
            "detail_audiocodec": self.tor_detail.audiocodec if self.tor_detail else "",
            "detail_videocodec": self.tor_detail.videocodec if self.tor_detail else "",
            "detail_group": self.tor_detail.group if self.tor_detail else "",
            "detail_season": self.tor_detail.season if self.tor_detail else "",
            "detail_episode": self.tor_detail.episode if self.tor_detail else "",
            "detail_imdbval": self.tor_detail.imdbval if self.tor_detail else 0,
            "detail_doubanval": self.tor_detail.doubanval if self.tor_detail else 0,
            "detail_pubdate": self.tor_detail.pubdate if self.tor_detail else "",
        }
        return result


class LogRecord(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    level = Column(String(10), nullable=False)
    logger_name = Column(String(100), nullable=False)
    message = Column(String(1000), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level,
            "logger_name": self.logger_name,
            "message": self.message,
        }
