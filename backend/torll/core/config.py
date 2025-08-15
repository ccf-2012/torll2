import os
import configparser
from pydantic_settings import BaseSettings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'backend', 'config.ini')

def get_config_from_ini():
    if not os.path.exists(CONFIG_FILE):
        return {}
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config_dict = {}
    if 'tmdb' in config and 'tmdb_api_key' in config['tmdb']:
        config_dict['TMDB_API_KEY'] = config['tmdb']['tmdb_api_key']
    # We intentionally do not read DATABASE_URL from the ini file
    # to ensure the absolute path is used.
    return config_dict

class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'torll.db')}"
    TMDB_API_KEY: str = "YOUR_TMDB_API_KEY"

# Initialize settings by first getting values from the INI file
settings = Settings(**get_config_from_ini())