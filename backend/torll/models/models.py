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
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from torll.db.database import Base


class AcceptStatus(enum.IntEnum):
    PENDING = 0  # 待处理
    ACCEPTED = 1  # 已接受
    REJECTED = 2  # 已拒绝
    IGNORED = 3  # 已忽略
    ERROR = 4  # 接受但出错
    OPTPICK = 5  # 优选淘汰
    DUPE = 6  # 查重


class TorDetail(Base):
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


class TorMediaItem(Base):
    __tablename__ = "tor_media_items"
    id = Column(Integer, primary_key=True)
    addedon = Column(DateTime, default=datetime.now)
    torname = Column(String(256), index=True)
    title = Column(String(256), index=True)
    torsite = Column(String(64))
    torsitecat = Column(String(20))
    torimdb = Column(String(20), index=True)
    torhash = Column(String(120))
    torsize = Column(BigInteger)
    tmdbid = Column(Integer)
    tmdbcat = Column(String(20))
    tmdbposter = Column(String(120))
    tmdbyear = Column(Integer)
    tmdbgenreids = Column(String(20))
    location = Column(String(256))
    plexid = Column(String(120))
    season = Column(String(128))
    episode = Column(String(128))
    fullseason = Column(Boolean, default=True)
    mediasource = Column(String(32))
    resolution = Column(String(16))
    tordownload_qbid = Column(String(64))
    subtitle = Column(String(255))
    group = Column(String(64))
    medianame = Column(String(256), index=True)
    infolink = Column(String(256))
    qbitname = Column(String(64))
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")


class QbitConfig(Base):
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


class TorDownload(Base):
    __tablename__ = "tor_download"

    id = Column(Integer, primary_key=True)
    addedon = Column(DateTime, default=datetime.now)
    src = Column(String(16))
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")

    qbitname = Column(String(50), index=True)
    qbid = Column(String(128), index=True)
    torname = Column(String(256))
    site = Column(String(32))
    subtitle = Column(String(256))
    size = Column(BigInteger)
    torimdb = Column(String(20))
    infolink = Column(String(256))
    downloadlink = Column(String(256))
    taglist = Column(String(256))
    auto_cat = Column(String(64))
    torcped = Column(Boolean, default=False)
    torcped_at = Column(DateTime, default=datetime.now)


class SiteTorrent(Base):
    __tablename__ = "site_torrent"

    id = Column(Integer, primary_key=True)
    addedon = Column(DateTime, default=datetime.now)
    site = Column(String(32))
    tortitle = Column(String(256))
    infolink = Column(String(256))
    subtitle = Column(String(256))
    downlink = Column(String(256))
    mediatype = Column(String(32))
    mediasource = Column(String(32))
    tmdbtitle = Column(String(256))
    tmdbcat = Column(String(32))
    tmdbid = Column(Integer)
    tmdbyear = Column(Integer)
    tmdbposter = Column(String(64))
    genrestr = Column(String(128))
    tmdboverview = Column(Text)
    tagspecial = Column(String(32))
    taggy = Column(Boolean)
    tagzz = Column(Boolean)
    tagfree = Column(Boolean)
    tag2xfree = Column(Boolean)
    tag50off = Column(Boolean)
    imdbstr = Column(String(16))
    imdbval = Column(Float, default=0.0)
    doubanval = Column(Float, default=0.0)
    doubanid = Column(String(16))
    seednum = Column(Integer)
    downnum = Column(Integer)
    torsizestr = Column(String(16))
    torsizeint = Column(BigInteger)
    tordate = Column(DateTime)
    dlcount = Column(Integer, default=0)
    videocodec = Column(String(16))
    audiocodec = Column(String(16))


class PtSite(Base):
    __tablename__ = "pt_site"
    id = Column(Integer, primary_key=True)
    addedon = Column(DateTime, default=datetime.now)
    last_update = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    site = Column(String(32))
    auto_update = Column(Boolean)
    update_interval = Column(Integer, default=60)
    updateing = Column(Integer, default=0)
    icopath = Column(String(256))
    cookie = Column(String(1024))
    siteNewLink = Column(String(256))
    siteNewCheck = Column(Boolean, default=True)
    lastSearchCheck = Column(Boolean, default=False)
    lastResultCount = Column(Integer, default=0)
    newTorCount = Column(Integer, default=0)
    lastNewStatus = Column(Integer, default=0)


class TorrentCache(Base):
    __tablename__ = "torrent_cache"

    id = Column(Integer, primary_key=True)
    addedon = Column(DateTime, default=datetime.now)
    site = Column(String(32))
    searchword = Column(String(64))
    tortitle = Column(String(256))
    infolink = Column(String(256))
    subtitle = Column(String(256))
    downlink = Column(String(256))
    mediatype = Column(String(32))
    mediasource = Column(String(32))
    tmdbtitle = Column(String(256))
    tmdbcat = Column(String(16))
    tmdbid = Column(Integer)
    tmdbyear = Column(Integer)
    tmdbposter = Column(String(64))
    genrestr = Column(String(128))
    tmdboverview = Column(Text)
    tagspecial = Column(String(32))
    taggy = Column(Boolean)
    tagzz = Column(Boolean)
    tagfree = Column(Boolean)
    tag2xfree = Column(Boolean)
    tag50off = Column(Boolean)
    imdbstr = Column(String(16))
    imdbval = Column(Float, default=0.0)
    doubanval = Column(Float, default=0.0)
    doubanid = Column(String(16))
    seednum = Column(Integer)
    downnum = Column(Integer)
    torsizestr = Column(String(16))
    torsizeint = Column(BigInteger)
    tordate = Column(DateTime)
    dlcount = Column(Integer, default=0)
    videocodec = Column(String(16))
    audiocodec = Column(String(16))


class RssFeedConfig(Base):
    __tablename__ = "rss_feed_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    enable = Column(Boolean, default=True)
    rssUrl = Column(String(512), nullable=False)
    site = Column(String(64), nullable=False)
    qbCategory = Column(String(64))
    action = Column(String(64), default="download")
    interval = Column(Integer, default=600)
    # Filters can be stored as JSON string or in a separate table if complex
    filters = Column(Text) # Storing as JSON string for simplicity for now
    tag = Column(String(255))
    getDetail = Column(Boolean, default=False)
    optpick = Column(String(255))
    qbitname = Column(String(64))


class RSSHistory(Base):
    __tablename__ = "rss_history"

    id = Column(Integer, primary_key=True)
    site = Column(String(64), nullable=False, index=True)
    tor_detail_id = Column(
        Integer, ForeignKey("tor_details.id", ondelete="SET NULL"), nullable=True
    )
    tor_detail = relationship("TorDetail")
    title = Column(String(255))
    subtitle = Column(String(255))
    tid = Column(Integer)
    size = Column(BigInteger)
    info_link = Column(String(255))
    download_link = Column(String(255))
    accept = Column(Enum(AcceptStatus), default=AcceptStatus.PENDING)
    reason = Column(String(64))
    added_on = Column(DateTime, default=datetime.now)
    rssname = Column(String(64))
    rsstags = Column(String(64))
    pubdate = Column(DateTime)


class LogRecord(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    level = Column(String(10), nullable=False)
    logger_name = Column(String(100), nullable=False)
    message = Column(String(1000), nullable=False)
