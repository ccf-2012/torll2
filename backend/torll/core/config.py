from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./torll.db"
    TMDB_API_KEY: str = "YOUR_TMDB_API_KEY" # Replace with your actual TMDb API key

    class Config:
        env_file = ".env"

settings = Settings()
