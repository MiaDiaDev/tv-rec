"""EPG service using filtered JSON data for German live TV schedules."""

import json
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
from app.config import config
from app.models.schemas import TVProgram
from app.services.cache import cached
from app.utils.content_detector import detect_content_type
from app.utils.genre_mapper import normalize_genres


class EPGService:
    """Service for fetching and parsing filtered EPG data."""

    def __init__(self):
        """Initialize EPG service."""
        self.xmltv_url = config.XMLTV_EPG_URL
        self.epg_data_path = Path(__file__).parent.parent / 'data' / 'epg_filtered.json'
        self.max_age_hours = 6  # Refresh if older than 6 hours

    def _is_epg_data_fresh(self) -> bool:
        """
        Check if filtered EPG data exists and is fresh.

        Returns:
            True if data is fresh, False otherwise
        """
        if not self.epg_data_path.exists():
            return False

        try:
            with open(self.epg_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            generated_at_str = data.get('generated_at')
            if not generated_at_str:
                return False

            generated_at = datetime.fromisoformat(generated_at_str)

            # Use timezone-aware now for comparison
            from datetime import timezone
            if generated_at.tzinfo is None:
                # If stored time is naive, assume local
                now = datetime.now()
            else:
                # If stored time is aware, use UTC now
                now = datetime.now(tz=timezone.utc)

            age = now - generated_at
            max_age = timedelta(hours=self.max_age_hours)

            return age < max_age

        except Exception as e:
            print(f"Error checking EPG data freshness: {e}")
            return False

    def _ensure_fresh_epg_data(self) -> bool:
        """
        Ensure EPG data is fresh, download and filter if needed.

        Returns:
            True if fresh data is available, False on error
        """
        if self._is_epg_data_fresh():
            return True

        print("EPG data is stale or missing, updating...")

        try:
            from app.utils.epg_filter import download_and_filter_epg

            stats = download_and_filter_epg(
                xmltv_url=self.xmltv_url,
                output_path=str(self.epg_data_path),
                days_ahead=1
            )

            if 'error' in stats:
                print(f"Error updating EPG: {stats['error']}")
                return False

            return True

        except Exception as e:
            print(f"Error updating EPG data: {e}")
            return False

    def _load_epg_data(self) -> Optional[dict]:
        """
        Load filtered EPG data from JSON file.

        Returns:
            EPG data dictionary or None on error
        """
        if not self.epg_data_path.exists():
            return None

        try:
            with open(self.epg_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading EPG data: {e}")
            return None

    def _parse_program(self, program_data: dict) -> Optional[TVProgram]:
        """
        Parse program data from JSON into TVProgram object.

        Args:
            program_data: Program dictionary from JSON

        Returns:
            TVProgram object or None on error
        """
        try:
            title = program_data.get('title', '')
            channel = program_data.get('channel', '')
            description = program_data.get('description')
            duration = program_data.get('duration', 0)
            genres_raw = program_data.get('genres', [])

            # Parse times
            start_time_str = program_data.get('start_time')
            end_time_str = program_data.get('end_time')

            if not start_time_str or not end_time_str:
                return None

            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)

            # Normalize genres
            normalized_genres = normalize_genres(genres_raw)

            # Detect content type
            content_type = detect_content_type(
                title=title,
                duration=duration,
                genres=normalized_genres
            )

            program = TVProgram(
                title=title,
                channel=channel,
                description=description,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                genres=normalized_genres,
                content_type=content_type,
                source="epg"
            )

            return program

        except Exception as e:
            print(f"Error parsing program: {e}")
            return None

    def get_programs_today(
        self,
        channels: Optional[List[str]] = None
    ) -> List[TVProgram]:
        """
        Get today's TV programs.

        Args:
            channels: Filter by channel names (optional)

        Returns:
            List of TVProgram objects for today
        """
        # Ensure we have fresh data
        if not self._ensure_fresh_epg_data():
            print("Warning: Could not get fresh EPG data, using cached if available")

        # Load data
        epg_data = self._load_epg_data()
        if not epg_data:
            print("No EPG data available")
            return []

        programs_data = epg_data.get('programs', [])

        # Filter for today (use CET for German TV)
        from datetime import timezone
        cet = timezone(timedelta(hours=1))
        today = datetime.now(tz=cet).date()
        programs = []

        for program_data in programs_data:
            # Parse program
            program = self._parse_program(program_data)
            if not program:
                continue

            # Check if today
            if program.start_time.date() != today:
                continue

            # Filter by channels if specified
            if channels:
                channel_set = set(c.lower() for c in channels)
                if not any(ch in program.channel.lower() for ch in channel_set):
                    continue

            programs.append(program)

        print(f"Loaded {len(programs)} programs for today")
        return programs

    def get_programs_now(
        self,
        channels: Optional[List[str]] = None
    ) -> List[TVProgram]:
        """
        Get currently airing programs.

        Args:
            channels: Filter by channel names (optional)

        Returns:
            List of currently airing TVProgram objects
        """
        from datetime import timezone
        now = datetime.now(tz=timezone.utc)
        all_programs = self.get_programs_today(channels)

        # Filter for programs airing now
        current_programs = [
            p for p in all_programs
            if p.start_time <= now <= p.end_time
        ]

        return current_programs

    def get_programs_tonight(
        self,
        channels: Optional[List[str]] = None
    ) -> List[TVProgram]:
        """
        Get tonight's programs (after 18:00).

        Args:
            channels: Filter by channel names (optional)

        Returns:
            List of TVProgram objects for tonight
        """
        from datetime import timezone
        cet = timezone(timedelta(hours=1))  # CET baseline
        today = datetime.now(tz=cet).date()
        tonight_start = datetime.combine(today, datetime.min.time(), tzinfo=cet) + timedelta(hours=18)

        all_programs = self.get_programs_today(channels)

        # Filter for programs starting after 18:00
        tonight_programs = [
            p for p in all_programs
            if p.start_time >= tonight_start
        ]

        print(f"Found {len(tonight_programs)} programs for tonight")
        return tonight_programs


# Global instance
epg_service = EPGService()
