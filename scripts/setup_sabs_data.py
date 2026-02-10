"""Extract and set up SABS data for import."""
import sys
import zipfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_sabs_data(zip_path, extract_to='data/nces_zones'):
    """Extract SABS zip file and prepare for import."""
    zip_path = Path(zip_path)
    extract_dir = Path(extract_to)
    
    if not zip_path.exists():
        print(f"[ERROR] File not found: {zip_path}")
        return False
    
    print("=" * 60)
    print("Setting up NCES SABS Data")
    print("=" * 60)
    print(f"Source ZIP: {zip_path}")
    print(f"Extract to: {extract_dir}")
    print()
    
    # Create extraction directory
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already extracted
    existing_shp = list(extract_dir.glob("*.shp"))
    if existing_shp:
        print(f"[OK] Shapefiles already exist in {extract_dir}")
        print(f"   Found: {existing_shp[0].name}")
        print("\nYou can now run: python scripts/import_nces_zones.py")
        return True
    
    # Extract ZIP file
    print("Extracting ZIP file...")
    print("(This may take a few minutes - the file is large)")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            print(f"   Found {len(file_list)} files in ZIP")
            
            # Extract all files
            zip_ref.extractall(extract_dir)
            print(f"[OK] Extracted to: {extract_dir}")
        
        # Check for shapefiles (including in subdirectories)
        shapefiles = list(extract_dir.rglob("*.shp"))
        if shapefiles:
            print(f"\n[OK] Found {len(shapefiles)} shapefile(s):")
            for shp in shapefiles:
                print(f"   - {shp.name}")
            
            # Check for required companion files
            required_extensions = ['.shx', '.dbf']
            for shp in shapefiles:
                base_name = shp.stem
                shp_dir = shp.parent
                missing = []
                for ext in required_extensions:
                    companion_file = shp_dir / f"{base_name}{ext}"
                    if not companion_file.exists():
                        missing.append(ext)
                
                if missing:
                    print(f"   [WARNING] Missing companion files for {shp.name}: {', '.join(missing)}")
                else:
                    print(f"   [OK] All required files present for {shp.name}")
            
            # If shapefiles are in a subdirectory, note that
            if shapefiles[0].parent != extract_dir:
                print(f"\nNote: Shapefiles are in subdirectory: {shapefiles[0].parent.name}")
                print("The import script will find them automatically.")
            
            print("\n" + "=" * 60)
            print("Setup Complete!")
            print("=" * 60)
            print("\nNext step: Run the import script:")
            print("  python scripts/import_nces_zones.py")
            print("\nThis will:")
            print("  1. Convert shapefiles to GeoJSON")
            print("  2. Filter for NC and SC only")
            print("  3. Import into your Supabase database")
            return True
        else:
            print("\n[ERROR] No shapefiles found in extracted data")
            print("   Please check the ZIP file contents")
            return False
            
    except zipfile.BadZipFile:
        print(f"\n[ERROR] {zip_path} is not a valid ZIP file")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error extracting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    
    # Default path
    default_zip = Path.home() / "Downloads" / "SABS_1516.zip"
    
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
    else:
        zip_path = str(default_zip)
    
    success = setup_sabs_data(zip_path)
    
    if not success:
        print("\nUsage:")
        print(f"  python scripts/setup_sabs_data.py [path_to_SABS_1516.zip]")
        print(f"\nDefault location: {default_zip}")
        sys.exit(1)
