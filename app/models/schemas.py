"""Pydantic models for German TV Recommender."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """User preferences for TV recommendations."""
    mood: str = Field(..., description="User's mood (entspannt, spannend, lustig, informativ, etc.)")
    genres: List[str] = Field(default_factory=list, description="Selected genres")
    content_type: Optional[str] = Field(None, description="Movie (Film) or TV Show (Serie)")


class TVProgram(BaseModel):
    """TV program from EPG data."""
    title: str
    channel: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration: int  # in seconds
    genres: List[str] = Field(default_factory=list)
    content_type: str = Field(default="show", description="movie or show")
    source: str = Field(default="epg", description="epg or mediathek")


class MediathekContent(BaseModel):
    """On-demand content from Mediathek."""
    title: str
    channel: str
    topic: Optional[str] = None
    description: Optional[str] = None
    timestamp: int  # Unix timestamp
    duration: int  # in seconds
    url_video: Optional[str] = None
    url_video_hd: Optional[str] = None
    url_website: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    content_type: str = Field(default="show", description="movie or show")
    source: str = Field(default="mediathek")


class Recommendation(BaseModel):
    """Unified recommendation model."""
    title: str
    channel: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None  # None for on-demand
    duration: int  # in seconds
    genres: List[str] = Field(default_factory=list)
    content_type: str  # movie or show
    source: str  # epg or mediathek
    url_video: Optional[str] = None
    url_website: Optional[str] = None

    @property
    def duration_minutes(self) -> int:
        """Return duration in minutes."""
        return self.duration // 60

    @property
    def is_live(self) -> bool:
        """Check if this is live TV."""
        return self.source == "epg"

    @property
    def is_on_demand(self) -> bool:
        """Check if this is on-demand content."""
        return self.source == "mediathek"
