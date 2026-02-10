"""Client for getting zoned schools from GreatSchools website."""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple
import re
import time

class GreatSchoolsClient:
    """Client for scraping zoned schools from GreatSchools website."""
    
    BASE_URL = "https://www.greatschools.org"
    
    def __init__(self):
        """Initialize GreatSchools client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_zoned_schools_by_address(self, address: str, lat: float, lng: float) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Get zoned schools (elementary, middle, high) for an address from GreatSchools.
        
        Args:
            address: The address string
            lat: Latitude of the address
            lng: Longitude of the address
            
        Returns:
            Tuple of (elementary_school, middle_school, high_school) dictionaries
            Each dict contains: {'name': str, 'rating': Optional[int], 'address': Optional[str]}
        """
        try:
            # GreatSchools uses lat/lng in their URL structure
            # Try to find the address page
            # Format: https://www.greatschools.org/north-carolina/charlotte/schools/?view=table&lat=35.2271&lon=-80.8431
            
            # Extract city and state from address if possible
            state = self._extract_state(address)
            city = self._extract_city(address)
            
            # Build URL - GreatSchools uses lat/lng in query params
            url = f"{self.BASE_URL}/schools/search.page"
            params = {
                'q': address,
                'lat': lat,
                'lon': lng
            }
            
            # Alternative: Try direct address search
            search_url = f"{self.BASE_URL}/schools/search.page"
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"[DEBUG] GreatSchools search returned status {response.status_code}")
                return None, None, None
            
            # Parse the page to find zoned schools
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # GreatSchools displays zoned schools in a specific section
            # Look for "Assigned Schools" or "Zoned Schools" section
            zoned_schools = self._parse_zoned_schools(soup, lat, lng)
            
            if not zoned_schools:
                # Try alternative method: search by coordinates
                zoned_schools = self._get_schools_by_coordinates(lat, lng)
            
            if not zoned_schools:
                return None, None, None
            
            # Extract elementary, middle, high
            elementary = zoned_schools.get('elementary')
            middle = zoned_schools.get('middle')
            high = zoned_schools.get('high')
            
            return elementary, middle, high
            
        except Exception as e:
            print(f"[DEBUG] Error getting zoned schools from GreatSchools: {e}")
            return None, None, None
    
    def _parse_zoned_schools(self, soup: BeautifulSoup, lat: float, lng: float) -> Dict[str, Optional[Dict]]:
        """Parse zoned schools from GreatSchools HTML."""
        zoned_schools = {
            'elementary': None,
            'middle': None,
            'high': None
        }
        
        try:
            # Look for school cards or listings
            # GreatSchools structure may vary, try multiple selectors
            
            # Method 1: Look for "Assigned Schools" section
            assigned_section = soup.find('div', class_=re.compile(r'assigned|zoned', re.I))
            if assigned_section:
                schools = assigned_section.find_all('div', class_=re.compile(r'school|card', re.I))
                for school in schools:
                    school_info = self._extract_school_info(school)
                    if school_info:
                        level = school_info.get('level', '').lower()
                        if 'elementary' in level:
                            zoned_schools['elementary'] = school_info
                        elif 'middle' in level:
                            zoned_schools['middle'] = school_info
                        elif 'high' in level:
                            zoned_schools['high'] = school_info
            
            # Method 2: Look for school listings with "Assigned" or "Zoned" label
            school_listings = soup.find_all('div', class_=re.compile(r'school.*listing|school.*card', re.I))
            for listing in school_listings:
                # Check if it's marked as assigned/zoned
                assigned_label = listing.find(text=re.compile(r'assigned|zoned', re.I))
                if assigned_label:
                    school_info = self._extract_school_info(listing)
                    if school_info:
                        level = school_info.get('level', '').lower()
                        if 'elementary' in level:
                            zoned_schools['elementary'] = school_info
                        elif 'middle' in level:
                            zoned_schools['middle'] = school_info
                        elif 'high' in level:
                            zoned_schools['high'] = school_info
            
        except Exception as e:
            print(f"[DEBUG] Error parsing zoned schools: {e}")
        
        return zoned_schools
    
    def _extract_school_info(self, element) -> Optional[Dict]:
        """Extract school information from HTML element."""
        try:
            school_info = {}
            
            # Extract school name
            name_elem = element.find('a', class_=re.compile(r'name|title', re.I))
            if not name_elem:
                name_elem = element.find('h2') or element.find('h3')
            if name_elem:
                school_info['name'] = name_elem.get_text(strip=True)
            
            # Extract rating
            rating_elem = element.find('span', class_=re.compile(r'rating|score', re.I))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Extract number from rating (e.g., "8" from "8/10")
                rating_match = re.search(r'(\d+)', rating_text)
                if rating_match:
                    school_info['rating'] = int(rating_match.group(1))
            
            # Extract level
            level_elem = element.find('span', class_=re.compile(r'level|type|grade', re.I))
            if level_elem:
                school_info['level'] = level_elem.get_text(strip=True)
            
            # Extract address
            address_elem = element.find('div', class_=re.compile(r'address|location', re.I))
            if address_elem:
                school_info['address'] = address_elem.get_text(strip=True)
            
            return school_info if school_info.get('name') else None
            
        except Exception as e:
            print(f"[DEBUG] Error extracting school info: {e}")
            return None
    
    def _get_schools_by_coordinates(self, lat: float, lng: float) -> Dict[str, Optional[Dict]]:
        """Alternative method: Get schools by coordinates using GreatSchools API-like endpoint."""
        # This is a fallback - GreatSchools may have an API endpoint we can use
        # For now, return empty - we'll rely on web scraping
        return {'elementary': None, 'middle': None, 'high': None}
    
    def _extract_state(self, address: str) -> Optional[str]:
        """Extract state abbreviation from address."""
        state_match = re.search(r'\b([A-Z]{2})\b', address.upper())
        if state_match:
            return state_match.group(1)
        return None
    
    def _extract_city(self, address: str) -> Optional[str]:
        """Extract city name from address."""
        # Simple extraction - look for text before state/zip
        parts = address.split(',')
        if len(parts) >= 2:
            return parts[-2].strip()
        return None
