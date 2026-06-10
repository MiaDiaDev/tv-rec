"""Tests for content type detection."""

import pytest
from app.utils.content_detector import detect_content_type, is_movie, is_show


def test_detect_movie_by_duration():
    """Test movie detection based on long duration."""
    result = detect_content_type(
        title="Tatort",
        duration=90 * 60,  # 90 minutes
        genres=["Krimi"]
    )
    assert result == "movie"


def test_detect_show_by_short_duration():
    """Test show detection based on short duration."""
    result = detect_content_type(
        title="Tagesschau",
        duration=15 * 60,  # 15 minutes
        genres=["Nachrichten"]
    )
    assert result == "show"


def test_detect_movie_by_keyword():
    """Test movie detection by keyword in title."""
    result = detect_content_type(
        title="Der Spielfilm des Abends",
        duration=50 * 60,  # 50 minutes (short but has keyword)
        genres=["Drama"]
    )
    assert result == "movie"


def test_detect_show_by_series_keyword():
    """Test show detection by series keyword."""
    result = detect_content_type(
        title="Die Serie - Folge 1",
        duration=90 * 60,  # Long but has series keyword
        genres=["Drama"]
    )
    assert result == "show"


def test_detect_show_by_episode_pattern():
    """Test show detection by episode pattern."""
    result = detect_content_type(
        title="Breaking Bad S01E01",
        duration=45 * 60,
        genres=["Drama"]
    )
    assert result == "show"


def test_detect_movie_typical_case():
    """Test typical movie case: long duration + movie genre."""
    result = detect_content_type(
        title="Ein spannender Krimi",
        duration=120 * 60,  # 2 hours
        genres=["Krimi", "Thriller"]
    )
    assert result == "movie"


def test_detect_show_typical_case():
    """Test typical show case: short duration + topic."""
    result = detect_content_type(
        title="Tatort Hamburg",
        duration=45 * 60,
        genres=["Krimi"],
        topic="Tatort"
    )
    assert result == "show"


def test_is_movie_helper():
    """Test is_movie helper function."""
    assert is_movie("Spielfilm: Der Untergang", 150 * 60, ["Drama"]) is True
    assert is_movie("Serie Folge 1", 30 * 60, ["Drama"]) is False


def test_is_show_helper():
    """Test is_show helper function."""
    assert is_show("Serie Folge 1", 30 * 60, ["Drama"]) is True
    assert is_show("Kinofilm", 120 * 60, ["Action"]) is False


def test_edge_case_70_minutes():
    """Test edge case at exactly 70 minutes threshold."""
    # Exactly 70 minutes with movie genre should be movie
    result = detect_content_type(
        title="Ein Film",
        duration=70 * 60,
        genres=["Drama"]
    )
    assert result == "movie"

    # 69 minutes without strong movie indicators should be show
    result = detect_content_type(
        title="Programm",
        duration=69 * 60,
        genres=["Unterhaltung"]
    )
    assert result == "show"
