"""
Call /api/schools/address and print the result plus school_source (apify vs distance_fallback).

Usage (with app running on port 5000):
  python scripts/test_school_lookup_source.py "123 Main St, Charlotte, NC 28204"
  python scripts/test_school_lookup_source.py "123 Main St, Charlotte, NC 28204" 35.2271 -80.8431
"""
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = "http://localhost:5000/api/schools/address"
VERSION_URL = "http://localhost:5000/api/version"


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_school_lookup_source.py \"<address>\" [lat lng]")
        sys.exit(1)
    address = sys.argv[1]
    lat = lng = None
    if len(sys.argv) >= 4:
        try:
            lat = float(sys.argv[2])
            lng = float(sys.argv[3])
        except ValueError:
            pass
    params = {"address": address}
    if lat is not None and lng is not None:
        params["lat"] = lat
        params["lng"] = lng

    print("Request:", BASE)
    print("  address:", address)
    if lat is not None:
        print("  lat, lng:", lat, lng)
    print()

    try:
        ver = requests.get(VERSION_URL, timeout=5)
        if ver.ok and ver.json().get("school_source_in_schools_address"):
            print("(API version OK: server has school_source support)")
        else:
            print("WARNING: Server may not have updated code. Restart Flask (Ctrl+C then python -u app.py) and try again.")
        print()
    except Exception:
        pass

    try:
        r = requests.get(BASE, params=params, timeout=120)
        data = r.json()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect. Is the app running? (python -u app.py)")
        sys.exit(1)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

    if not r.ok:
        print("API error:", r.status_code)
        print(data.get("error", data))
        sys.exit(1)

    source = data.get("school_source", "unknown")
    print("=" * 60)
    print("SCHOOL SOURCE (what produced the schools below):", source.upper())
    print("=" * 60)
    if source == "apify":
        print("  Apify 2-mile box -> CLOSEST per level -> matched to school_data (legacy; no longer used for this endpoint).")
    elif source == "distance_fallback":
        print("  Nearest schools in school_data within ~5 miles (only source for address lookup now).")
    print()
    print("Elementary:", data.get("elementary_school_name") or "—", "| Rating:", data.get("elementary_school_rating"))
    print("Middle:    ", data.get("middle_school_name") or "—", "| Rating:", data.get("middle_school_rating"))
    print("High:      ", data.get("high_school_name") or "—", "| Rating:", data.get("high_school_rating"))
    print("Blended:   ", data.get("blended_school_score"))
    print()
    print("Full response keys:", list(data.keys()))


if __name__ == "__main__":
    main()
