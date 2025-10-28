"""Recommendation engine for German TV content."""

from datetime import datetime
from typing import List
from app.models.schemas import (
    UserPreferences,
    Recommendation,
    TVProgram,
    MediathekContent
)
from app.services.epg import epg_service
from app.services.mediathek import mediathek_service
from app.utils.genre_mapper import get_genres_for_mood, match_genres


class RecommenderService:
    """Service for generating TV recommendations."""

    def __init__(self):
        """Initialize recommender service."""
        self.epg = epg_service
        self.mediathek = mediathek_service

    def get_recommendations(
        self,
        preferences: UserPreferences,
        include_live: bool = True,
        include_mediathek: bool = True,
        limit: int = 20
    ) -> List[Recommendation]:
        """
        Get TV recommendations based on user preferences.

        Args:
            preferences: User preferences
            include_live: Include live TV programs
            include_mediathek: Include on-demand content
            limit: Maximum number of recommendations

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        # Get genres from mood
        mood_genres = get_genres_for_mood(preferences.mood) if preferences.mood else []

        # Combine with user-selected genres
        target_genres = list(set(mood_genres + preferences.genres))

        # Get live TV recommendations
        if include_live:
            live_programs = self._get_live_recommendations(
                target_genres=target_genres,
                content_type=preferences.content_type
            )
            recommendations.extend(live_programs)

        # Get Mediathek recommendations
        if include_mediathek:
            mediathek_programs = self._get_mediathek_recommendations(
                target_genres=target_genres,
                content_type=preferences.content_type
            )
            recommendations.extend(mediathek_programs)

        # Sort by relevance (live programs first, then by start time)
        recommendations.sort(
            key=lambda x: (
                0 if x.source == "epg" else 1,
                x.start_time if x.start_time else datetime.max
            )
        )

        return recommendations[:limit]

    def _get_live_recommendations(
        self,
        target_genres: List[str],
        content_type: str = None
    ) -> List[Recommendation]:
        """
        Get recommendations from live TV.

        Args:
            target_genres: List of target genres
            content_type: Filter by content type (movie/show)

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        # Get tonight's programs
        programs = self.epg.get_programs_tonight()

        for program in programs:
            # Filter by content type if specified
            if content_type and program.content_type != content_type:
                continue

            # Filter by genres if specified
            if target_genres and not match_genres(program.genres, target_genres):
                continue

            # Convert to Recommendation
            rec = self._program_to_recommendation(program)
            recommendations.append(rec)

        return recommendations

    def _get_mediathek_recommendations(
        self,
        target_genres: List[str],
        content_type: str = None
    ) -> List[Recommendation]:
        """
        Get recommendations from Mediathek.

        Args:
            target_genres: List of target genres
            content_type: Filter by content type (movie/show)

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        # Search by genres or get popular content
        if target_genres:
            content_list = self.mediathek.search_by_genres(target_genres, size=30)
        else:
            content_list = self.mediathek.get_popular(size=30)

        for content in content_list:
            # Filter by content type if specified
            if content_type and content.content_type != content_type:
                continue

            # Convert to Recommendation
            rec = self._mediathek_to_recommendation(content)
            recommendations.append(rec)

        return recommendations

    def _program_to_recommendation(self, program: TVProgram) -> Recommendation:
        """Convert TVProgram to Recommendation."""
        return Recommendation(
            title=program.title,
            channel=program.channel,
            description=program.description,
            start_time=program.start_time,
            duration=program.duration,
            genres=program.genres,
            content_type=program.content_type,
            source=program.source,
            url_video=None,
            url_website=None
        )

    def _mediathek_to_recommendation(
        self,
        content: MediathekContent
    ) -> Recommendation:
        """Convert MediathekContent to Recommendation."""
        return Recommendation(
            title=content.title,
            channel=content.channel,
            description=content.description,
            start_time=None,  # On-demand has no start time
            duration=content.duration,
            genres=content.genres,
            content_type=content.content_type,
            source=content.source,
            url_video=content.url_video or content.url_video_hd,
            url_website=content.url_website
        )


# Global instance
recommender_service = RecommenderService()
