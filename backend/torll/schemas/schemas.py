from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TorDetailBase(BaseModel):
    media_title: Optional[str] = None
    extitle: Optional[str] = None
    subtitle: Optional[str] = None
    title_translation: Optional[str] = None
    area: Optional[str] = None
    year_int: Optional[int] = 0
    tmdbtype: Optional[str] = None
    tmdbid: Optional[str] = None
    season: Optional[str] = None
    episode: Optional[str] = None
    epnum: Optional[str] = None
    fullseason: Optional[bool] = None
    imdbstr: Optional[str] = None
    doubanid: Optional[str] = None
    imdbval: Optional[float] = 0.0
    doubanval: Optional[float] = 0.0
    resolution: Optional[str] = None
    mediasource: Optional[str] = None
    audiocodec: Optional[str] = None
    videocodec: Optional[str] = None
    group: Optional[str] = None
    sizestr: Optional[str] = None
    seednum: Optional[int] = -1
    downnum: Optional[int] = -1
    pubdate: Optional[str] = None

class TorDetailCreate(TorDetailBase):
    pass

class TorDetail(TorDetailBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TorMediaItemBase(BaseModel):
    torname: Optional[str] = None
    title: Optional[str] = None
    torsite: Optional[str] = None
    torsitecat: Optional[str] = None
    torimdb: Optional[str] = None
    torhash: Optional[str] = None
    torsize: Optional[int] = None
    tmdbid: Optional[int] = None
    tmdbcat: Optional[str] = None
    tmdbposter: Optional[str] = None
    tmdbyear: Optional[int] = None
    tmdbgenreids: Optional[str] = None
    location: Optional[str] = None
    plexid: Optional[str] = None
    season: Optional[str] = None
    episode: Optional[str] = None
    fullseason: Optional[bool] = True
    mediasource: Optional[str] = None
    resolution: Optional[str] = None
    tordownload_qbid: Optional[str] = None
    subtitle: Optional[str] = None
    group: Optional[str] = None
    medianame: Optional[str] = None
    infolink: Optional[str] = None
    qbitname: Optional[str] = None
    tor_detail_id: Optional[int] = None

class TorMediaItemCreate(TorMediaItemBase):
    pass

class TorMediaItem(TorMediaItemBase):
    id: int
    addedon: datetime
    tor_detail: Optional[TorDetail] = None

    class Config:
        orm_mode = True

class TorMediaItemUpdate(BaseModel):
    tmdbid: Optional[str] = None
    tmdbcat: Optional[str] = None

class SiteTorrentBase(BaseModel):
    site: Optional[str] = None
    tortitle: Optional[str] = None
    infolink: Optional[str] = None
    subtitle: Optional[str] = None
    downlink: Optional[str] = None
    mediatype: Optional[str] = None
    mediasource: Optional[str] = None
    tmdbtitle: Optional[str] = None
    tmdbcat: Optional[str] = None
    tmdbid: Optional[int] = None
    tmdbyear: Optional[int] = None
    tmdbposter: Optional[str] = None
    genrestr: Optional[str] = None
    tmdboverview: Optional[str] = None
    tagspecial: Optional[str] = None
    taggy: Optional[bool] = None
    tagzz: Optional[bool] = None
    tagfree: Optional[bool] = None
    tag2xfree: Optional[bool] = None
    tag50off: Optional[bool] = None
    imdbstr: Optional[str] = None
    imdbval: Optional[float] = None
    doubanval: Optional[float] = None
    doubanid: Optional[str] = None
    seednum: Optional[int] = None
    downnum: Optional[int] = None
    torsizestr: Optional[str] = None
    torsizeint: Optional[int] = None
    tordate: Optional[datetime] = None
    dlcount: Optional[int] = None
    videocodec: Optional[str] = None
    audiocodec: Optional[str] = None

class SiteTorrentCreate(SiteTorrentBase):
    pass

class SiteTorrent(SiteTorrentBase):
    id: int
    addedon: datetime

    class Config:
        orm_mode = True

class TorDownloadBase(BaseModel):
    src: Optional[str] = None
    qbitname: Optional[str] = None
    qbid: Optional[str] = None
    torname: Optional[str] = None
    site: Optional[str] = None
    subtitle: Optional[str] = None
    size: Optional[int] = None
    torimdb: Optional[str] = None
    infolink: Optional[str] = None
    downloadlink: Optional[str] = None
    taglist: Optional[str] = None
    auto_cat: Optional[str] = None
    torcped: Optional[bool] = None
    torcped_at: Optional[datetime] = None
    tor_detail_id: Optional[int] = None

class TorDownloadCreate(TorDownloadBase):
    pass

class TorDownload(TorDownloadBase):
    id: int
    addedon: datetime
    tor_detail: Optional[TorDetail] = None

    class Config:
        orm_mode = True

class DownloadRequest(BaseModel):
    download_link: str
    qbit_config_name: str

class TorrentCacheBase(BaseModel):
    site: Optional[str] = None
    searchword: Optional[str] = None
    tortitle: Optional[str] = None
    infolink: Optional[str] = None
    subtitle: Optional[str] = None
    downlink: Optional[str] = None
    mediatype: Optional[str] = None
    mediasource: Optional[str] = None
    tmdbtitle: Optional[str] = None
    tmdbcat: Optional[str] = None
    tmdbid: Optional[int] = None
    tmdbyear: Optional[int] = None
    tmdbposter: Optional[str] = None
    genrestr: Optional[str] = None
    tmdboverview: Optional[str] = None
    tagspecial: Optional[str] = None
    taggy: Optional[bool] = None
    tagzz: Optional[bool] = None
    tagfree: Optional[bool] = None
    tag2xfree: Optional[bool] = None
    tag50off: Optional[bool] = None
    imdbstr: Optional[str] = None
    imdbval: Optional[float] = None
    doubanval: Optional[float] = None
    doubanid: Optional[str] = None
    seednum: Optional[int] = None
    downnum: Optional[int] = None
    torsizestr: Optional[str] = None
    torsizeint: Optional[int] = None
    tordate: Optional[datetime] = None
    dlcount: Optional[int] = None
    videocodec: Optional[str] = None
    audiocodec: Optional[str] = None

class TorrentCacheCreate(TorrentCacheBase):
    pass

class TorrentCache(TorrentCacheBase):
    id: int
    addedon: datetime

    class Config:
        orm_mode = True

class PTSearchRequest(BaseModel):
    search_term: str
    site_name: str

class PtSiteBase(BaseModel):
    site: Optional[str] = None
    auto_update: Optional[bool] = None
    update_interval: Optional[int] = None
    icopath: Optional[str] = None
    cookie: Optional[str] = None
    siteNewLink: Optional[str] = None
    siteNewCheck: Optional[bool] = None
    lastSearchCheck: Optional[bool] = None
    lastResultCount: Optional[int] = None
    newTorCount: Optional[int] = None
    lastNewStatus: Optional[int] = None

class PtSiteCreate(PtSiteBase):
    site: str # Site name is required for creation
    cookie: str # Cookie is required for creation

class PtSiteUpdate(PtSiteBase):
    pass

class PtSite(PtSiteBase):
    id: int
    addedon: datetime
    last_update: datetime

    class Config:
        orm_mode = True