from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from torll.db.database import get_db
from torll.schemas import schemas, rss_schemas
from torll.services import crud, rss_service, download_service, pt_search_service

router = APIRouter()

@router.get("/rss/status")
async def get_rss_status():
    return {"status": "RSS module is active"}

@router.post("/rss/process/{feed_name}")
async def process_rss_feed(feed_name: str, db: Session = Depends(get_db)):
    db_rss_feed_config = crud.get_rss_feed_config_by_name(db, name=feed_name)
    if db_rss_feed_config is None:
        raise HTTPException(status_code=404, detail="RSS Feed config not found")

    # Convert db_rss_feed_config to RssFeedConfigBase for rss_service.RssFeed
    # This might require some adjustments in rss_service.RssFeed if it expects a Pydantic model
    # or a dictionary with specific keys.
    rss_processor = rss_service.RssFeed(rss_schemas.RssFeedConfigBase.from_orm(db_rss_feed_config))
    rss_processor.process_rss_feeds(db)
    return {"message": f"RSS feed {feed_name} processed successfully."}

@router.get("/rss/history/{rss_name}", response_model=List[rss_schemas.RSSHistory])
def read_rss_history_by_name(rss_name: str, db: Session = Depends(get_db)):
    return crud.get_rss_history_by_name(db, rss_name=rss_name)

# Endpoints for managing RssFeedConfig
@router.post("/rss/configs/", response_model=rss_schemas.RssFeedConfig, status_code=status.HTTP_201_CREATED)
def create_rss_feed_config(rss_feed_config: rss_schemas.RssFeedConfigCreate, db: Session = Depends(get_db)):
    db_rss_feed_config = crud.get_rss_feed_config_by_name(db, name=rss_feed_config.name)
    if db_rss_feed_config:
        raise HTTPException(status_code=400, detail="RSS Feed config with this name already exists")
    return crud.create_rss_feed_config(db=db, rss_feed_config=rss_feed_config)

@router.get("/rss/configs/", response_model=List[rss_schemas.RssFeedConfig])
def read_rss_feed_configs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rss_feed_configs = crud.get_rss_feed_configs(db, skip=skip, limit=limit)
    return rss_feed_configs

@router.get("/rss/configs/{config_id}", response_model=rss_schemas.RssFeedConfig)
def read_rss_feed_config(config_id: int, db: Session = Depends(get_db)):
    db_rss_feed_config = crud.get_rss_feed_config(db, config_id=config_id)
    if db_rss_feed_config is None:
        raise HTTPException(status_code=404, detail="RSS Feed config not found")
    return db_rss_feed_config

@router.put("/rss/configs/{config_id}", response_model=rss_schemas.RssFeedConfig)
def update_rss_feed_config(config_id: int, rss_feed_config: rss_schemas.RssFeedConfigCreate, db: Session = Depends(get_db)):
    db_rss_feed_config = crud.update_rss_feed_config(db, config_id=config_id, rss_feed_config=rss_feed_config)
    if db_rss_feed_config is None:
        raise HTTPException(status_code=404, detail="RSS Feed config not found")
    return db_rss_feed_config

@router.delete("/rss/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rss_feed_config(config_id: int, db: Session = Depends(get_db)):
    db_rss_feed_config = crud.delete_rss_feed_config(db, config_id=config_id)
    if db_rss_feed_config is None:
        raise HTTPException(status_code=404, detail="RSS Feed config not found")
    return {"message": "RSS Feed config deleted successfully"}

@router.post("/pt_configs/", response_model=schemas.PtSite, status_code=status.HTTP_201_CREATED)
def create_pt_site(pt_site: schemas.PtSiteCreate, db: Session = Depends(get_db)):
    db_pt_site = crud.get_pt_site_by_name(db, site_name=pt_site.site)
    if db_pt_site:
        raise HTTPException(status_code=400, detail="PT Site with this name already exists")
    return crud.create_pt_site(db=db, pt_site=pt_site)

@router.get("/pt_configs/", response_model=List[schemas.PtSite])
def read_pt_sites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pt_sites(db, skip=skip, limit=limit)

@router.get("/pt_configs/{config_id}", response_model=schemas.PtSite)
def read_pt_site(config_id: int, db: Session = Depends(get_db)):
    db_pt_site = crud.get_pt_site(db, pt_site_id=config_id)
    if db_pt_site is None:
        raise HTTPException(status_code=404, detail="PT Site not found")
    return db_pt_site

@router.put("/pt_configs/{config_id}", response_model=schemas.PtSite)
def update_pt_site(config_id: int, pt_site: schemas.PtSiteUpdate, db: Session = Depends(get_db)):
    db_pt_site = crud.update_pt_site(db, pt_site_id=config_id, pt_site=pt_site)
    if db_pt_site is None:
        raise HTTPException(status_code=404, detail="PT Site not found")
    return db_pt_site

@router.delete("/pt_configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pt_site(config_id: int, db: Session = Depends(get_db)):
    db_pt_site = crud.delete_pt_site(db, pt_site_id=config_id)
    if db_pt_site is None:
        raise HTTPException(status_code=404, detail="PT Site not found")
    return {"message": "PT Site deleted successfully"}

@router.get("/site_torrents/", response_model=List[schemas.SiteTorrent])
def read_site_torrents(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    title: Optional[str] = None, # New parameter for filtering
    db: Session = Depends(get_db)
):
    return crud.get_site_torrents(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order, title=title)

@router.get("/downloads/", response_model=List[schemas.TorDownload])
def read_downloads(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    name: Optional[str] = None, # New parameter for filtering
    db: Session = Depends(get_db)
):
    return crud.get_downloads(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order, name=name)

@router.post("/downloads/add")
def add_download(download_request: schemas.DownloadRequest, db: Session = Depends(get_db)):
    return download_service.add_to_downloader(db, download_request)

@router.post("/downloads/{download_id}/redownload")
def redownload_torrent(download_id: int, db: Session = Depends(get_db)):
    return download_service.redownload_torrent(db, download_id)

@router.post("/downloads/{download_id}/stop")
def stop_torrent(download_id: int, db: Session = Depends(get_db)):
    return download_service.stop_torrent(db, download_id)

@router.delete("/downloads/{download_id}")
def delete_torrent(download_id: int, db: Session = Depends(get_db)):
    return download_service.delete_torrent(db, download_id)

@router.get("/media_items/", response_model=List[schemas.TorMediaItem])
def read_media_items(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    title: Optional[str] = None, # New parameter for filtering
    db: Session = Depends(get_db)
):
    return crud.get_media_items(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order, title=title)

@router.put("/media_items/{media_item_id}", response_model=schemas.TorMediaItem)
def update_media_item(media_item_id: int, media_item: schemas.TorMediaItemUpdate, db: Session = Depends(get_db)):
    return crud.update_media_item(db, media_item_id, media_item)

@router.get("/search/cache", response_model=List[schemas.TorrentCache])
def read_search_cache(
    title: Optional[str] = None, # New parameter for filtering
    db: Session = Depends(get_db)
):
    return crud.get_search_cache(db, title=title)

@router.post("/search/pt")
def search_pt(search_request: schemas.PTSearchRequest, db: Session = Depends(get_db)):
    return pt_search_service.search_pt_site(db, search_request.search_term, search_request.site_name)

@router.post("/tor_details/", response_model=schemas.TorDetail)
def create_tor_detail(tor_detail: schemas.TorDetailCreate, db: Session = Depends(get_db)):
    return crud.create_tor_detail(db=db, tor_detail=tor_detail)

@router.get("/tor_details/{tor_detail_id}", response_model=schemas.TorDetail)
def read_tor_detail(tor_detail_id: int, db: Session = Depends(get_db)):
    db_tor_detail = crud.get_tor_detail(db, tor_detail_id=tor_detail_id)
    if db_tor_detail is None:
        raise HTTPException(status_code=404, detail="TorDetail not found")
    return db_tor_detail

@router.get("/tor_media_items/{tor_media_item_id}", response_model=schemas.TorMediaItem)
def read_tor_media_item(tor_media_item_id: int, db: Session = Depends(get_db)):
    db_tor_media_item = crud.get_tor_media_item(db, tor_media_item_id=tor_media_item_id)
    if db_tor_media_item is None:
        raise HTTPException(status_code=404, detail="TorMediaItem not found")
    return db_tor_media_item
