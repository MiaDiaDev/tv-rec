"""Tests for genre normalization and mood mapping."""

import pytest
from app.utils.genre_mapper import (
    normalize_genre,
    normalize_genres,
    get_genres_for_mood,
    match_genres,
    STANDARD_GENRES,
    MOOD_TO_GENRES
)


def test_normalize_genre_standard():
    """Test normalization of standard genre names."""
    assert normalize_genre("Krimi") == "Krimi"
    assert normalize_genre("Drama") == "Drama"
    assert normalize_genre("Komödie") == "Komödie"


def test_normalize_genre_variations():
    """Test normalization of genre variations."""
    assert normalize_genre("Kriminalfilm") == "Krimi"
    assert normalize_genre("Actionthriller") == "Thriller"
    assert normalize_genre("Tragikomödie") == "Komödie"
    assert normalize_genre("Doku") == "Dokumentation"
    assert normalize_genre("Comedy") == "Komödie"


def test_normalize_genre_unknown():
    """Test normalization of unknown genre."""
    # Unknown genres are returned as-is
    result = normalize_genre("UnknownGenre")
    assert result == "UnknownGenre"


def test_normalize_genre_empty():
    """Test normalization of empty genre."""
    assert normalize_genre("") == "Unterhaltung"
    assert normalize_genre(None) == "Unterhaltung"


def test_normalize_genres_list():
    """Test normalization of genre list."""
    input_genres = ["Kriminalfilm", "Actionthriller", "Drama"]
    result = normalize_genres(input_genres)
    assert "Krimi" in result
    assert "Thriller" in result
    assert "Drama" in result
    assert len(result) == 3


def test_normalize_genres_removes_duplicates():
    """Test that normalization removes duplicates."""
    input_genres = ["Krimi", "Kriminalfilm", "Krimi-Serie"]
    result = normalize_genres(input_genres)
    # All should normalize to "Krimi"
    assert result == ["Krimi"]


def test_normalize_genres_sorted():
    """Test that normalized genres are sorted."""
    input_genres = ["Thriller", "Action", "Krimi"]
    result = normalize_genres(input_genres)
    assert result == sorted(result)


def test_get_genres_for_mood_entspannt():
    """Test mood mapping for 'entspannt'."""
    genres = get_genres_for_mood("entspannt")
    assert "Komödie" in genres
    assert "Dokumentation" in genres
    assert "Unterhaltung" in genres


def test_get_genres_for_mood_spannend():
    """Test mood mapping for 'spannend'."""
    genres = get_genres_for_mood("spannend")
    assert "Krimi" in genres
    assert "Thriller" in genres
    assert "Action" in genres


def test_get_genres_for_mood_lustig():
    """Test mood mapping for 'lustig'."""
    genres = get_genres_for_mood("lustig")
    assert "Komödie" in genres
    assert "Show" in genres


def test_get_genres_for_mood_informativ():
    """Test mood mapping for 'informativ'."""
    genres = get_genres_for_mood("informativ")
    assert "Dokumentation" in genres
    assert "Nachrichten" in genres


def test_get_genres_for_mood_case_insensitive():
    """Test that mood mapping is case insensitive."""
    genres_lower = get_genres_for_mood("spannend")
    genres_upper = get_genres_for_mood("SPANNEND")
    assert genres_lower == genres_upper


def test_get_genres_for_mood_unknown():
    """Test mood mapping for unknown mood."""
    genres = get_genres_for_mood("unknown_mood")
    assert genres == []


def test_match_genres_exact_match():
    """Test genre matching with exact match."""
    program_genres = ["Krimi", "Drama"]
    target_genres = ["Krimi"]
    assert match_genres(program_genres, target_genres) is True


def test_match_genres_no_match():
    """Test genre matching with no match."""
    program_genres = ["Komödie", "Show"]
    target_genres = ["Krimi", "Thriller"]
    assert match_genres(program_genres, target_genres) is False


def test_match_genres_normalized():
    """Test genre matching with normalization."""
    program_genres = ["Kriminalfilm"]
    target_genres = ["Krimi"]
    # Should match after normalization
    assert match_genres(program_genres, target_genres) is True


def test_match_genres_empty_target():
    """Test genre matching with empty target (match all)."""
    program_genres = ["Krimi", "Drama"]
    target_genres = []
    assert match_genres(program_genres, target_genres) is True


def test_match_genres_multiple_matches():
    """Test genre matching with multiple matches."""
    program_genres = ["Krimi", "Thriller", "Action"]
    target_genres = ["Thriller", "Drama"]
    assert match_genres(program_genres, target_genres) is True


def test_all_moods_have_genres():
    """Test that all defined moods have non-empty genre lists."""
    for mood, genres in MOOD_TO_GENRES.items():
        assert len(genres) > 0, f"Mood '{mood}' has no genres"
        for genre in genres:
            assert genre in STANDARD_GENRES, f"Genre '{genre}' in mood '{mood}' is not standard"
