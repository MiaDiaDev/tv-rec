"""EPG filter utility to create lightweight filtered EPG data."""

import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


# Channel mapping: XMLTV channel ID patterns -> our standard name
CHANNEL_MAPPING = {
    'Das Erste': ['Das Erste', 'ARD', 'das erste', 'ard.de'],
    'ZDF': ['ZDF', 'zdf.de', 'ZDF HD'],
    'RTL': ['RTL', 'RTL Television', 'rtl.de'],
    'ProSieben': ['ProSieben', 'Pro7', 'Pro 7', 'prosieben.de'],
    'Sat.1': ['SAT.1', 'Sat.1', 'sat1.de'],
    'VOX': ['VOX', 'vox.de'],
    'RTL II': ['RTL ZWEI', 'RTL II', 'RTL2', 'rtl2.de'],
    'Kabel Eins': ['kabel eins', 'Kabel 1', 'Kabel Eins', 'kabeleins.de'],
    '3sat': ['3sat', '3sat.de'],
    'arte': ['ARTE', 'arte', 'arte.de', 'arte.tv']
}


def normalize_channel_name(xmltv_channel: str) -> Optional[str]:
    """
    Normalize XMLTV channel ID/name to our standard channel name.

    Args:
        xmltv_channel: Channel ID or name from XMLTV

    Returns:
        Standard channel name or None if not in our list
    """
    xmltv_lower = xmltv_channel.lower()

    for standard_name, patterns in CHANNEL_MAPPING.items():
        for pattern in patterns:
            if pattern.lower() in xmltv_lower:
                return standard_name

    return None


def parse_xmltv_time(time_str: str) -> Optional[datetime]:
    """
    Parse XMLTV time format to timezone-aware datetime.

    Args:
        time_str: Time string in format "YYYYMMDDHHmmss +ZZZZ"

    Returns:
        Timezone-aware datetime object or None
    """
    try:
        from datetime import timezone

        # Format: 20241018200000 +0200
        if '+' in time_str or '-' in time_str:
            parts = time_str.split()
            time_part = parts[0]
            offset_part = parts[1] if len(parts) > 1 else '+0000'

            # Parse base datetime
            dt = datetime.strptime(time_part, "%Y%m%d%H%M%S")

            # Parse timezone offset
            sign = 1 if offset_part[0] == '+' else -1
            hours = int(offset_part[1:3])
            minutes = int(offset_part[3:5])
            offset = timezone(timedelta(hours=sign*hours, minutes=sign*minutes))

            # Make timezone-aware
            return dt.replace(tzinfo=offset)
        else:
            # No timezone info, assume CET (+0100/+0200)
            dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            cet = timezone(timedelta(hours=1))
            return dt.replace(tzinfo=cet)
    except Exception as e:
        print(f"Time parse error for '{time_str}': {e}")
        return None


def download_and_filter_epg(
    xmltv_url: str,
    output_path: str,
    days_ahead: int = 1
) -> Dict:
    """
    Download full XMLTV and create filtered JSON for main German channels.

    Args:
        xmltv_url: URL to download XMLTV from
        output_path: Path to save filtered JSON
        days_ahead: Number of days ahead to include (0 = today only, 1 = today + tomorrow)

    Returns:
        Dictionary with statistics about the filtering
    """
    print(f"Downloading XMLTV from {xmltv_url}...")
    print("This may take 30-60 seconds for a ~100MB file...")

    try:
        response = requests.get(xmltv_url, timeout=120)
        response.raise_for_status()
        print(f"Downloaded {len(response.content) / 1024 / 1024:.1f} MB")
    except requests.RequestException as e:
        print(f"Error downloading XMLTV: {e}")
        return {"error": str(e)}

    print("Parsing XML...")
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return {"error": str(e)}

    # Calculate date range (timezone-aware for CET/CEST)
    from datetime import timezone
    cet = timezone(timedelta(hours=1))  # CET baseline, XMLTV times include actual offset
    today = datetime.now(tz=cet).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=days_ahead + 1)

    print(f"Filtering programs from {today.date()} to {end_date.date()}...")

    filtered_programs = []
    total_programs = 0
    channels_found = set()

    for programme_elem in root.findall('programme'):
        total_programs += 1

        try:
            # Get channel
            xmltv_channel = programme_elem.get('channel', '')
            standard_channel = normalize_channel_name(xmltv_channel)

            if not standard_channel:
                continue  # Skip channels not in our list

            channels_found.add(standard_channel)

            # Parse times
            start_str = programme_elem.get('start')
            stop_str = programme_elem.get('stop')

            start_time = parse_xmltv_time(start_str)
            end_time = parse_xmltv_time(stop_str)

            if not start_time or not end_time:
                continue

            # Filter by date range
            if start_time < today or start_time >= end_date:
                continue

            # Extract program details
            title_elem = programme_elem.find('title')
            title = title_elem.text if title_elem is not None else ''

            desc_elem = programme_elem.find('desc')
            description = desc_elem.text if desc_elem is not None else None

            # Parse genres
            genres = []
            for category_elem in programme_elem.findall('category'):
                if category_elem.text:
                    genres.append(category_elem.text)

            # Calculate duration
            duration = int((end_time - start_time).total_seconds())

            program = {
                'title': title,
                'channel': standard_channel,
                'description': description,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': duration,
                'genres': genres
            }

            filtered_programs.append(program)

        except Exception as e:
            continue  # Skip problematic programs

    # Save to JSON
    from datetime import timezone
    output_data = {
        'generated_at': datetime.now(tz=timezone.utc).isoformat(),
        'channels': sorted(list(channels_found)),
        'program_count': len(filtered_programs),
        'date_range': {
            'start': today.isoformat(),
            'end': end_date.isoformat()
        },
        'programs': filtered_programs
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    file_size_mb = Path(output_path).stat().st_size / 1024 / 1024

    stats = {
        'total_programs_scanned': total_programs,
        'filtered_programs': len(filtered_programs),
        'channels_found': sorted(list(channels_found)),
        'output_file': output_path,
        'output_size_mb': round(file_size_mb, 2),
        'date_range': f"{today.date()} to {end_date.date()}"
    }

    print(f"\n✅ EPG filtering complete!")
    print(f"   Scanned: {stats['total_programs_scanned']:,} programs")
    print(f"   Filtered: {stats['filtered_programs']:,} programs")
    print(f"   Channels: {', '.join(stats['channels_found'])}")
    print(f"   File size: {stats['output_size_mb']} MB")
    print(f"   Saved to: {output_path}")

    return stats


if __name__ == "__main__":
    # For testing
    from app.config import config

    output_path = Path(__file__).parent.parent / 'data' / 'epg_filtered.json'

    stats = download_and_filter_epg(
        xmltv_url=config.XMLTV_EPG_URL,
        output_path=str(output_path),
        days_ahead=1
    )

    print(f"\nStats: {json.dumps(stats, indent=2)}")
