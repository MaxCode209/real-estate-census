"""Service for fetching zip code boundary polygons."""
import requests
from typing import Optional, Dict, List
import json

class ZipCodeBoundaryService:
    """Service to fetch zip code boundary polygons."""
    
    # Using a public GeoJSON service for zip code boundaries
    # Alternative: Use Census Bureau TIGER/Line shapefiles
    GEOJSON_BASE_URL = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master"
    
    def __init__(self):
        self.cache = {}  # Cache for fetched boundaries
    
    def get_zip_boundary(self, zip_code: str) -> Optional[Dict]:
        """
        Get GeoJSON boundary for a zip code.
        
        Args:
            zip_code: 5-digit zip code
            
        Returns:
            GeoJSON feature or None
        """
        if zip_code in self.cache:
            return self.cache[zip_code]
        
        # Try multiple approaches to get zip code boundaries
        boundary = None
        
        # Approach 1: Try using a public API/service
        boundary = self._fetch_from_public_api(zip_code)
        
        if not boundary:
            # Approach 2: Try Census Bureau ZCTA boundaries
            boundary = self._fetch_from_census(zip_code)
        
        if boundary:
            self.cache[zip_code] = boundary
        
        return boundary
    
    def _fetch_from_public_api(self, zip_code: str) -> Optional[Dict]:
        """Fetch from a public zip code boundary API."""
        try:
            # Using Zippopotam.us style approach or similar
            # For actual boundaries, we'd need a service that provides GeoJSON
            # Let's try using a known zip code boundary service
            
            # Option: Use a service like boundaries-io or similar
            # For now, return None to use Census approach
            return None
        except Exception as e:
            print(f"Error fetching from public API: {e}")
            return None
    
    def _fetch_from_census(self, zip_code: str) -> Optional[Dict]:
        """Fetch ZCTA boundaries from Census Bureau."""
        try:
            # Census Bureau provides ZCTA (Zip Code Tabulation Area) boundaries
            # These are available as shapefiles that can be converted to GeoJSON
            # For now, we'll use a simplified approach
            
            # Note: Full implementation would require:
            # 1. Downloading Census TIGER/Line shapefiles
            # 2. Converting to GeoJSON
            # 3. Serving via API
            
            # For immediate use, we can use a CDN or pre-processed data
            return None
        except Exception as e:
            print(f"Error fetching from Census: {e}")
            return None
    
    def get_boundary_from_geojson_url(self, url: str) -> Optional[Dict]:
        """Fetch GeoJSON from a URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching GeoJSON: {e}")
        return None

