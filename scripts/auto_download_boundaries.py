"""
Automated FREE zip code boundary downloader.
Downloads from Census Bureau and processes them - 100% FREE.
"""
import requests
import zipfile
import json
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Check if geopandas is available (free library)
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("Note: geopandas not installed. Install with: pip install geopandas")

BOUNDARIES_DIR = Path('data/zip_boundaries')
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

def download_and_extract_zcta(zip_codes=None):
    """
    Download Census ZCTA shapefile and extract specific zip codes.
    
    Args:
        zip_codes: List of zip codes to extract. If None, extracts all.
    """
    print("=" * 70)
    print("FREE Census ZCTA Boundary Downloader")
    print("=" * 70)
    
    if not HAS_GEOPANDAS:
        print("\n[ERROR] geopandas is required for this script.")
        print("Install it with: pip install geopandas")
        print("\nAlternatively, use the manual method (see setup_free_boundaries.py)")
        return False
    
    # Census Bureau ZCTA shapefile URLs (try different years - all FREE)
    shapefile_urls = [
        "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA5/tl_2023_us_zcta520.zip",
        "https://www2.census.gov/geo/tiger/TIGER2022/ZCTA5/tl_2022_us_zcta520.zip",
        "https://www2.census.gov/geo/tiger/TIGER2021/ZCTA5/tl_2021_us_zcta520.zip",
    ]
    
    shapefile_url = None
    for url in shapefile_urls:
        # Test if URL exists
        test_response = requests.head(url, timeout=10)
        if test_response.status_code == 200:
            shapefile_url = url
            break
    
    if not shapefile_url:
        print("Could not find valid Census shapefile URL.")
        print("Please download manually from: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html")
        return False
    
    print(f"\nDownloading Census ZCTA shapefile...")
    print(f"URL: {shapefile_url}")
    print("This is a large file (~50MB) but completely FREE from US government.")
    print("Download may take 2-5 minutes...")
    
    try:
        # Download
        response = requests.get(shapefile_url, stream=True, timeout=600)
        if response.status_code != 200:
            print(f"Download failed: {response.status_code}")
            return False
        
        # Save to temp file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        total_size = 0
        
        for chunk in response.iter_content(chunk_size=8192):
            temp_zip.write(chunk)
            total_size += len(chunk)
            if total_size % (10 * 1024 * 1024) == 0:  # Print every 10MB
                print(f"Downloaded: {total_size / (1024*1024):.1f} MB...")
        
        temp_zip.close()
        print(f"Download complete: {total_size / (1024*1024):.1f} MB")
        
        # Extract
        print("\nExtracting shapefile...")
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the .shp file
        shp_file = None
        for file in Path(extract_dir).glob('*.shp'):
            shp_file = file
            break
        
        if not shp_file:
            print("Error: Could not find .shp file in downloaded zip")
            return False
        
        print(f"Found shapefile: {shp_file.name}")
        
        # Read with geopandas
        print("Reading shapefile...")
        gdf = gpd.read_file(str(shp_file))
        
        print(f"Found {len(gdf)} ZCTA boundaries")
        
        # Extract specific zip codes or all
        if zip_codes:
            gdf_filtered = gdf[gdf['ZCTA5CE10'].isin(zip_codes)]
            print(f"Filtering to {len(gdf_filtered)} requested zip codes...")
        else:
            gdf_filtered = gdf
            print("Processing all zip codes (this may take a while)...")
        
        # Save each as GeoJSON
        saved = 0
        for idx, row in gdf_filtered.iterrows():
            zip_code = row['ZCTA5CE10']
            
            # Convert to GeoJSON
            geojson = json.loads(gdf_filtered[[idx]].to_json())
            
            # Save
            output_file = BOUNDARIES_DIR / f"{zip_code}.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f)
            
            saved += 1
            if saved % 100 == 0:
                print(f"Saved {saved} boundaries...")
        
        print(f"\n[SUCCESS] Saved {saved} zip code boundaries to {BOUNDARIES_DIR}/")
        print("These are now available in your application!")
        
        # Cleanup
        os.unlink(temp_zip.name)
        shutil.rmtree(extract_dir)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nIf geopandas installation fails, use the manual method instead.")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        zip_codes = sys.argv[1:]
        print(f"Downloading boundaries for: {', '.join(zip_codes)}")
        download_and_extract_zcta(zip_codes)
    else:
        print("Usage: python auto_download_boundaries.py <zip1> <zip2> ...")
        print("Example: python auto_download_boundaries.py 28204 10001 90210")
        print("\nOr download all boundaries:")
        print("python auto_download_boundaries.py --all")
        print("\nNote: This requires: pip install geopandas")

