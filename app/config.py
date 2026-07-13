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
    _DEFAULT_EPG_URL = "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz"
    # TVprofil URL is dead (404) since 2026; override stale .env files
    _DEAD_EPG_URLS = {"https://tvprofil.net/xmltv/epg_tvprofil.net.xml"}

    XMLTV_EPG_URL = os.getenv("XMLTV_EPG_URL", _DEFAULT_EPG_URL)
    if XMLTV_EPG_URL in _DEAD_EPG_URLS:
        print(
            f"Hinweis: XMLTV_EPG_URL in .env zeigt auf eine tote Quelle "
            f"({XMLTV_EPG_URL}), verwende stattdessen {_DEFAULT_EPG_URL}"
        )
        XMLTV_EPG_URL = _DEFAULT_EPG_URL

    # Cache TTLs (seconds)
    EPG_CACHE_TTL = int(os.getenv("EPG_CACHE_TTL", "3600"))
    MEDIATHEK_CACHE_TTL = int(os.getenv("MEDIATHEK_CACHE_TTL", "7200"))

    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))


config = Config()
