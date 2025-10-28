# German TV Program APIs: Complete Technical Guide

**No official public APIs exist** for German TV program data, but robust community solutions and commercial services provide comprehensive access to EPG schedules and Mediathek content. For your TV recommendation app, **MediathekViewWeb** (Mediathek content) and **TVprofil.net** (EPG data) offer the best combination of legality, reliability, and ease of integration.

## Best overall approach for your project

For a German TV recommendation app with today's program and on-demand content, implement a hybrid solution using **MediathekViewWeb API** for ARD/ZDF Mediathek content (free, legal, comprehensive) combined with **TVprofil.net XMLTV files** for live EPG schedules (free for personal use). If you need more control or additional private broadcaster coverage, add **WebGrab+Plus** for custom EPG scraping. This combination provides complete coverage while remaining legal for personal/educational projects.

## Public broadcaster APIs (ARD, ZDF Mediathek)

### MediathekViewWeb API - The gold standard

MediathekViewWeb aggregates all German public broadcasters into a unified, searchable database. This community project is your best option for accessing Mediathek content programmatically.

**API endpoint:** `https://mediathekviewweb.de/api/query`

**Authentication:** None required - completely free and open

**Rate limits:** No strict limits documented, reasonable usage expected

**Data format:** JSON with comprehensive metadata

**Coverage:** ARD, ZDF, arte, 3sat, BR, WDR, NDR, MDR, RBB, HR, SWR, SR, Phoenix, KiKA, tagesschau24, ONE, and all regional ARD stations

**Available metadata includes:**
- Video title, topic/series name, description
- Channel/broadcaster
- Publication timestamp and duration
- Direct video URLs (standard, low quality, HD)
- Website URLs and subtitle links
- File size information

**Python implementation:**

```python
import requests
import json

def search_mediathek(search_term, channel=None, min_duration=0):
    """Search MediathekViewWeb for videos"""
    url = "https://mediathekviewweb.de/api/query"
    
    queries = [{"fields": ["title", "topic"], "query": search_term}]
    if channel:
        queries.append({"fields": ["channel"], "query": channel})
    
    query = {
        "queries": queries,
        "sortBy": "timestamp",
        "sortOrder": "desc",
        "future": False,
        "offset": 0,
        "size": 50,
        "duration_min": min_duration,
        "duration_max": 99999
    }
    
    response = requests.post(
        url,
        data=json.dumps(query),
        headers={"Content-Type": "text/plain"}
    )
    
    return response.json()

# Search for crime shows on ARD
results = search_mediathek("Tatort", channel="ARD")
for video in results['result']['results']:
    print(f"{video['title']} ({video['duration']}s)")
    print(f"HD: {video.get('url_video_hd', 'N/A')}")
    print(f"Description: {video['description'][:100]}...")
    print()
```

**Recommended Python library:** [pymediathek](https://github.com/linusgke/pymediathek)

```python
from pymediathek import MediathekOptions, find_programme
import asyncio
import aiohttp

async def get_ard_video(url):
    async with aiohttp.ClientSession() as session:
        programme = await find_programme(
            field="website_url",
            target_value=url,
            options=MediathekOptions(http_session=session)
        )
        return programme

# Usage
video = asyncio.run(get_ard_video("https://www.ardmediathek.de/video/..."))
```

**Terms of use:** Free for personal and educational projects. Content intended for non-commercial use. Respect copyright and geo-restrictions (most content restricted to Germany/Austria/Switzerland).

### ARD Mediathek unofficial API

**Base URL:** `https://api.ardmediathek.de/page-gateway`

**Authentication:** Not required for public content

**Data format:** JSON with nested structures

**Key endpoints:**

```python
# Editorial content
editorial_url = "https://api.ardmediathek.de/page-gateway/widgets/ard/editorials/{widgetId}?pageNumber=0&pageSize=10"

# Video details
video_url = f"https://api.ardmediathek.de/page-gateway/pages/ard/item/{itemId}"

# Example implementation
import requests

def get_ard_video_details(video_id):
    url = f"https://api.ardmediathek.de/page-gateway/pages/ard/item/{video_id}"
    response = requests.get(url)
    data = response.json()
    
    # Extract video stream
    streams = data['widgets'][0]['mediaCollection']['embedded']['_mediaArray'][0]['_mediaStreamArray']
    return {
        'title': data['widgets'][0]['title'],
        'description': data['widgets'][0]['synopsis'],
        'video_url': streams[0]['_stream'],
        'duration': data['widgets'][0]['duration']
    }
```

**Available metadata:** Title, subtitle, description, show information, broadcast date, duration, thumbnails (various aspect ratios), video stream URLs (HLS .m3u8, MP4), publication service, geoblocking status

**Rate limits:** No official limits - recommend maximum 1 request per second

**Community projects:**
- [Bouni/ard-mediathek](https://github.com/Bouni/ard-mediathek) - Python downloader with CLI
- [raptor2101/Mediathek](https://github.com/raptor2101/Mediathek) - GraphQL implementation

### ZDF Mediathek unofficial API

**Structure:** Undocumented JSON API with periodically changing endpoints

**Base pattern:** `https://api.zdf.de/content/documents/{documentId}.json`

**Authentication:** Requires API tokens extracted from ZDF website JavaScript (tokens change periodically)

**Challenges:** Token extraction required, endpoints change frequently, no official documentation

**Recommendation:** Use MediathekViewWeb instead for ZDF content - more stable and maintained

### arte.tv API

**API endpoints (v1 - still functional):**

```
https://api.arte.tv/api/player/v1/config/{language}/{videoId}?autostart=1&lifeCycle=1&lang={language}&config=arte_tvguide
```

**Languages supported:** de (German), fr (French), en, es, pl, it

**Authentication:** v1 API requires no authentication; v2 requires Bearer token

**Data format:** JSON with video sources in multiple qualities

**Python implementation:**

```python
import requests
import re

def get_arte_video(video_url):
    # Extract video ID (format: XXXXXX-XXX-A)
    video_id = re.search(r'(\d{6}-\d{3}-[A-Z])', video_url).group(1)
    
    api_url = f"https://api.arte.tv/api/player/v1/config/de/{video_id}?autostart=1&lifeCycle=1&lang=de_DE&config=arte_tvguide"
    
    response = requests.get(api_url)
    data = response.json()
    
    # Extract video URLs by quality
    videos = []
    for stream in data['videoJsonPlayer']['VSR'].values():
        videos.append({
            'quality': stream.get('quality'),
            'url': stream.get('url'),
            'mediaType': stream.get('mediaType')
        })
    
    return videos
```

**CORS note:** ARTE API blocks browser-based requests but works fine from server-side Python applications

## Live EPG data sources

### TVprofil.net XMLTV - Best free option

**Overview:** Free XMLTV EPG service with 5000+ European channels including comprehensive German coverage

**Base URL:** `https://tvprofil.net/xmltv/`

**Authentication:** None required

**Data format:** XMLTV (UTF-8 encoding, CET timezone)

**Coverage:** ARD, ZDF, RTL, ProSieben, Sat.1, VOX, and 5000+ other European channels

**Update frequency:** Automatic updates on internal channel changes

**Key endpoints:**

```python
# All EPG data (2-day coverage)
all_epg = "https://tvprofil.net/xmltv/epg_tvprofil.net.xml"

# Sport live events
sport_epg = "https://tvprofil.net/xmltv/epg_sport_live_tvprofil.net.xml"

# Channel list
channels = "https://tvprofil.net/xmltv/channel-list.tvprofil.net.xml"

# Per-channel weekly file
weekly = "xmltv/data/{channel-id}/weekly_{channel-id}_tvprofil.net.xml"

# Per-channel daily file
daily = "xmltv/data/{channel-id}/YYYY-MM-DD_{channel-id}_tvprofil.net.xml"
```

**Available metadata:** Program title, description, genres, air times, duration, channel information

**Python parsing implementation:**

```python
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

def parse_xmltv_time(timestr):
    """Parse XMLTV time format: YYYYMMDDHHmmss +ZZZZ"""
    dt = datetime.strptime(timestr[:14], '%Y%m%d%H%M%S')
    return dt

def get_current_programs(channel_id):
    """Get currently airing programs for a channel"""
    # Download EPG
    response = requests.get('https://tvprofil.net/xmltv/epg_tvprofil.net.xml')
    
    tree = ET.fromstring(response.content)
    now = datetime.now()
    
    current_programs = []
    for programme in tree.findall('programme'):
        if programme.get('channel') == channel_id:
            start = parse_xmltv_time(programme.get('start'))
            stop = parse_xmltv_time(programme.get('stop'))
            
            if start <= now <= stop:
                title = programme.find('title').text
                desc_elem = programme.find('desc')
                desc = desc_elem.text if desc_elem is not None else ''
                
                # Extract genres
                genres = [cat.text for cat in programme.findall('category')]
                
                current_programs.append({
                    'channel': channel_id,
                    'title': title,
                    'description': desc,
                    'start': start,
                    'stop': stop,
                    'genres': genres
                })
    
    return current_programs

# Usage
programs = get_current_programs('Das Erste')
for prog in programs:
    print(f"{prog['start']:%H:%M} - {prog['title']}")
    print(f"Genres: {', '.join(prog['genres'])}")
```

**Rate limits:** Static files are cached - avoid frequent downloads. Download once and cache locally, refresh every 6-12 hours

**Terms of use:** Free for home/personal use; commercial use requires contacting tvprofil@tvprofil.com. Must use provided XMLTV URLs (direct scraping prohibited)

**Best for:** Personal projects, home media centers (Kodi, Plex), educational applications

### WebGrab+Plus - Advanced self-hosted option

**Overview:** Free multi-site incremental XMLTV EPG grabber supporting 150+ sources worldwide including multiple German providers

**Website:** https://www.webgrabplus.com/

**Platform support:** Windows, Linux, macOS

**Data format:** XMLTV output (guide.xml)

**German sources available:**
- tvtv.de
- tvtoday.de
- vodafone.de
- horizon.tv
- sky.de
- magentatv.de
- hd-plus.de (requires decryption key)

**Configuration example:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <filename>guide.xml</filename>
  <mode>incremental</mode>
  <timespan>7</timespan>
  <channel update="i" site="tvtv.de" site_id="ARD" xmltv_id="Das Erste">Das Erste</channel>
  <channel update="i" site="tvtv.de" site_id="ZDF" xmltv_id="ZDF">ZDF</channel>
  <channel update="i" site="tvtv.de" site_id="RTL" xmltv_id="RTL">RTL</channel>
</settings>
```

**Licensing tiers:**
- **Unregistered:** 20 channels, 2 siteinis, 4-second delays
- **Registered (free):** 30 channels, 3 siteinis
- **Donator (€5/year):** 250 channels, 15 siteinis, no delays, encrypted siteinis access

**Python automation:**

```python
import subprocess
import schedule
from pathlib import Path

def run_webgrabplus():
    """Run WebGrab+Plus to update EPG"""
    webgrab_path = Path("/path/to/WebGrab+Plus.exe")
    config_dir = Path("/path/to/config")
    
    result = subprocess.run(
        [str(webgrab_path), str(config_dir / "WebGrab++.config.xml")],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("EPG update successful")
    else:
        print(f"EPG update failed: {result.stderr}")
    
    return result.returncode == 0

# Schedule daily updates at 2 AM
schedule.every().day.at("02:00").do(run_webgrabplus)
```

**Best for:** Advanced users, custom source combinations, self-hosted EPG solutions, home media centers

**Authentication:** Optional registration for increased limits

**Rate limits:** Configurable in siteini files, respects source website requirements

### iptv-org/epg - Open source grabber

**GitHub:** https://github.com/iptv-org/epg

**Overview:** Node.js-based EPG grabber utilities supporting hundreds of sources worldwide

**Installation:**

```bash
git clone --depth 1 -b master https://github.com/iptv-org/epg.git
cd epg
npm install
```

**Usage:**

```bash
# Grab from specific site
npm run grab --- --site=example.com

# Custom channels file
npm run grab --- --channels=path/to/custom.channels.xml

# With options
npm run grab --- --site=example.com --maxConnections=10 --days=7 --output=guide.xml
```

**Docker deployment:**

```bash
docker run \
  -p 3000:3000 \
  -v /path/to/channels.xml:/epg/channels.xml \
  -e CRON_SCHEDULE="0 0,12 * * *" \
  -e MAX_CONNECTIONS=10 \
  iptv-org/epg
```

**Best for:** Developers, self-hosted solutions, Docker deployments

### Commercial EPG services

**EPGdata.com status:** This service was discontinued in 2022 after being a primary solution (previously €17.95/year)

**FUNKE Digital TV Guide:** Enterprise-grade metadata from FUNKE Mediengruppe (publishers of TV DIGITAL and HÖRZU magazines). Contact sales for API access - best for commercial applications with budget.

**Gracenote (Nielsen):** Industry-leading enterprise EPG covering 80+ countries. Offers free public plan with limited access and commercial plans with full coverage. Base URL: https://api.themoviedb.org/3/

**EPG Service (epgservice.tv):** Commercial API primarily for IPTV/OTT platforms with real-time updates and accurate timestamps. Contact for commercial pricing.

## Alternative approaches for private broadcasters

### Web scraping considerations

German private broadcasters (RTL, ProSieben, Sat.1, VOX) provide **no public APIs**. Alternative approaches involve web scraping or commercial services.

**Primary scraping targets:**

**TV-Spielfilm.de** - Most comprehensive German TV program guide
- **Coverage:** 200+ channels including all major private broadcasters
- **Data available:** 7+ days ahead with program descriptions, ratings, genres, durations
- **Owner:** Hubert Burda Media
- **Robots.txt status:** Must verify before scraping
- **Community project:** [Michdo93/python-german-epg](https://github.com/Michdo93/python-german-epg)

**Implementation example:**

```python
import requests
from bs4 import BeautifulSoup
import time
from urllib.robotparser import RobotFileParser

class GermanTVScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PersonalProject/1.0 (your.email@example.com)',
            'Accept-Language': 'de-DE,de;q=0.9',
        })
        self.check_robots_txt()
    
    def check_robots_txt(self):
        """Check robots.txt before scraping"""
        rp = RobotFileParser()
        rp.set_url(f"{self.base_url}/robots.txt")
        try:
            rp.read()
            if not rp.can_fetch("*", self.base_url):
                raise Exception("Scraping disallowed by robots.txt")
        except:
            print("Warning: Could not read robots.txt")
    
    def scrape_schedule(self, channel, date):
        """Scrape TV schedule for given channel and date"""
        # Rate limiting - ESSENTIAL
        time.sleep(12)  # 12 seconds between requests
        
        url = f"{self.base_url}/programm/{channel}/{date}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse schedule (site-specific selectors needed)
            programs = []
            # ... add parsing logic based on site structure ...
            
            return programs
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
```

**Legal and ethical requirements:**

**Must do:**
- ✅ Check and respect robots.txt
- ✅ Set proper User-Agent with contact information
- ✅ Implement rate limiting (minimum 10-15 seconds between requests)
- ✅ Respect crawl-delay directives
- ✅ Cache results to minimize requests
- ✅ Keep scraped data private (no republishing)
- ✅ Review Terms of Service
- ✅ Request permission for commercial use

**Legal framework (Germany/EU):**
- Web scraping exists in legal gray area
- EU Database Directive protects substantial database portions
- Robots.txt not legally binding but ethically important
- Personal/research use generally more permissive
- Commercial use requires proper licensing
- GDPR compliance required for personal data
- German courts have mixed rulings on scraping legality

**TVToday.de** - Alternative scraping target
- Supported by WebGrab+Plus with maintained configuration files
- Series episode information available
- Regional channel variants included

### RSS feeds and alternatives

**Limited availability:** German TV broadcasters provide very limited RSS feed access for EPG data. RSS more commonly used for on-demand content notifications rather than live schedules.

**MediathekView RSS:** Community project [Mediathek2RSS](https://github.com/) creates RSS feeds for public broadcaster Mediathek content, but not applicable to live EPG schedules.

**DVB/Satellite EPG extraction:** Legal method using DVB-T/S/C broadcast streams with tools like VDR or TVHeadend. Requires DVB hardware but provides comprehensive, legal EPG data for received channels.

## Implementation recommendations

### Architecture for your TV recommendation app

**Recommended stack:**

```
Frontend: React/Vue.js
Backend: Python (Flask/FastAPI)
Database: PostgreSQL + Redis (caching)
Data sources: MediathekViewWeb + TVprofil.net
```

**System architecture:**

```python
# Backend service structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import redis
import json

app = FastAPI()
cache = redis.Redis(host='localhost', port=6379, db=0)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TVDataService:
    def __init__(self):
        self.mediathek_url = "https://mediathekviewweb.de/api/query"
        self.epg_url = "https://tvprofil.net/xmltv/epg_tvprofil.net.xml"
    
    def get_mediathek_content(self, query=None, channel=None):
        """Get on-demand content from Mediathek"""
        # Check cache first
        cache_key = f"mediathek:{query}:{channel}"
        cached = cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query MediathekViewWeb
        queries = []
        if query:
            queries.append({"fields": ["title", "topic"], "query": query})
        if channel:
            queries.append({"fields": ["channel"], "query": channel})
        
        payload = {
            "queries": queries,
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": False,
            "offset": 0,
            "size": 100
        }
        
        response = requests.post(
            self.mediathek_url,
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain"}
        )
        
        result = response.json()
        
        # Cache for 1 hour
        cache.setex(cache_key, 3600, json.dumps(result))
        
        return result
    
    def get_live_schedule(self, channels=None):
        """Get today's TV schedule from EPG"""
        # Check cache
        cache_key = "epg:today"
        cached = cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Download and parse XMLTV
        response = requests.get(self.epg_url)
        tree = ET.fromstring(response.content)
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        
        schedule = {}
        for programme in tree.findall('programme'):
            channel = programme.get('channel')
            
            if channels and channel not in channels:
                continue
            
            start_str = programme.get('start')
            start = datetime.strptime(start_str[:14], '%Y%m%d%H%M%S')
            
            if today_start <= start < today_end:
                if channel not in schedule:
                    schedule[channel] = []
                
                title_elem = programme.find('title')
                desc_elem = programme.find('desc')
                
                schedule[channel].append({
                    'title': title_elem.text if title_elem is not None else '',
                    'description': desc_elem.text if desc_elem is not None else '',
                    'start': start.isoformat(),
                    'stop': programme.get('stop'),
                    'genres': [cat.text for cat in programme.findall('category')]
                })
        
        # Cache for 30 minutes
        cache.setex(cache_key, 1800, json.dumps(schedule))
        
        return schedule

tv_service = TVDataService()

@app.get("/api/schedule")
async def get_schedule(channels: str = None):
    """Get today's TV schedule"""
    channel_list = channels.split(',') if channels else None
    return tv_service.get_live_schedule(channel_list)

@app.get("/api/mediathek")
async def search_mediathek(q: str = None, channel: str = None, genre: str = None):
    """Search Mediathek content"""
    results = tv_service.get_mediathek_content(query=q, channel=channel)
    
    # Filter by genre if requested
    if genre:
        filtered = []
        for item in results.get('result', {}).get('results', []):
            # Implement genre filtering logic
            filtered.append(item)
        return {'results': filtered}
    
    return results

@app.get("/api/recommendations")
async def get_recommendations(content_type: str = None):
    """Get recommendations based on filtering"""
    # Combine live and on-demand content
    live = tv_service.get_live_schedule()
    mediathek = tv_service.get_mediathek_content()
    
    # Apply filtering by content_type (movie vs TV show)
    # Implement recommendation algorithm
    
    return {
        'live': live,
        'on_demand': mediathek
    }
```

**Frontend integration example:**

```javascript
// React component for TV schedule
import React, { useState, useEffect } from 'react';

function TVSchedule() {
  const [schedule, setSchedule] = useState({});
  const [filter, setFilter] = useState({ genre: '', type: 'all' });
  
  useEffect(() => {
    fetch('http://localhost:8000/api/schedule?channels=ARD,ZDF,RTL,ProSieben')
      .then(res => res.json())
      .then(data => setSchedule(data));
  }, []);
  
  const filterPrograms = () => {
    // Implement filtering by genre and content type
    // Movie detection: duration > 70 mins, certain keywords
  };
  
  return (
    <div>
      <FilterBar filter={filter} setFilter={setFilter} />
      <ProgramGrid schedule={schedule} filter={filter} />
    </div>
  );
}
```

### Content type detection (movie vs TV show)

Since EPG data doesn't always explicitly mark content type, implement heuristics:

```python
def detect_content_type(program):
    """Detect if program is movie or TV show"""
    title = program.get('title', '').lower()
    duration = program.get('duration', 0)
    genres = [g.lower() for g in program.get('genres', [])]
    
    # Movie indicators
    movie_keywords = ['film', 'spielfilm', 'kinofilm', 'fernsehfilm']
    movie_genres = ['drama', 'komödie', 'thriller', 'action', 'krimi']
    
    # TV show indicators
    series_keywords = ['serie', 'reihe', 'folge', 'staffel']
    
    # Scoring system
    score = 0
    
    # Duration check (movies typically 70+ minutes)
    if duration >= 4200:  # 70 minutes
        score += 2
    
    # Title keyword check
    if any(kw in title for kw in movie_keywords):
        score += 3
    if any(kw in title for kw in series_keywords):
        score -= 2
    
    # Genre check
    if any(g in genres for g in movie_genres):
        score += 1
    
    return 'movie' if score >= 2 else 'show'
```

### Genre normalization

Different sources use different genre taxonomies. Normalize them:

```python
GENRE_MAPPING = {
    'Krimi': 'crime',
    'Thriller': 'thriller',
    'Komödie': 'comedy',
    'Drama': 'drama',
    'Dokumentation': 'documentary',
    'Nachrichten': 'news',
    'Sport': 'sports',
    'Spielfilm': 'movie',
    'Serie': 'series',
    # Add more mappings
}

def normalize_genre(german_genre):
    """Convert German genre names to standardized English"""
    return GENRE_MAPPING.get(german_genre, german_genre.lower())
```

### Caching strategy

Implement aggressive caching to minimize API calls:

```python
import redis
from functools import wraps
import hashlib
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def cached(ttl=3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=1800)  # Cache for 30 minutes
def get_tv_schedule(date):
    # Expensive operation
    pass
```

**Recommended cache durations:**
- EPG data: 30-60 minutes
- Mediathek search results: 1-2 hours
- Channel lists: 24 hours
- Static content: 7 days

## Complete code examples

### Full XMLTV parser with filtering

```python
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TVProgramParser:
    def __init__(self, xmltv_url: str):
        self.xmltv_url = xmltv_url
        self.tree = None
        self.channels = {}
    
    def fetch_data(self):
        """Download and parse XMLTV data"""
        response = requests.get(self.xmltv_url, timeout=30)
        response.raise_for_status()
        self.tree = ET.fromstring(response.content)
        
        # Parse channel information
        for channel in self.tree.findall('channel'):
            channel_id = channel.get('id')
            display_name = channel.find('display-name')
            if display_name is not None:
                self.channels[channel_id] = display_name.text
    
    def parse_time(self, timestr: str) -> datetime:
        """Parse XMLTV timestamp format"""
        return datetime.strptime(timestr[:14], '%Y%m%d%H%M%S')
    
    def get_programs(
        self,
        channel_ids: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        genres: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get programs with optional filtering"""
        
        if not self.tree:
            self.fetch_data()
        
        # Default time range: today
        if not start_time:
            start_time = datetime.now().replace(hour=0, minute=0, second=0)
        if not end_time:
            end_time = start_time + timedelta(days=1)
        
        programs = []
        
        for programme in self.tree.findall('programme'):
            channel = programme.get('channel')
            
            # Filter by channel
            if channel_ids and channel not in channel_ids:
                continue
            
            # Parse times
            start = self.parse_time(programme.get('start'))
            stop = self.parse_time(programme.get('stop'))
            
            # Filter by time range
            if not (start_time <= start < end_time):
                continue
            
            # Extract metadata
            title_elem = programme.find('title')
            title = title_elem.text if title_elem is not None else ''
            
            desc_elem = programme.find('desc')
            description = desc_elem.text if desc_elem is not None else ''
            
            # Extract genres/categories
            program_genres = [cat.text for cat in programme.findall('category')]
            
            # Filter by genre
            if genres and not any(g in program_genres for g in genres):
                continue
            
            # Extract additional metadata
            episode_elem = programme.find('episode-num')
            rating_elem = programme.find('star-rating')
            
            program_data = {
                'channel_id': channel,
                'channel_name': self.channels.get(channel, channel),
                'title': title,
                'description': description,
                'start': start.isoformat(),
                'stop': stop.isoformat(),
                'duration_minutes': int((stop - start).total_seconds() / 60),
                'genres': program_genres,
                'episode': episode_elem.text if episode_elem is not None else None,
                'rating': rating_elem.find('value').text if rating_elem is not None else None
            }
            
            programs.append(program_data)
        
        return programs
    
    def get_now_playing(self, channel_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get currently airing programs"""
        now = datetime.now()
        
        if not self.tree:
            self.fetch_data()
        
        current_programs = []
        
        for programme in self.tree.findall('programme'):
            channel = programme.get('channel')
            
            if channel_ids and channel not in channel_ids:
                continue
            
            start = self.parse_time(programme.get('start'))
            stop = self.parse_time(programme.get('stop'))
            
            # Check if program is currently airing
            if start <= now < stop:
                title_elem = programme.find('title')
                desc_elem = programme.find('desc')
                
                current_programs.append({
                    'channel_id': channel,
                    'channel_name': self.channels.get(channel, channel),
                    'title': title_elem.text if title_elem is not None else '',
                    'description': desc_elem.text if desc_elem is not None else '',
                    'start': start.isoformat(),
                    'stop': stop.isoformat(),
                    'progress_percent': int(((now - start).total_seconds() / 
                                           (stop - start).total_seconds()) * 100)
                })
        
        return current_programs

# Usage example
parser = TVProgramParser('https://tvprofil.net/xmltv/epg_tvprofil.net.xml')

# Get all programs today
today_programs = parser.get_programs()

# Get specific channels
ard_zdf = parser.get_programs(channel_ids=['Das Erste', 'ZDF'])

# Get programs by genre
crime_shows = parser.get_programs(genres=['Krimi', 'Thriller'])

# Get what's currently playing
now_playing = parser.get_now_playing(channel_ids=['ARD', 'ZDF', 'RTL'])
```

### Combined Mediathek + EPG service

```python
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class GermanTVService:
    def __init__(self):
        self.mediathek_url = "https://mediathekviewweb.de/api/query"
        self.epg_url = "https://tvprofil.net/xmltv/epg_tvprofil.net.xml"
    
    def search_mediathek(
        self,
        query: str = "",
        channels: Optional[List[str]] = None,
        min_duration: int = 0,
        max_duration: int = 99999,
        limit: int = 50
    ) -> Dict:
        """Search MediathekView for on-demand content"""
        
        queries = []
        if query:
            queries.append({"fields": ["title", "topic"], "query": query})
        
        if channels:
            for channel in channels:
                queries.append({"fields": ["channel"], "query": channel})
        
        payload = {
            "queries": queries,
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": False,
            "offset": 0,
            "size": limit,
            "duration_min": min_duration,
            "duration_max": max_duration
        }
        
        response = requests.post(
            self.mediathek_url,
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        
        return response.json()
    
    def get_recommendations(
        self,
        content_type: Optional[str] = None,  # 'movie' or 'show'
        genres: Optional[List[str]] = None,
        channels: Optional[List[str]] = None
    ) -> Dict:
        """Get content recommendations combining live and on-demand"""
        
        # Get live schedule
        from TVProgramParser import TVProgramParser
        epg_parser = TVProgramParser(self.epg_url)
        live_programs = epg_parser.get_programs(
            channel_ids=channels,
            genres=genres
        )
        
        # Get on-demand content
        mediathek_query = " ".join(genres) if genres else ""
        mediathek_results = self.search_mediathek(
            query=mediathek_query,
            channels=channels,
            min_duration=4200 if content_type == 'movie' else 0
        )
        
        # Filter and combine results
        recommendations = {
            'live': [],
            'on_demand': []
        }
        
        # Process live programs
        for program in live_programs:
            if content_type:
                detected_type = self._detect_content_type(program)
                if detected_type != content_type:
                    continue
            
            recommendations['live'].append({
                'type': 'live',
                'channel': program['channel_name'],
                'title': program['title'],
                'description': program['description'],
                'start': program['start'],
                'duration': program['duration_minutes'],
                'genres': program['genres']
            })
        
        # Process Mediathek results
        for item in mediathek_results.get('result', {}).get('results', []):
            if content_type == 'movie' and item.get('duration', 0) < 4200:
                continue
            
            recommendations['on_demand'].append({
                'type': 'on_demand',
                'channel': item['channel'],
                'title': item['title'],
                'description': item.get('description', ''),
                'url': item.get('url_website', ''),
                'video_url': item.get('url_video_hd', item.get('url_video', '')),
                'duration': item.get('duration', 0) // 60,
                'published': datetime.fromtimestamp(item['timestamp']).isoformat()
            })
        
        return recommendations
    
    def _detect_content_type(self, program: Dict) -> str:
        """Detect if content is movie or TV show"""
        title = program.get('title', '').lower()
        duration = program.get('duration_minutes', 0)
        
        movie_keywords = ['film', 'spielfilm', 'kinofilm']
        series_keywords = ['serie', 'reihe', 'folge']
        
        score = 0
        if duration >= 70:
            score += 2
        if any(kw in title for kw in movie_keywords):
            score += 3
        if any(kw in title for kw in series_keywords):
            score -= 2
        
        return 'movie' if score >= 2 else 'show'

# Usage
service = GermanTVService()

# Search for crime content
crime_content = service.search_mediathek(
    query="Tatort",
    channels=["ARD", "ZDF"]
)

# Get movie recommendations
movies = service.get_recommendations(
    content_type='movie',
    genres=['Krimi', 'Thriller'],
    channels=['ARD', 'ZDF', 'arte']
)

print(f"Found {len(movies['live'])} live movies")
print(f"Found {len(movies['on_demand'])} on-demand movies")
```

## Terms of use summary

**MediathekViewWeb:** Free for personal and educational use. Content is copyrighted by broadcasters and intended for non-commercial use. Respect geo-restrictions.

**TVprofil.net:** Free for personal/home use with attribution. Commercial use requires contacting tvprofil@tvprofil.com. Must use provided XMLTV files, not scrape website.

**ARD/ZDF APIs (unofficial):** No official terms since APIs are undocumented. Community consensus is personal use acceptable. ARD explicitly confirmed private EPG scraping is legal.

**arte.tv API:** No official public API terms. v1 endpoint functional without authentication. Use responsibly.

**Web scraping:** Must respect robots.txt, implement rate limiting, use descriptive User-Agent, and limit to personal/educational use. Commercial use requires proper licensing from content owners.

**GDPR compliance:** EPG and program metadata generally not considered personal data. If collecting user preferences or personal information, GDPR requirements apply.

## Summary and final recommendations

For your German TV recommendation web app showing today's programs and on-demand Mediathek content with genre/type filtering:

**Optimal implementation:**
1. **Use MediathekViewWeb API** for all public broadcaster on-demand content (ARD, ZDF, arte, 3sat, regional stations)
2. **Use TVprofil.net XMLTV files** for live EPG schedules (download and cache, refresh every 6-12 hours)
3. **Implement filtering** for movies vs TV shows using duration and keyword heuristics
4. **Add genre normalization** to standardize German genre names
5. **Set up Redis caching** to minimize API calls and improve performance
6. **Deploy with FastAPI backend** and React/Vue frontend

**For private broadcasters (RTL, ProSieben):**
- TVprofil.net includes these channels in their XMLTV feed
- If more detailed data needed, consider WebGrab+Plus for self-hosted scraping
- Respect robots.txt and rate limiting requirements

**Python libraries to install:**

```bash
pip install fastapi uvicorn requests beautifulsoup4 redis python-multipart aiohttp
```

This approach provides comprehensive coverage of German TV (both public and private broadcasters), remains legal for personal/educational projects, and offers reliable data sources that are well-maintained by the community. The combination of MediathekViewWeb's robust API and TVprofil.net's free XMLTV service gives you everything needed to build a feature-rich TV recommendation application.