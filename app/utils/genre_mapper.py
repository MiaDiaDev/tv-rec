"""Genre normalization and mood mapping for German TV content."""

from typing import List, Set


# Standard genre categories
STANDARD_GENRES = {
    'Krimi',
    'Thriller',
    'Komödie',
    'Drama',
    'Dokumentation',
    'Nachrichten',
    'Sport',
    'Unterhaltung',
    'Kinder',
    'Spielfilm',
    'Action',
    'Abenteuer',
    'Science-Fiction',
    'Fantasy',
    'Horror',
    'Romantik',
    'Melodram',
    'Western',
    'Musik',
    'Reportage',
    'Magazin',
    'Show',
    'Serie',
}


# Genre mapping from various sources to standard genres
GENRE_MAPPING = {
    # Krimi variations
    'Krimi': 'Krimi',
    'Kriminalfilm': 'Krimi',
    'Krimi-Serie': 'Krimi',
    'Krimiserie': 'Krimi',
    'Polizeiruf': 'Krimi',
    'Tatort': 'Krimi',

    # Thriller variations
    'Thriller': 'Thriller',
    'Actionthriller': 'Thriller',
    'Psychothriller': 'Thriller',
    'Politthriller': 'Thriller',

    # Comedy variations
    'Komödie': 'Komödie',
    'Komödie/Humor': 'Komödie',
    'Tragikomödie': 'Komödie',
    'Satire': 'Komödie',
    'Comedy': 'Komödie',

    # Drama variations
    'Drama': 'Drama',
    'Familiendrama': 'Drama',
    'Sozialdrama': 'Drama',
    'Historiendrama': 'Drama',

    # Documentary variations
    'Dokumentation': 'Dokumentation',
    'Doku': 'Dokumentation',
    'Dokumentarfilm': 'Dokumentation',
    'Dokureihe': 'Dokumentation',

    # News variations
    'Nachrichten': 'Nachrichten',
    'News': 'Nachrichten',
    'Tagesschau': 'Nachrichten',
    'Heute': 'Nachrichten',

    # Entertainment variations
    'Unterhaltung': 'Unterhaltung',
    'Entertainment': 'Unterhaltung',
    'Show': 'Show',
    'Talkshow': 'Show',
    'Quizshow': 'Show',
    'Gameshow': 'Show',

    # Film-specific
    'Spielfilm': 'Spielfilm',
    'Fernsehfilm': 'Spielfilm',
    'Kinofilm': 'Spielfilm',
    'Film': 'Spielfilm',

    # Other
    'Action': 'Action',
    'Actionfilm': 'Action',
    'Abenteuer': 'Abenteuer',
    'Science-Fiction': 'Science-Fiction',
    'Sci-Fi': 'Science-Fiction',
    'Fantasy': 'Fantasy',
    'Horror': 'Horror',
    'Horrorfilm': 'Horror',
    'Romantik': 'Romantik',
    'Liebesfilm': 'Romantik',
    'Melodram': 'Melodram',
    'Western': 'Western',
    'Musik': 'Musik',
    'Musikfilm': 'Musik',
    'Reportage': 'Reportage',
    'Magazin': 'Magazin',
    'Serie': 'Serie',
    'Kinder': 'Kinder',
    'Kinderfilm': 'Kinder',
    'Sport': 'Sport',
}


# Mood to genre mapping
MOOD_TO_GENRES = {
    'entspannt': ['Komödie', 'Dokumentation', 'Unterhaltung', 'Show', 'Magazin'],
    'spannend': ['Krimi', 'Thriller', 'Action', 'Abenteuer'],
    'lustig': ['Komödie', 'Show', 'Unterhaltung'],
    'informativ': ['Dokumentation', 'Nachrichten', 'Reportage', 'Magazin'],
    'emotional': ['Drama', 'Melodram', 'Romantik'],
    'abenteuerlich': ['Action', 'Abenteuer', 'Thriller', 'Science-Fiction'],
}


def normalize_genre(genre: str) -> str:
    """
    Normalize genre name to standard format.

    Args:
        genre: Raw genre name from API

    Returns:
        Normalized genre name
    """
    if not genre:
        return 'Unterhaltung'

    # Try exact match first
    if genre in STANDARD_GENRES:
        return genre

    # Try mapping
    return GENRE_MAPPING.get(genre, genre)


def normalize_genres(genres: List[str]) -> List[str]:
    """
    Normalize a list of genres.

    Args:
        genres: List of raw genre names

    Returns:
        List of normalized genre names (unique)
    """
    normalized = {normalize_genre(g) for g in genres if g}
    return sorted(list(normalized))


def get_genres_for_mood(mood: str) -> List[str]:
    """
    Get appropriate genres for a given mood.

    Args:
        mood: User's mood (entspannt, spannend, lustig, etc.)

    Returns:
        List of matching genres
    """
    mood_lower = mood.lower()
    return MOOD_TO_GENRES.get(mood_lower, [])


def match_genres(program_genres: List[str], target_genres: List[str]) -> bool:
    """
    Check if program genres match any of the target genres.

    Args:
        program_genres: Genres of the program
        target_genres: Genres to match against

    Returns:
        True if any genre matches
    """
    if not target_genres:
        return True  # No filter, match everything

    program_set = {normalize_genre(g) for g in program_genres}
    target_set = {normalize_genre(g) for g in target_genres}

    return bool(program_set & target_set)
