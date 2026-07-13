"""Configuration management for German TV Recommender."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    # API Endpoints
    MEDIATHEK_API_URL = os.getenv(
        "MEDIATHEK_API_URL",
        "https://mediathekviewweb.de/api/query"
    )
    XMLTV_EPG_URL = os.getenv(
        "XMLTV_EPG_URL",
        "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz"
    )

    # Cache TTLs (seconds)
    EPG_CACHE_TTL = int(os.getenv("EPG_CACHE_TTL", "3600"))
    MEDIATHEK_CACHE_TTL = int(os.getenv("MEDIATHEK_CACHE_TTL", "7200"))

    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))


config = Config()
