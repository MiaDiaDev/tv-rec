"""Tests for EPG service."""

import pytest
from datetime import datetime
from app.services.epg import EPGService


def test_epg_service_init():
    """Test EPGService initialization."""
    service = EPGService()
    assert service.xmltv_url is not None


def test_parse_xmltv_time():
    """Test XMLTV time parsing."""
    service = EPGService()
    time_str = "20241018200000 +0200"
    result = service.parse_xmltv_time(time_str)
    assert result is not None
    assert isinstance(result, datetime)


def test_parse_epg():
    """Test EPG parsing."""
    service = EPGService()
    # Add test implementation with sample XML
    pass


def test_get_programs_today():
    """Test getting today's programs."""
    service = EPGService()
    # Add test implementation
    pass
