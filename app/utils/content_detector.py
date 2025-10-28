"""Content type detection (Movie vs TV Show) for German TV programs."""

import re
from typing import List


# Movie indicators
MOVIE_KEYWORDS = [
    'film',
    'spielfilm',
    'kinofilm',
    'fernsehfilm',
    'TV-Film',
    'TV Film',
]

MOVIE_GENRES = [
    'Spielfilm',
    'Krimi',
    'Thriller',
    'Drama',
    'Komödie',
    'Action',
    'Abenteuer',
    'Science-Fiction',
    'Fantasy',
    'Horror',
    'Romantik',
    'Melodram',
    'Western',
]

# TV Show indicators
SERIES_KEYWORDS = [
    'serie',
    'reihe',
    'folge',
    'staffel',
    'episode',
    'teil',
]

SERIES_PATTERNS = [
    r'\bS\d+E\d+\b',  # S01E01 format
    r'\b\d+x\d+\b',   # 1x01 format
    r'\((\d+)\)',     # (1) episode number
    r'Folge\s+\d+',   # Folge 1
    r'Teil\s+\d+',    # Teil 1
]

# Minimum duration for a movie (in seconds)
MOVIE_MIN_DURATION = 70 * 60  # 70 minutes


def detect_content_type(
    title: str,
    duration: int,
    genres: List[str],
    topic: str = None
) -> str:
    """
    Detect if content is a movie or TV show.

    Args:
        title: Program title
        duration: Duration in seconds
        genres: List of genres
        topic: Topic/series name (optional)

    Returns:
        'movie' or 'show'
    """
    score = 0
    title_lower = title.lower() if title else ''
    topic_lower = topic.lower() if topic else ''

    # Duration check (strong indicator)
    if duration >= MOVIE_MIN_DURATION:
        score += 2
    else:
        score -= 1

    # Movie keywords in title
    for keyword in MOVIE_KEYWORDS:
        if keyword in title_lower:
            score += 3
            break

    # Series keywords in title (negative score)
    for keyword in SERIES_KEYWORDS:
        if keyword in title_lower or keyword in topic_lower:
            score -= 2
            break

    # Check for episode patterns
    for pattern in SERIES_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            score -= 3
            break

    # Genre check
    for genre in genres:
        if genre in MOVIE_GENRES:
            score += 1
            break

    # Final decision
    return 'movie' if score >= 2 else 'show'


def is_movie(
    title: str,
    duration: int,
    genres: List[str],
    topic: str = None
) -> bool:
    """
    Check if content is a movie.

    Args:
        title: Program title
        duration: Duration in seconds
        genres: List of genres
        topic: Topic/series name (optional)

    Returns:
        True if movie, False otherwise
    """
    return detect_content_type(title, duration, genres, topic) == 'movie'


def is_show(
    title: str,
    duration: int,
    genres: List[str],
    topic: str = None
) -> bool:
    """
    Check if content is a TV show.

    Args:
        title: Program title
        duration: Duration in seconds
        genres: List of genres
        topic: Topic/series name (optional)

    Returns:
        True if TV show, False otherwise
    """
    return detect_content_type(title, duration, genres, topic) == 'show'
