"""MediathekViewWeb API client for German TV on-demand content."""

import requests
from typing import List, Optional
from app.config import config
from app.models.schemas import MediathekContent
from app.services.cache import cached
from app.utils.content_detector import detect_content_type
from app.utils.genre_mapper import normalize_genres


class MediathekService:
    """Service for fetching on-demand content from MediathekViewWeb."""

    def __init__(self):
        """Initialize Mediathek service."""
        self.api_url = config.MEDIATHEK_API_URL

    @cached(ttl=config.MEDIATHEK_CACHE_TTL)
    def search(
        self,
        query: str = "",
        channels: Optional[List[str]] = None,
        duration_min: int = 0,
        duration_max: int = 99999,
        size: int = 50
    ) -> List[dict]:
        """
        Search Mediathek content.

        Args:
            query: Search term
            channels: List of channels to filter by
            duration_min: Minimum duration in seconds
            duration_max: Maximum duration in seconds
            size: Number of results to return

        Returns:
            List of raw API results
        """
        queries = []

        # Add query if provided
        if query:
            queries.append({"fields": ["title", "topic"], "query": query})

        # Add channel filter if provided
        if channels:
            for channel in channels:
                queries.append({"fields": ["channel"], "query": channel})

        # If no queries, search everything
        if not queries:
            queries = [{"fields": ["title"], "query": ""}]

        payload = {
            "queries": queries,
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": False,
            "offset": 0,
            "size": size,
            "duration_min": duration_min,
            "duration_max": duration_max
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("result", {}).get("results", [])
        except requests.RequestException as e:
            print(f"Mediathek API error: {e}")
            return []

    def search_by_genres(
        self,
        genres: List[str],
        size: int = 50
    ) -> List[MediathekContent]:
        """
        Search content by genres.

        Args:
            genres: List of genre names
            size: Number of results

        Returns:
            List of MediathekContent objects
        """
        # Search with genre terms
        results = []
        for genre in genres[:3]:  # Limit to first 3 genres
            raw_results = self.search(query=genre, size=size // len(genres[:3]))
            results.extend(raw_results)

        return self._parse_results(results)

    def get_popular(self, size: int = 50) -> List[MediathekContent]:
        """
        Get popular/recent content.

        Args:
            size: Number of results

        Returns:
            List of MediathekContent objects
        """
        # Get recent content from major channels
        channels = ["ARD", "ZDF", "arte", "3sat"]
        raw_results = self.search(channels=channels, size=size)
        return self._parse_results(raw_results)

    def _parse_results(self, raw_results: List[dict]) -> List[MediathekContent]:
        """
        Parse raw API results into MediathekContent objects.

        Args:
            raw_results: Raw results from API

        Returns:
            List of MediathekContent objects
        """
        parsed = []

        for item in raw_results:
            try:
                title = item.get("title", "")
                topic = item.get("topic", "")
                channel = item.get("channel", "")
                description = item.get("description", "")
                duration = item.get("duration", 0)
                timestamp = item.get("timestamp", 0)

                # Detect content type
                content_type = detect_content_type(
                    title=title,
                    duration=duration,
                    genres=[],
                    topic=topic
                )

                content = MediathekContent(
                    title=title,
                    channel=channel,
                    topic=topic,
                    description=description,
                    timestamp=timestamp,
                    duration=duration,
                    url_video=item.get("url_video"),
                    url_video_hd=item.get("url_video_hd"),
                    url_website=item.get("url_website"),
                    genres=[],  # Mediathek API doesn't provide genres
                    content_type=content_type,
                    source="mediathek"
                )
                parsed.append(content)
            except Exception as e:
                print(f"Error parsing Mediathek result: {e}")
                continue

        return parsed


# Global instance
mediathek_service = MediathekService()
