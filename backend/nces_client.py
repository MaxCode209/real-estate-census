"""NCES EDGE API client for looking up public school addresses by name."""
import re
from typing import Optional, List, Dict

import requests

# NCES EDGE - Public school locations with address, zip, lat/lng (free, no API key)
NCES_QUERY_URL = "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_1920/MapServer/0/query"


def search_school_by_name(
    school_name: str,
    level: str,
    states: List[str] = None,
) -> Optional[Dict]:
    """
    Search NCES for a school by name. Returns first good match with address, zip, lat, lng.

    NCES has public schools only; charters may be included. Private schools not in NCES.

    Args:
        school_name: e.g. "Lincoln Elementary" or "Lincoln Elementary School"
        level: "elementary", "middle", or "high" - used to prefer matching school types
        states: e.g. ["NC", "SC"] - restrict search to these states

    Returns:
        Dict with address, zip_code, latitude, longitude, or None if not found
    """
    if not school_name or not str(school_name).strip():
        return None

    states = states or ["NC", "SC"]
    name_clean = str(school_name).strip()

    # Build search term - use core name, NCES might abbreviate "Elementary" -> "Elem"
    search_term = re.sub(r"\s+(Elementary|Middle|High|School|Academy)\s*$", "", name_clean, flags=re.I)
    if not search_term:
        search_term = name_clean[:40]  # NCES NAME field is 60 chars

    # Escape single quotes for ArcGIS WHERE
    safe_term = search_term.replace("'", "''")
    # For LIKE: %term% - need to escape % and _ if present
    like_val = f"%{safe_term}%"

    state_clause = " OR ".join(f"STATE='{s}'" for s in states)
    where = f"({state_clause}) AND NAME LIKE '{like_val}'"

    try:
        r = requests.get(
            NCES_QUERY_URL,
            params={
                "where": where,
                "outFields": "NAME,STREET,CITY,STATE,ZIP,LAT,LON",
                "returnGeometry": "false",
                "f": "json",
                "resultRecordCount": 25,
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        features = data.get("features") or []
        if not features:
            return None

        # Prefer matches that align with level (elementary/middle/high in name)
        level_hints = {
            "elementary": ["elementary", "elem", "primary"],
            "middle": ["middle", "jr", "junior", "intermediate"],
            "high": ["high", "senior", "sr", "academy"],
        }
        hints = level_hints.get(level.lower(), [])

        def score_match(attrs: dict) -> tuple:
            name = (attrs.get("NAME") or "").upper()
            # Prefer exact or close name match
            name_match = 1 if search_term.upper() in name else 0
            # Prefer level hint in NCES name
            level_match = 1 if any(h in name for h in [x.upper() for x in hints]) else 0
            return (level_match, name_match)

        features.sort(key=lambda f: score_match(f.get("attributes", {})), reverse=True)
        best = features[0].get("attributes", {})

        street = (best.get("STREET") or "").strip()
        city = (best.get("CITY") or "").strip()
        state = (best.get("STATE") or "").strip()
        zip_code = (best.get("ZIP") or "").strip()[:5]
        lat = best.get("LAT")
        lon = best.get("LON")

        if not street and not city:
            return None

        parts = [p for p in [street, city, f"{state} {zip_code}".strip()] if p]
        address = ", ".join(parts)

        return {
            "address": address,
            "city": city or None,
            "state": state or None,
            "zip_code": zip_code or None,
            "latitude": float(lat) if lat is not None else None,
            "longitude": float(lon) if lon is not None else None,
            "nces_name": best.get("NAME"),
        }
    except Exception as e:
        return None
