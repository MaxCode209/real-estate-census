"""Apify API client for Zillow School Scraper."""
import requests
import time
from typing import Dict, List, Optional, Tuple
from config.config import Config


class ApifySchoolClient:
    """Client for interacting with Apify Zillow School Scraper API."""
    
    BASE_URL = "https://api.apify.com/v2"
    ACTOR_ID = "axlymxp~zillow-school-scraper"  # Format: username~actorName
    
    def __init__(self, api_token: str = None):
        """Initialize Apify client."""
        self.api_token = api_token or Config.APIFY_API_TOKEN
        if not self.api_token:
            raise ValueError("Apify API token is required")
    
    def get_schools_by_bounds(
        self,
        north_lat: float,
        south_lat: float,
        east_lng: float,
        west_lng: float,
        min_rating: int = 1,
        include_elementary: bool = True,
        include_middle: bool = True,
        include_high: bool = True,
        include_public: bool = True,
        include_private: bool = False,
        include_charter: bool = True,
        include_unrated: bool = False
    ) -> List[Dict]:
        """
        Get schools within geographic boundaries using Apify Zillow School Scraper.
        
        Args:
            north_lat: Northern boundary latitude
            south_lat: Southern boundary latitude
            east_lng: Eastern boundary longitude
            west_lng: Western boundary longitude
            min_rating: Minimum school rating (1-10)
            include_elementary: Include elementary schools
            include_middle: Include middle schools
            include_high: Include high schools
            include_public: Include public schools
            include_private: Include private schools
            include_charter: Include charter schools
            include_unrated: Include unrated schools
            
        Returns:
            List of school dictionaries with ratings and details
        """
        # Prepare input for Apify actor
        # Note: The API expects longitude/latitude as STRINGS, not numbers!
        input_data = {
            "eastLongitude": str(east_lng),
            "westLongitude": str(west_lng),
            "northLatitude": str(north_lat),
            "southLatitude": str(south_lat),
            "minRating": int(min_rating),
            "includeElementary": bool(include_elementary),
            "includeMiddle": bool(include_middle),
            "includeHigh": bool(include_high),
            "includePublic": bool(include_public),
            "includePrivate": bool(include_private),
            "includeCharter": bool(include_charter),
            "includeUnrated": bool(include_unrated)
        }
        
        print(f"DEBUG: Apify input data: {input_data}")
        
        # Start the actor run
        run_response = self._start_actor_run(input_data)
        if not run_response:
            return []
        
        # Apify API returns data in 'data' key, or directly as 'id'
        run_id = None
        if 'data' in run_response and 'id' in run_response['data']:
            run_id = run_response['data']['id']
        elif 'id' in run_response:
            run_id = run_response['id']
        
        if not run_id:
            print(f"Could not extract run ID from response: {run_response}")
            return []
        
        # Wait for the run to complete and get results
        return self._wait_for_results(run_id)
    
    def _start_actor_run(self, input_data: Dict) -> Optional[Dict]:
        """Start an Apify actor run."""
        # Try both formats: username~actorName and username/actorName
        actor_ids_to_try = [
            "axlymxp~zillow-school-scraper",  # Tilde format
            "axlymxp/zillow-school-scraper",   # Slash format
        ]
        
        for actor_id in actor_ids_to_try:
            url = f"{self.BASE_URL}/acts/{actor_id}/runs"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # Also add token as query parameter (some Apify endpoints require it)
            url_with_token = f"{url}?token={self.api_token}"
            
            try:
                print(f"DEBUG: Trying actor ID: {actor_id}")
                print(f"DEBUG: URL: {url_with_token}")
                print(f"DEBUG: Input data: {input_data}")
                response = requests.post(url_with_token, json=input_data, headers=headers, timeout=30)
                
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response headers: {dict(response.headers)}")
                
                if response.status_code in [200, 201]:  # 201 = Created (run started)
                    print(f"DEBUG: Success with actor ID: {actor_id}")
                    return response.json()
                elif response.status_code == 400:
                    # Try to get error details
                    try:
                        error_data = response.json()
                        print(f"DEBUG: 400 Error details: {error_data}")
                    except:
                        print(f"DEBUG: 400 Error text: {response.text[:500]}")
                    # Try next format only if this one failed
                    if actor_id != actor_ids_to_try[-1]:
                        continue
                    else:
                        return None
                else:
                    print(f"DEBUG: Response status {response.status_code}, text: {response.text[:500]}")
                    # Only try next format if not the last one
                    if actor_id != actor_ids_to_try[-1]:
                        continue
                    else:
                        response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                print(f"DEBUG: Exception with {actor_id}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        print(f"DEBUG: Error response: {e.response.json()}")
                    except:
                        print(f"DEBUG: Error response text: {e.response.text[:500]}")
                # Only try next format if not the last one
                if actor_id != actor_ids_to_try[-1]:
                    continue
                else:
                    print(f"Error starting Apify actor run: {e}")
                    return None
        
        return None
    
    def _wait_for_results(self, run_id: str, max_wait: int = 300, poll_interval: int = 5) -> List[Dict]:
        """Wait for actor run to complete and fetch results."""
        url = f"{self.BASE_URL}/actor-runs/{run_id}?token={self.api_token}"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Check run status
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                run_data = response.json().get('data', {})
                status = run_data.get('status')
                
                if status == 'SUCCEEDED':
                    # Fetch results
                    return self._fetch_results(run_id)
                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                    print(f"Actor run {run_id} failed with status: {status}")
                    return []
                
                # Still running, wait and check again
                time.sleep(poll_interval)
                
            except requests.exceptions.RequestException as e:
                print(f"Error checking actor run status: {e}")
                return []
        
        print(f"Actor run {run_id} timed out after {max_wait} seconds")
        return []
    
    def _fetch_results(self, run_id: str) -> List[Dict]:
        """Fetch results from completed actor run."""
        url = f"{self.BASE_URL}/actor-runs/{run_id}/dataset/items?token={self.api_token}"
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching actor results: {e}")
            return []
    
    def get_schools_by_address(
        self,
        address: str,
        lat: float,
        lng: float,
        radius_miles: float = 2.0
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Get school names (elementary, middle, high) for an address.
        
        LIMITATION: The Apify actor only accepts a bounding box, not an address.
        It returns ALL schools in that area—not "the 3 zoned schools" for this
        address. So we build a box around (lat, lng) and pick the CLOSEST school
        of each level. Zoned schools are not always the closest; this is a proxy.
        See APIFY_WHY_BOUNDS_AND_CLOSEST.md for details.
        
        Args:
            address: The address string (unused by actor; we use lat/lng for box)
            lat: Latitude of the address
            lng: Longitude of the address
            radius_miles: Box radius in miles (default 2 miles)
            
        Returns:
            Tuple of (elementary_school, middle_school, high_school) dictionaries
        """
        # Actor has no "address" input—only bounding box. Build box around address.
        # Approximate: 1 degree latitude ≈ 69 miles
        # Longitude varies by latitude, but we'll use a simple approximation
        lat_offset = radius_miles / 69.0
        lng_offset = radius_miles / (69.0 * abs(lat / 90.0) if lat != 0 else 69.0)
        
        north_lat = lat + lat_offset
        south_lat = lat - lat_offset
        east_lng = lng + lng_offset
        west_lng = lng - lng_offset
        
        print(f"[ZONED SCHOOLS / Apify] get_schools_by_address: address={address!r}, box radius={radius_miles} mi")
        print(f"[ZONED SCHOOLS / Apify] Bounding box: N={north_lat:.4f} S={south_lat:.4f} E={east_lng:.4f} W={west_lng:.4f}")
        
        # Get all schools in the area
        schools = self.get_schools_by_bounds(
            north_lat=north_lat,
            south_lat=south_lat,
            east_lng=east_lng,
            west_lng=west_lng,
            min_rating=1,
            include_elementary=True,
            include_middle=True,
            include_high=True,
            include_public=True,
            include_private=False,
            include_charter=True,
            include_unrated=False
        )
        
        if not schools:
            print("[ZONED SCHOOLS / Apify] get_schools_by_address: No schools returned from Apify in this box.")
            return None, None, None
        
        print(f"[ZONED SCHOOLS / Apify] get_schools_by_address: Got {len(schools)} schools in box; picking CLOSEST to (lat={lat}, lng={lng}) per level.")
        
        # Find closest schools of each type
        elementary = self._find_closest_school(schools, 'elementary', lat, lng)
        middle = self._find_closest_school(schools, 'middle', lat, lng)
        high = self._find_closest_school(schools, 'high', lat, lng)
        
        def _name(s):
            if not s:
                return None
            return s.get('name') or s.get('schoolName') or s.get('title') or '(no name)'
        print(f"[ZONED SCHOOLS / Apify] CLOSEST selection: elementary={_name(elementary)!r}, middle={_name(middle)!r}, high={_name(high)!r}")
        
        return elementary, middle, high
    
    def _find_closest_school(
        self,
        schools: List[Dict],
        school_level: str,
        target_lat: float,
        target_lng: float
    ) -> Optional[Dict]:
        """Find the closest school of a specific level."""
        if not schools:
            print(f"DEBUG: No schools provided for level {school_level}")
            return None
        
        print(f"DEBUG: Looking for {school_level} schools. Total schools: {len(schools)}")
        print(f"DEBUG: First school sample: {schools[0] if schools else 'None'}")
        
        # Filter schools by level - try multiple possible field names
        level_key = school_level.lower()
        filtered = []
        
        for s in schools:
            # Try different possible field names for level
            # Apify returns 'schoolLevels' as an array like ['high'] or ['elementary', 'middle']
            level_value = None
            
            # First try 'schoolLevels' (array) - this is what Apify actually returns
            if 'schoolLevels' in s:
                school_levels = s['schoolLevels']
                if isinstance(school_levels, list):
                    # Check if our target level is in the array
                    for sl in school_levels:
                        if level_key in str(sl).lower():
                            filtered.append(s)
                            break
                    continue
                else:
                    level_value = str(school_levels).lower()
            
            # Fallback to other field names
            if not level_value:
                for key in ['level', 'schoolLevel', 'type', 'schoolType', 'gradeLevel']:
                    if key in s:
                        level_value = str(s[key]).lower()
                        break
            
            if level_value and (level_value == level_key or level_key in level_value):
                filtered.append(s)
        
        if not filtered:
            print(f"DEBUG: No {school_level} schools found after filtering")
            return None
        
        print(f"DEBUG: Found {len(filtered)} {school_level} schools")
        
        # Find closest by distance
        closest = None
        min_distance = float('inf')
        
        for school in filtered:
            # Try different possible field names for coordinates
            school_lat = None
            school_lng = None
            
            for lat_key in ['latitude', 'lat', 'y', 'coordY']:
                if lat_key in school:
                    try:
                        school_lat = float(school[lat_key])
                        break
                    except (ValueError, TypeError):
                        continue
            
            for lng_key in ['longitude', 'lng', 'lon', 'x', 'coordX']:
                if lng_key in school:
                    try:
                        school_lng = float(school[lng_key])
                        break
                    except (ValueError, TypeError):
                        continue
            
            if school_lat is None or school_lng is None:
                print(f"DEBUG: School missing coordinates: {school}")
                continue
            
            # Calculate simple distance (Haversine would be more accurate but this works)
            distance = ((school_lat - target_lat) ** 2 + (school_lng - target_lng) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest = school
        
        if closest:
            print(f"DEBUG: Closest {school_level} school: {closest}")
        else:
            print(f"DEBUG: No closest {school_level} school found (all missing coordinates)")
        
        return closest
