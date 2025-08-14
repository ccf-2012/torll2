from sqlalchemy.orm import Session
from torll.models import models
from torll.schemas import schemas
from loguru import logger
from datetime import datetime

def search_pt_site(db: Session, search_term: str, site_name: str):
    """
    Simulates searching a PT site and saves dummy results to TorrentCache.
    In a real implementation, this would involve web scraping and parsing.
    """
    logger.info(f"Simulating search for '{search_term}' on site '{site_name}'")

    # Simulate some search results
    dummy_results = [
        {
            "site": site_name,
            "searchword": search_term,
            "tortitle": f"Dummy Torrent 1 for {search_term} on {site_name}",
            "infolink": "http://example.com/dummy1",
            "downlink": "http://example.com/dummy1.torrent",
            "torsizestr": "1.5 GB",
            "torsizeint": 1610612736,
            "seednum": 10,
            "downnum": 5,
            "tordate": datetime.now(),
        },
        {
            "site": site_name,
            "searchword": search_term,
            "tortitle": f"Dummy Torrent 2 for {search_term} on {site_name}",
            "infolink": "http://example.com/dummy2",
            "downlink": "http://example.com/dummy2.torrent",
            "torsizestr": "700 MB",
            "torsizeint": 734003200,
            "seednum": 20,
            "downnum": 10,
            "tordate": datetime.now(),
        },
    ]

    for result_data in dummy_results:
        db_torrent_cache = models.TorrentCache(**result_data)
        db.add(db_torrent_cache)
    db.commit()
    logger.info(f"Saved {len(dummy_results)} dummy search results to cache.")
    return dummy_results
