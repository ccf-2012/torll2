from sqlalchemy.orm import Session
from torll.models import models
from torll.schemas import schemas
from torll.services import crud
from fastapi import HTTPException
from loguru import logger
from qbittorrent import Client

def get_qb_client(qbit_config: models.QbitConfig):
    """Helper function to get a qBittorrent client instance."""
    try:
        qb = Client(
            host=f"http://{qbit_config.host}:{qbit_config.port}",
            username=qbit_config.username,
            password=qbit_config.password
        )
        qb.auth_log_in()
        return qb
    except Exception as e:
        logger.error(f"Failed to connect to qBittorrent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to qBittorrent: {e}")

def add_to_downloader(db: Session, download_request: schemas.DownloadRequest):
    qbit_config = crud.get_qbit_config_by_name(db, name=download_request.qbit_config_name)
    if not qbit_config:
        raise HTTPException(status_code=404, detail="qBittorrent config not found")

    qb = get_qb_client(qbit_config)
    try:
        qb.download_from_link(download_request.download_link)
        return {"message": "Torrent added to downloader successfully."}
    except Exception as e:
        logger.error(f"Failed to add torrent to downloader: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add torrent to downloader: {e}")

def redownload_torrent(db: Session, download_id: int):
    db_download = crud.get_tor_download(db, download_id)
    if not db_download:
        raise HTTPException(status_code=404, detail="Download record not found.")

    qbit_config = crud.get_qbit_config_by_name(db, name=db_download.qbitname)
    if not qbit_config:
        raise HTTPException(status_code=404, detail="qBittorrent config not found for this download.")

    qb = get_qb_client(qbit_config)
    try:
        # Assuming qbid is the torrent hash in qBittorrent
        qb.recheck_torrents(db_download.qbid)
        return {"message": "Torrent re-download initiated successfully."}
    except Exception as e:
        logger.error(f"Failed to re-download torrent {db_download.qbid}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to re-download torrent: {e}")

def stop_torrent(db: Session, download_id: int):
    db_download = crud.get_tor_download(db, download_id)
    if not db_download:
        raise HTTPException(status_code=404, detail="Download record not found.")

    qbit_config = crud.get_qbit_config_by_name(db, name=db_download.qbitname)
    if not qbit_config:
        raise HTTPException(status_code=404, detail="qBittorrent config not found for this download.")

    qb = get_qb_client(qbit_config)
    try:
        qb.pause_torrents(db_download.qbid)
        return {"message": "Torrent stopped successfully."}
    except Exception as e:
        logger.error(f"Failed to stop torrent {db_download.qbid}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop torrent: {e}")

def delete_torrent(db: Session, download_id: int):
    db_download = crud.get_tor_download(db, download_id)
    if not db_download:
        raise HTTPException(status_code=404, detail="Download record not found.")

    qbit_config = crud.get_qbit_config_by_name(db, name=db_download.qbitname)
    if not qbit_config:
        raise HTTPException(status_code=404, detail="qBittorrent config not found for this download.")

    qb = get_qb_client(qbit_config)
    try:
        # Delete torrent from qBittorrent, optionally delete files
        qb.delete_permanently(db_download.qbid) # or qb.delete(db_download.qbid)
        crud.delete_download(db, download_id) # Delete from our DB
        return {"message": "Torrent deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete torrent {db_download.qbid}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete torrent: {e}")