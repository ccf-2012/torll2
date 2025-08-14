from sqlalchemy.orm import Session
from typing import List, Optional
from torll.models import models
from torll.schemas import schemas, rss_schemas

def get_tor_detail(db: Session, tor_detail_id: int):
    return db.query(models.TorDetail).filter(models.TorDetail.id == tor_detail_id).first()

def create_tor_detail(db: Session, tor_detail: schemas.TorDetailCreate):
    db_tor_detail = models.TorDetail(**tor_detail.dict())
    db.add(db_tor_detail)
    db.commit()
    db.refresh(db_tor_detail)
    return db_tor_detail

def get_tor_media_item(db: Session, tor_media_item_id: int):
    return db.query(models.TorMediaItem).filter(models.TorMediaItem.id == tor_media_item_id).first()

# CRUD operations for RssFeedConfig
def create_rss_feed_config(db: Session, rss_feed_config: rss_schemas.RssFeedConfigCreate):
    db_rss_feed_config = models.RssFeedConfig(**rss_feed_config.dict())
    db.add(db_rss_feed_config)
    db.commit()
    db.refresh(db_rss_feed_config)
    return db_rss_feed_config

def get_rss_feed_config(db: Session, config_id: int):
    return db.query(models.RssFeedConfig).filter(models.RssFeedConfig.id == config_id).first()

def get_rss_feed_config_by_name(db: Session, name: str):
    return db.query(models.RssFeedConfig).filter(models.RssFeedConfig.name == name).first()

def get_rss_feed_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RssFeedConfig).offset(skip).limit(limit).all()

def update__feed_config(db: Session, config_id: int, rss_feed_config: rss_schemas.RssFeedConfigCreate):
    db_rss_feed_config = db.query(models.RssFeedConfig).filter(models.RssFeedConfig.id == config_id).first()
    if db_rss_feed_config:
        for key, value in rss_feed_config.dict().items():
            setattr(db_rss_feed_config, key, value)
        db.commit()
        db.refresh(db_rss_feed_config)
    return db_rss_feed_config

def delete_rss_feed_config(db: Session, config_id: int):
    db_rss_feed_config = db.query(models.RssFeedConfig).filter(models.RssFeedConfig.id == config_id).first()
    if db_rss_feed_config:
        db.delete(db_rss_feed_config)
        db.commit()
    return db_rss_feed_config

def get_rss_history_by_name(db: Session, rss_name: str):
    return db.query(models.RSSHistory).filter(models.RSSHistory.rssname == rss_name).all()

def get_site_torrents(db: Session, skip: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_order: Optional[str] = None, title: Optional[str] = None):
    query = db.query(models.SiteTorrent)
    if title:
        query = query.filter(models.SiteTorrent.tortitle.contains(title))
    if sort_by:
        if sort_order == "desc":
            query = query.order_by(getattr(models.SiteTorrent, sort_by).desc())
        else:
            query = query.order_by(getattr(models.SiteTorrent, sort_by).asc())
    return query.offset(skip).limit(limit).all()

def get_downloads(db: Session, skip: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_order: Optional[str] = None, name: Optional[str] = None):
    query = db.query(models.TorDownload)
    if name:
        query = query.filter(models.TorDownload.torname.contains(name))
    if sort_by:
        if sort_order == "desc":
            query = query.order_by(getattr(models.TorDownload, sort_by).desc())
        else:
            query = query.order_by(getattr(models.TorDownload, sort_by).asc())
    return query.offset(skip).limit(limit).all()

def get_media_items(db: Session, skip: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_order: Optional[str] = None, title: Optional[str] = None):
    query = db.query(models.TorMediaItem)
    if title:
        query = query.filter(models.TorMediaItem.title.contains(title))
    if sort_by:
        if sort_order == "desc":
            query = query.order_by(getattr(models.TorMediaItem, sort_by).desc())
        else:
            query = query.order_by(getattr(models.TorMediaItem, sort_by).asc())
    return query.offset(skip).limit(limit).all()

def get_qbit_config_by_name(db: Session, name: str):
    return db.query(models.QbitConfig).filter(models.QbitConfig.qbitname == name).first()

def delete_download(db: Session, download_id: int):
    db_download = db.query(models.TorDownload).filter(models.TorDownload.id == download_id).first()
    if db_download:
        db.delete(db_download)
        db.commit()
    return db_download

def update_media_item(db: Session, media_item_id: int, media_item: schemas.TorMediaItemUpdate):
    db_media_item = db.query(models.TorMediaItem).filter(models.TorMediaItem.id == media_item_id).first()
    if db_media_item:
        if media_item.tmdbid:
            db_media_item.tmdbid = media_item.tmdbid
        if media_item.tmdbcat:
            db_media_item.tmdbcat = media_item.tmdbcat
        db.commit()
        db.refresh(db_media_item)
    return db_media_item

def get_search_cache(db: Session, title: Optional[str] = None):
    query = db.query(models.TorrentCache)
    if title:
        query = query.filter(models.TorrentCache.tortitle.contains(title))
    return query.all()

def get_tor_download(db: Session, download_id: int):
    return db.query(models.TorDownload).filter(models.TorDownload.id == download_id).first()

def create_pt_site(db: Session, pt_site: schemas.PtSiteCreate):
    db_pt_site = models.PtSite(**pt_site.dict())
    db.add(db_pt_site)
    db.commit()
    db.refresh(db_pt_site)
    return db_pt_site

def get_pt_site(db: Session, pt_site_id: int):
    return db.query(models.PtSite).filter(models.PtSite.id == pt_site_id).first()

def get_pt_site_by_name(db: Session, site_name: str):
    return db.query(models.PtSite).filter(models.PtSite.site == site_name).first()

def get_pt_sites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PtSite).offset(skip).limit(limit).all()

def update_pt_site(db: Session, pt_site_id: int, pt_site: schemas.PtSiteUpdate):
    db_pt_site = db.query(models.PtSite).filter(models.PtSite.id == pt_site_id).first()
    if db_pt_site:
        update_data = pt_site.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pt_site, key, value)
        db.commit()
        db.refresh(db_pt_site)
    return db_pt_site

def delete_pt_site(db: Session, pt_site_id: int):
    db_pt_site = db.query(models.PtSite).filter(models.PtSite.id == pt_site_id).first()
    if db_pt_site:
        db.delete(db_pt_site)
        db.commit()
    return db_pt_site