"""Tests for configuration handling."""

import importlib
import os


def test_dead_epg_url_is_overridden(monkeypatch):
    """A stale .env pointing at the dead TVprofil URL falls back to the default."""
    monkeypatch.setenv("XMLTV_EPG_URL", "https://tvprofil.net/xmltv/epg_tvprofil.net.xml")
    import app.config
    importlib.reload(app.config)
    assert app.config.config.XMLTV_EPG_URL == "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz"


def test_custom_epg_url_is_respected(monkeypatch):
    """A custom (non-dead) URL from the environment is kept as-is."""
    monkeypatch.setenv("XMLTV_EPG_URL", "https://example.org/my-epg.xml.gz")
    import app.config
    importlib.reload(app.config)
    assert app.config.config.XMLTV_EPG_URL == "https://example.org/my-epg.xml.gz"
    # Restore module state for other tests
    monkeypatch.delenv("XMLTV_EPG_URL")
    importlib.reload(app.config)
