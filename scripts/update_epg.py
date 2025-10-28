#!/usr/bin/env python3
"""
Manual EPG update script.

Usage:
    python scripts/update_epg.py

Can be run via cron:
    0 6 * * * cd /path/to/tv_rec && python scripts/update_epg.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.epg_filter import download_and_filter_epg
from app.config import config
import json


def main():
    """Update EPG data."""
    print("=" * 60)
    print("EPG Update Script")
    print("=" * 60)

    output_path = Path(__file__).parent.parent / 'app' / 'data' / 'epg_filtered.json'

    print(f"\nOutput: {output_path}")
    print(f"Source: {config.XMLTV_EPG_URL}")
    print()

    stats = download_and_filter_epg(
        xmltv_url=config.XMLTV_EPG_URL,
        output_path=str(output_path),
        days_ahead=1
    )

    if 'error' in stats:
        print(f"\n❌ Update failed: {stats['error']}")
        return 1

    print("\n" + "=" * 60)
    print("Update Summary")
    print("=" * 60)
    print(json.dumps(stats, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
