# German TV Recommender - Claude.md

## Project Overview

A web application that recommends German TV content based on user preferences. The app targets German users and helps them discover what to watch this evening from both live TV programs and on-demand content from ARD/ZDF Mediatheken.

**Target Audience:** German users  
**Language:** All UI and content in German  
**Scope:** German TV stations only (public and private broadcasters)

## User Features

### Core Features (MVP)
1. **User Input Form:**
   - Daily mood selection (e.g., entspannt, spannend, lustig, informativ)
   - Genre selection (Krimi, Komödie, Drama, Dokumentation, etc.)
   - Content type filter: Movie (Film) vs TV Show (Serie/Sendung)

2. **Recommendations Display:**
   - Show today's TV program alternatives based on user inputs
   - Include both live TV (currently airing / starting soon) and on-demand content
   - Display: channel, title, description, start time (for live), duration, genre tags

3. **Session-based:**
   - No user accounts or persistent storage initially
   - All preferences stored in session only

### Future Enhancements (Phase 2)
- Allow users to mark/discard shows they've already seen
- User profiles with persistent preferences
- Watchlist functionality
- Integration of more Mediathek sources beyond ARD/ZDF

## Technical Stack

### Backend
- **Framework:** FastAPI (Python)
- **Data Fetching:** Real-time when user visits (no background jobs initially)
- **Caching:** Redis for API response caching
- **APIs Used:**
  - MediathekViewWeb API for ARD/ZDF Mediathek on-demand content
  - XMLTV EPG files (epgshare01.online) for live EPG schedules

### Frontend
- **Framework:** Gradio (Python-based UI framework)
- **Reason:** Developer familiarity and rapid prototyping

### Data Storage
- **Session Storage:** In-memory (Gradio session state)
- **Cache:** Redis for API responses (30-60 min TTL for EPG, 1-2 hours for Mediathek)
- **Future:** PostgreSQL for user profiles and viewing history

### Deployment
- Docker container recommended
- Environment variables for configuration
- Redis as separate service

## API Information

### 1. MediathekViewWeb API (On-Demand Content)

**Endpoint:** `https://mediathekviewweb.de/api/query`  
**Method:** POST  
**Authentication:** None required  
**Rate Limits:** No strict limits, reasonable usage expected  
**Coverage:** ARD, ZDF, arte, 3sat, and all regional public broadcasters

**Request Format:**
```python
{
    "queries": [
        {"fields": ["title", "topic"], "query": "search_term"},
        {"fields": ["channel"], "query": "ARD"}
    ],
    "sortBy": "timestamp",
    "sortOrder": "desc",
    "future": False,
    "offset": 0,
    "size": 50,
    "duration_min": 0,
    "duration_max": 99999
}
```

**Response Fields:**
- `title`: Video title
- `topic`: Series/topic name
- `description`: Program description
- `channel`: Broadcasting channel
- `timestamp`: Publication timestamp (Unix)
- `duration`: Duration in seconds
- `url_video`: Standard quality video URL
- `url_video_hd`: HD video URL (if available)
- `url_website`: Link to broadcaster's website

**Caching Strategy:** Cache results for 1-2 hours

### 2. XMLTV EPG (Live EPG Data) - **FILTERED APPROACH**

**Endpoint:** `https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz` (configurable via `XMLTV_EPG_URL`)
**Format:** XMLTV (XML), gzip-compressed (`.xml.gz` handled automatically)
**Authentication:** None required
**Coverage:** German channels (DE1 file), updated daily
**Implementation:** **Filtered to 10 main German channels only**

> **History:** The original source `https://tvprofil.net/xmltv/epg_tvprofil.net.xml`
> started returning 404 in 2026 and was replaced by epgshare01.online.
> The downloader is source-agnostic: any standard XMLTV file (plain or gzip)
> works via the `XMLTV_EPG_URL` environment variable.

**Filtered Channels (10 Main Stations):**
- **Public:** Das Erste (ARD), ZDF, 3sat, arte
- **Private:** RTL, ProSieben, Sat.1, VOX, RTL II, Kabel Eins

**Filtering Strategy:**
1. Download full XMLTV file (once per 6 hours)
2. Filter for 10 main channels only
3. Filter for today + tomorrow only (not full 7-day schedule)
4. Convert to JSON format (~1-3MB instead of 100MB)
5. Store in `app/data/epg_filtered.json`
6. Load from JSON on subsequent requests (fast)

**Key XMLTV Elements:**
```xml
<programme start="20241018200000 +0200" stop="20241018213000 +0200" channel="Das Erste">
    <title>Tatort</title>
    <desc>Ein neuer Fall für das Ermittlerteam...</desc>
    <category>Krimi</category>
</programme>
```

**Parsing Notes:**
- Time format: `YYYYMMDDHHmmss +ZZZZ`
- Timezone: CET (Central European Time)
- Genre in `<category>` tags
- Multiple categories possible per program

**Performance Benefits:**
- First download: ~30-60 seconds (one-time)
- Filtered file size: 1-3MB (vs 100MB)
- Subsequent loads: <1 second (load from JSON)
- Update frequency: Every 6 hours automatically

**Implementation Files:**
- `app/utils/epg_filter.py`: Filtering utility
- `app/services/epg.py`: EPG service using filtered JSON
- `scripts/update_epg.py`: Manual update script

### 3. Terms of Use

**MediathekViewWeb:**
- Free for personal and educational use
- Content is copyrighted by broadcasters
- Respect geo-restrictions (most content Germany/Austria/Switzerland only)

**epgshare01.online:**
- Free EPG for legal/personal use
- No authentication required; be considerate with download frequency
  (app downloads at most once per 6 hours)

## Data Processing Requirements

### Content Type Detection (Movie vs TV Show)

Implement heuristics since EPG data doesn't always explicitly specify:

**Movie Indicators:**
- Duration ≥ 70 minutes (4200 seconds)
- Keywords in title: "Film", "Spielfilm", "Kinofilm", "Fernsehfilm"
- Genres: Drama, Komödie, Thriller, Action, Krimi (as primary genre)

**TV Show Indicators:**
- Duration < 70 minutes
- Keywords: "Serie", "Reihe", "Folge", "Staffel"
- Episode numbering present

**Detection Algorithm:**
```python
def detect_content_type(program):
    score = 0
    if duration >= 4200: score += 2
    if movie_keywords in title: score += 3
    if series_keywords in title: score -= 2
    return 'movie' if score >= 2 else 'show'
```

### Genre Normalization

Different sources use different German genre names. Normalize to standard set:

**Standard Genres:**
- Krimi (Crime)
- Thriller
- Komödie (Comedy)
- Drama
- Dokumentation (Documentary)
- Nachrichten (News)
- Sport
- Unterhaltung (Entertainment)
- Kinder (Children)
- Spielfilm (Feature Film)

**Mapping Example:**
```python
GENRE_MAPPING = {
    'Krimi': 'Krimi',
    'Thriller': 'Thriller', 
    'Komödie': 'Komödie',
    'Kriminalfilm': 'Krimi',
    'Actionthriller': 'Thriller',
    # etc.
}
```

### Mood Mapping to Genres

Map user moods to appropriate genres:

- **Entspannt** (Relaxed) → Komödie, Dokumentation, Unterhaltung
- **Spannend** (Exciting) → Krimi, Thriller, Action
- **Lustig** (Funny) → Komödie, Show, Unterhaltung
- **Informativ** (Informative) → Dokumentation, Nachrichten, Reportage
- **Emotional** → Drama, Melodram
- **Abenteuerlich** (Adventurous) → Action, Abenteuer, Thriller

## File Structure

```
tv-recommender/
├── README.md
├── Claude.md (this file)
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── gradio_ui.py         # Gradio interface
│   ├── config.py            # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── mediathek.py     # MediathekViewWeb API client
│   │   ├── epg.py           # XMLTV EPG parser
│   │   ├── recommender.py   # Recommendation logic
│   │   └── cache.py         # Redis caching utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       ├── __init__.py
│       ├── content_detector.py  # Movie/show detection
│       └── genre_mapper.py      # Genre normalization
└── tests/
    ├── __init__.py
    ├── test_mediathek.py
    ├── test_epg.py
    └── test_recommender.py
```

## Key Implementation Details

### 1. Caching Layer

Use Redis to minimize API calls and improve performance:

```python
import redis
import json
from functools import wraps

cache = redis.Redis(host='redis', port=6379, db=0)

def cached(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            result = func(*args, **kwargs)
            cache.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

**Cache TTLs:**
- EPG data: 30-60 minutes
- Mediathek search results: 1-2 hours
- Genre/channel lists: 24 hours

### 2. Error Handling

Implement graceful fallbacks:
- If XMLTV download fails, use cached version
- If MediathekView is down, show only live TV
- If Redis unavailable, function without cache (slower but still works)

### 3. Performance Considerations

- Download XMLTV file on first request, cache in memory and Redis
- Parse XMLTV only once per cache period
- Use async/await for API calls where possible
- Limit Mediathek search results to 50-100 items
- Filter on backend, not frontend

### 4. German Language Requirements

All user-facing text must be in German:
- UI labels and buttons
- Error messages
- Genre names
- Content type labels (Film/Serie)
- Time formatting (24-hour clock)
- Date formatting (DD.MM.YYYY)

## Environment Variables

Create `.env` file:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Endpoints
MEDIATHEK_API_URL=https://mediathekviewweb.de/api/query
XMLTV_EPG_URL=https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz

# Cache TTLs (seconds)
EPG_CACHE_TTL=3600
MEDIATHEK_CACHE_TTL=7200

# Application Settings
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
gradio>=4.0.0
requests>=2.31.0
redis>=5.0.0
python-dotenv>=1.0.0
pydantic>=2.5.0
beautifulsoup4>=4.12.0
aiohttp>=3.9.0
pytest>=7.4.0
```

## Docker Compose Setup

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
    volumes:
      - ./app:/app
    command: python app/gradio_ui.py

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Testing Strategy

1. **Unit Tests:**
   - Content type detection accuracy
   - Genre normalization
   - XMLTV parsing
   - Mood-to-genre mapping

2. **Integration Tests:**
   - MediathekView API calls
   - XMLTV download and parsing
   - Caching behavior

3. **E2E Tests:**
   - User flow: select preferences → see recommendations
   - Edge cases: no results, API failures

## Known Limitations & Future Work

**Current Limitations:**
- No user authentication or profiles
- Session data lost on refresh
- Limited to today's TV program (no future days)
- No viewing history or "already seen" tracking
- German channels only

**Future Enhancements:**
- Add user accounts with persistent preferences
- Multi-day EPG viewing (up to 7 days ahead)
- "Mark as seen" functionality
- Personalized recommendations based on history
- Email/push notifications for favorite shows
- Integration with more Mediathek sources (ARTE, regional stations)
- Mobile app version
- Social features (share recommendations)

## Important Notes for Claude Code

1. **API Rate Limiting:** Always implement caching. Don't hit APIs on every request.

2. **XMLTV File Size:** The full XMLTV file is large (50-100MB). Parse efficiently and cache parsed data.

3. **Error Handling:** APIs can fail. Always have fallbacks and clear error messages in German.

4. **Timezone:** EPG data uses CET/CEST. Handle timezone conversions correctly.

5. **Content Availability:** Some Mediathek content is geo-restricted. Note this in UI when relevant.

6. **Performance:** Initial load might be slow (downloading XMLTV). Show loading indicator.

7. **German TV Specific:**
   - Prime time is 20:15 (8:15 PM) in Germany
   - Key channels: ARD (Das Erste), ZDF, RTL, ProSieben, Sat.1, VOX, arte
   - Public broadcasters (ARD, ZDF) have different program style than private (RTL, ProSieben)

## Resources & Documentation

- **MediathekViewWeb API:** https://mediathekviewweb.de/
- **epgshare01.online:** https://epgshare01.online/ (current EPG source)
- **TVprofil.net:** https://tvprofil.net/xmltv/ (former EPG source, URL dead since 2026)
- **XMLTV Format:** http://wiki.xmltv.org/index.php/XMLTVFormat
- **Gradio Docs:** https://www.gradio.app/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

## Implementation Status (Updated)

### ✅ Completed
- [x] Set up Python virtual environment (Docker)
- [x] Install dependencies from requirements.txt
- [x] Start Redis (Docker Compose)
- [x] Create .env file with configuration
- [x] Test MediathekView API connection (✅ Working)
- [x] Implement filtered EPG system (replaces full XMLTV download)
- [x] Implement basic Gradio UI (✅ German interface)
- [x] Add caching layer (Redis)
- [x] Implement recommendation logic
- [x] Add content type detection (Film/Serie)
- [x] Add genre normalization and mood mapping
- [x] Add error handling and loading states
- [x] Docker setup with docker-compose.yml

### 🔧 Implemented, Testing Required
- [ ] Test filtered EPG download and parsing
- [ ] Test live TV recommendations with real EPG data
- [ ] Verify all 10 channels are correctly filtered
- [ ] Test with different mood/genre combinations
- [ ] Performance testing (first load vs cached loads)

### 📋 Next Steps
1. **Restart Docker containers** with new EPG implementation
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Test EPG filtering** (first load will take 30-60 seconds)
   - Make a request with live TV enabled
   - Check Docker logs for "Downloading XMLTV..." message
   - Verify `app/data/epg_filtered.json` is created
   - Check file size (~1-3MB)

3. **Test live TV recommendations**
   - Request with mood="spannend", genres=["Krimi"], live TV only
   - Should return tonight's crime shows from main channels
   - Verify German formatting of times and descriptions

4. **Complete unit tests**
   - EPG filter utility tests
   - Content type detection tests
   - Genre mapper tests

5. **Production readiness**
   - Add cron job for daily EPG updates (optional)
   - Add monitoring/alerting
   - Document deployment process

### 🐛 Known Issues
- EPG data persistence requires volume mount (✅ Already configured)
- First load slow but acceptable (~30-60 seconds)
- Need to verify channel name matching in XMLTV

---

**Project Status:** MVP Implementation Complete - Testing Phase
**Target MVP Date:** Ready for testing
**Last Updated:** 2025-10-28
