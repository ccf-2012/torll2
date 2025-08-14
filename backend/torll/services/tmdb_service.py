import tmdbsimple as tmdb
from loguru import logger

# Assume API key is configured elsewhere, e.g., in a config file or environment variable
# tmdb.API_KEY = "YOUR_TMDB_API_KEY"

def search_tmdb(query: str, media_type: str = "multi"):
    """
    Searches TMDb for a given query and media type.
    media_type can be "movie", "tv", "person", "collection", "company", "keyword", "multi".
    Returns a list of results.
    """
    try:
        if not tmdb.API_KEY:
            logger.warning("TMDb API key is not set. Skipping TMDb search.")
            return []

        search = tmdb.Search()
        response = search.multi(query=query)
        
        filtered_results = []
        for result in response['results']:
            if media_type == "multi" or result.get('media_type') == media_type:
                filtered_results.append(result)
        return filtered_results
    except Exception as e:
        logger.error(f"Error searching TMDb for '{query}': {e}")
        return []