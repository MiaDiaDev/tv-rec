"""Tests for EPG service."""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.epg import EPGService
from app.utils.epg_filter import parse_xmltv_time, normalize_channel_name


def test_epg_service_init():
    """Test EPGService initialization."""
    service = EPGService()
    assert service.xmltv_url is not None


def test_parse_xmltv_time():
    """Test XMLTV time parsing with timezone offset."""
    time_str = "20241018200000 +0200"
    result = parse_xmltv_time(time_str)
    assert result is not None
    assert isinstance(result, datetime)
    assert result.tzinfo is not None
    # Should be 20:00 in +0200 timezone
    assert result.hour == 20
    assert result.minute == 0


def test_parse_xmltv_time_cest():
    """Test XMLTV time parsing with CEST offset."""
    time_str = "20260610210000 +0200"  # June = CEST
    result = parse_xmltv_time(time_str)
    assert result is not None
    # Verify offset is +02:00
    assert result.utcoffset() == timedelta(hours=2)


def test_parse_xmltv_time_cet():
    """Test XMLTV time parsing with CET offset."""
    time_str = "20241218200000 +0100"  # December = CET
    result = parse_xmltv_time(time_str)
    assert result is not None
    # Verify offset is +01:00
    assert result.utcoffset() == timedelta(hours=1)


def test_parse_xmltv_time_no_offset():
    """Test XMLTV time parsing without offset (assumes CET)."""
    time_str = "20241018200000"
    result = parse_xmltv_time(time_str)
    assert result is not None
    # Should default to CET (+0100)
    assert result.utcoffset() == timedelta(hours=1)


def test_normalize_channel_name():
    """Test channel name normalization."""
    assert normalize_channel_name("Das Erste") == "Das Erste"
    assert normalize_channel_name("ard.de") == "Das Erste"
    assert normalize_channel_name("ZDF HD") == "ZDF"
    assert normalize_channel_name("RTL Television") == "RTL"
    assert normalize_channel_name("Pro7") == "ProSieben"
    assert normalize_channel_name("SAT.1") == "Sat.1"
    assert normalize_channel_name("kabel eins") == "Kabel Eins"
    assert normalize_channel_name("3sat") == "3sat"
    assert normalize_channel_name("ARTE") == "arte"
    assert normalize_channel_name("unknown_channel") is None


def test_normalize_channel_case_insensitive():
    """Test that channel normalization is case insensitive."""
    assert normalize_channel_name("das erste") == "Das Erste"
    assert normalize_channel_name("DAS ERSTE") == "Das Erste"
    assert normalize_channel_name("zdf") == "ZDF"
