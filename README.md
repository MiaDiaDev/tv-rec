# German TV Recommender

Eine Web-Anwendung, die deutsche TV-Inhalte basierend auf Benutzerpräferenzen empfiehlt. Die App richtet sich an deutsche Nutzer und hilft ihnen zu entdecken, was sie heute Abend schauen können - sowohl aus dem Live-TV-Programm als auch aus On-Demand-Inhalten der ARD/ZDF Mediatheken.

## 🚀 Implementation Status

**✅ Voll funktionsfähig:**
- Gradio Web-UI mit deutschem Interface
- MediathekViewWeb API Integration (On-Demand Content)
- Genre-Normalisierung und Mood-Mapping
- Film/Serie-Erkennung
- Redis Caching
- Docker Setup

**🔧 Implementiert, Teste ausstehend:**
- Gefiltertes EPG-System für Live TV (10 Hauptsender)
- Automatische EPG-Aktualisierung

**📋 Nächste Schritte:**
1. Container neu starten und EPG-Download testen
2. Live TV Empfehlungen verifizieren
3. Performance-Tests durchführen
4. Unit Tests vervollständigen

## Features

- 🎭 **Stimmungsbasierte Empfehlungen**: Wählen Sie Ihre Stimmung (entspannt, spannend, lustig, etc.)
- 🎬 **Genre-Filter**: Filtern nach Krimi, Komödie, Drama, Dokumentation und mehr
- 📺 **Live TV & Mediathek**: Kombiniert Live-Programm mit On-Demand-Inhalten
- 🔍 **Intelligente Erkennung**: Automatische Unterscheidung zwischen Filmen und Serien
- ⚡ **Schnell & Cached**: Redis-Caching und gefiltertes EPG für optimale Performance

## Technologie-Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Gradio
- **Caching**: Redis
- **APIs**: MediathekViewWeb API (On-Demand), TVprofil.net XMLTV (Live TV mit Filterung)

## Schnellstart

### Mit Docker (empfohlen)

```bash
# Repository klonen
git clone <repository-url>
cd tv_rec

# Umgebungsvariablen konfigurieren
cp .env.example .env

# Mit Docker Compose starten
docker-compose up
```

Die App ist dann verfügbar unter: http://localhost:7860

### Ohne Docker

```bash
# Python Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Redis starten (separat)
redis-server

# Umgebungsvariablen konfigurieren
cp .env.example .env

# Gradio UI starten
python app/gradio_ui.py

# Oder FastAPI starten
python app/main.py
```

## Projektstruktur

```
tv-recommender/
├── app/
│   ├── main.py              # FastAPI Hauptanwendung
│   ├── gradio_ui.py         # Gradio Benutzeroberfläche
│   ├── config.py            # Konfigurationsverwaltung
│   ├── data/                # EPG-Daten (nicht in Git)
│   │   └── epg_filtered.json
│   ├── services/
│   │   ├── mediathek.py     # MediathekViewWeb API Client
│   │   ├── epg.py           # Gefilterter EPG Service
│   │   ├── recommender.py   # Empfehlungslogik
│   │   └── cache.py         # Redis Caching
│   ├── models/
│   │   └── schemas.py       # Pydantic Modelle
│   └── utils/
│       ├── content_detector.py  # Film/Serie Erkennung
│       ├── genre_mapper.py      # Genre-Normalisierung
│       └── epg_filter.py        # EPG Filter-Utility
├── scripts/
│   └── update_epg.py        # Manuelle EPG-Aktualisierung
├── tests/                   # Unit Tests
├── requirements.txt         # Python Dependencies
├── docker-compose.yml       # Docker Compose Konfiguration
├── Dockerfile              # Docker Image
├── CLAUDE.md               # Detaillierte Projektdokumentation
└── README.md
```

## Verwendung

### Gradio UI

1. Öffnen Sie http://localhost:7860
2. Wählen Sie Ihre Stimmung und Präferenzen
3. Klicken Sie auf "Empfehlungen anzeigen"

### FastAPI

Die API ist verfügbar unter http://localhost:8000

**Empfehlungen abrufen:**

```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "entspannt",
    "genres": ["Komödie"],
    "content_type": null
  }'
```

**Verfügbare Genres:**

```bash
curl "http://localhost:8000/genres"
```

**Verfügbare Stimmungen:**

```bash
curl "http://localhost:8000/moods"
```

## Konfiguration

Passen Sie `.env` an:

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Cache TTLs
EPG_CACHE_TTL=3600
MEDIATHEK_CACHE_TTL=7200

# App Settings
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Tests ausführen

```bash
pytest tests/
```

## Datenquellen

- **MediathekViewWeb API**: On-Demand Content von ARD, ZDF, arte, 3sat und regionalen Sendern
- **TVprofil.net XMLTV**: Live EPG-Daten, gefiltert auf 10 Hauptsender:
  - Öffentlich-rechtlich: Das Erste (ARD), ZDF, 3sat, arte
  - Privatsender: RTL, ProSieben, Sat.1, VOX, RTL II, Kabel Eins

### EPG-System (Optimiert)

Statt der vollständigen 100MB XMLTV-Datei (5000+ Kanäle) nutzt die App ein **gefiltertes System**:

- **Erstdownload**: Einmalig beim ersten Start (~30-60 Sekunden)
- **Gefiltertes EPG**: Nur 10 Hauptsender, ~1-3MB statt 100MB
- **Automatische Updates**: Alle 6 Stunden
- **Manuelle Aktualisierung**: `python scripts/update_epg.py`
- **Persistenz**: EPG-Daten bleiben zwischen Container-Neustarts erhalten

## Einschränkungen

- Nur deutsche Sender (10 Hauptsender für Live TV)
- Sitzungsbasiert (keine persistenten Benutzerprofile)
- Nur heutiges + morgiges TV-Programm
- Manche Mediathek-Inhalte sind geo-beschränkt

## Lizenz

Siehe CLAUDE.md für Details zu den API-Nutzungsbedingungen.

## Entwicklung

Siehe `CLAUDE.md` für detaillierte Projektdokumentation und Implementierungsrichtlinien.
