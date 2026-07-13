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


def test_normalize_channel_dotted_ids():
    """Test matching of dotted channel IDs (e.g. epgshare01 format)."""
    assert normalize_channel_name("Das.Erste.de") == "Das Erste"
    assert normalize_channel_name("ZDF.de") == "ZDF"
    assert normalize_channel_name("RTL.Television.de") == "RTL"
    assert normalize_channel_name("Kabel.Eins.de") == "Kabel Eins"


def test_normalize_channel_rtl_zwei_not_rtl():
    """Test that RTL ZWEI matches RTL II, not RTL (longest pattern wins)."""
    assert normalize_channel_name("RTL ZWEI") == "RTL II"
    assert normalize_channel_name("RTL2") == "RTL II"
    assert normalize_channel_name("rtl zwei.de") == "RTL II"
    # Plain RTL still maps to RTL
    assert normalize_channel_name("RTL") == "RTL"


def test_download_and_filter_gzip(monkeypatch, tmp_path):
    """End-to-end filter test with a gzipped XMLTV payload and display-name matching."""
    import gzip as gzip_mod
    from datetime import datetime, timezone, timedelta
    from app.utils import epg_filter

    cet = timezone(timedelta(hours=2))
    tonight = datetime.now(tz=cet).replace(hour=20, minute=15, second=0, microsecond=0)
    start = tonight.strftime("%Y%m%d%H%M%S +0200")
    stop = (tonight + timedelta(minutes=90)).strftime("%Y%m%d%H%M%S +0200")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="some.opaque.id.1"><display-name>Das Erste HD</display-name></channel>
  <channel id="some.opaque.id.2"><display-name>Unknown Channel</display-name></channel>
  <programme start="{start}" stop="{stop}" channel="some.opaque.id.1">
    <title>Tatort</title>
    <desc>Testfall</desc>
    <category>Krimi</category>
  </programme>
  <programme start="{start}" stop="{stop}" channel="some.opaque.id.2">
    <title>Should be filtered out</title>
  </programme>
</tv>"""

    payload = gzip_mod.compress(xml.encode("utf-8"))

    class FakeResponse:
        content = payload
        def raise_for_status(self):
            pass

    monkeypatch.setattr(epg_filter.requests, "get", lambda *a, **kw: FakeResponse())

    output = tmp_path / "epg.json"
    stats = epg_filter.download_and_filter_epg("https://example.invalid/epg.xml.gz", str(output))

    assert "error" not in stats
    assert stats["filtered_programs"] == 1
    assert stats["channels_found"] == ["Das Erste"]
