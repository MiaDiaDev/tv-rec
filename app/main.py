"""FastAPI main application for German TV Recommender."""

from fastapi import FastAPI, HTTPException
from typing import List, Optional
from app.models.schemas import UserPreferences, Recommendation
from app.services.recommender import recommender_service
from app.config import config

app = FastAPI(
    title="German TV Recommender API",
    description="API for recommending German TV content based on user preferences",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "German TV Recommender API",
        "version": "1.0.0",
        "endpoints": {
            "/recommendations": "Get TV recommendations",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/recommendations", response_model=List[Recommendation])
async def get_recommendations(
    preferences: UserPreferences,
    include_live: bool = True,
    include_mediathek: bool = True,
    limit: int = 20
):
    """
    Get TV recommendations based on user preferences.

    Args:
        preferences: User preferences (mood, genres, content_type)
        include_live: Include live TV programs
        include_mediathek: Include on-demand content
        limit: Maximum number of recommendations

    Returns:
        List of recommendations
    """
    try:
        recommendations = recommender_service.get_recommendations(
            preferences=preferences,
            include_live=include_live,
            include_mediathek=include_mediathek,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@app.get("/genres")
async def get_available_genres():
    """Get list of available genres."""
    from app.utils.genre_mapper import STANDARD_GENRES
    return {"genres": sorted(list(STANDARD_GENRES))}


@app.get("/moods")
async def get_available_moods():
    """Get list of available moods."""
    from app.utils.genre_mapper import MOOD_TO_GENRES
    return {"moods": list(MOOD_TO_GENRES.keys())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
