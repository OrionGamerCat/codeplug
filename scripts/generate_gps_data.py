#!/usr/bin/env python3
"""
Unified GPS Data Generator for Icom ID-52PLUS
Generates GPS format files for POTA parks and SOTA summits
Compatible with gpsexample.csv format
"""

import csv
import subprocess
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import time

try:
    import requests
except ImportError:
    print("Warning: requests module not available. POTA functionality will be limited.")
    print("Install with: apt install python3-requests")
    requests = None

def convert_umlauts(text):
    """Convert German, Slovak and special characters to ASCII equivalents."""
    if not text:
        return text
    
    umlaut_map = {
        'ä': 'ae', 'Ä': 'Ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue', 'Ü': 'Ue',
        'ß': 'ss', 'é': 'e', 'É': 'E', 'è': 'e', 'È': 'E',
        'á': 'a', 'Á': 'A', 'à': 'a', 'À': 'A', 'í': 'i', 'Í': 'I',
        'ì': 'i', 'Ì': 'I', 'ó': 'o', 'Ó': 'O', 'ò': 'o', 'Ò': 'O',
        'ú': 'u', 'Ú': 'U', 'ù': 'u', 'Ù': 'U', 'ñ': 'n', 'Ñ': 'N',
        'ç': 'c', 'Ç': 'C', '–': '-', '—': '-', '\"': '\"', '\"': '\"',
        ''': "'", ''': "'", '…': '...', 'ř': 'r', 'Ř': 'R',
        'ľ': 'l', 'Ľ': 'L', 'š': 's', 'Š': 'S', 'ť': 't', 'Ť': 'T',
        'ž': 'z', 'Ž': 'Z', 'ý': 'y', 'Ý': 'Y', 'č': 'c', 'Č': 'C',
        'ď': 'd', 'Ď': 'D', 'ň': 'n', 'Ň': 'N', 'ô': 'o', 'Ô': 'O'
    }
    
    result = text
    for umlaut, replacement in umlaut_map.items():
        result = result.replace(umlaut, replacement)
    
    return result

def maidenhead_to_gps(grid):
    """Convert Maidenhead grid square to GPS coordinates."""
    if not grid or len(grid) < 4:
        return None, None
    
    try:
        grid = grid.upper()
        
        # Get longitude from first two characters (A-R)
        lon = (ord(grid[0]) - ord('A')) * 20 - 180
        lon += (ord(grid[2]) - ord('0')) * 2
        
        # Get latitude from second two characters (A-R) 
        lat = (ord(grid[1]) - ord('A')) * 10 - 90
        lat += (ord(grid[3]) - ord('0')) * 1
        
        # Add subsquare precision if available
        if len(grid) >= 6:
            lon += (ord(grid[4]) - ord('A')) * (2.0/24.0)
            lat += (ord(grid[5]) - ord('A')) * (1.0/24.0)
        else:
            # Center of grid square
            lon += 1.0  # Half of 2 degree square
            lat += 0.5  # Half of 1 degree square
        
        return lat, lon
        
    except (ValueError, IndexError):
        return None, None

def find_memory_processor():
    """Find memory-channels-processor executable."""
    if subprocess.run(['which', 'memory-channels-processor'], capture_output=True).returncode == 0:
        return 'memory-channels-processor'
    elif Path('/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe').exists():
        return '/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe'
    else:
        print("Error: memory-channels-processor not found")
        print("Please install memory-channels-processor or ensure it's in your PATH")
        return None

def fetch_pota_locations():
    """Fetch POTA location data from API."""
    if requests is None:
        print("Error: requests module not available for POTA API access")
        return []
        
    try:
        print("Fetching POTA locations from API...")
        response = requests.get('https://api.pota.app/programs/locations', timeout=30)
        response.raise_for_status()
        
        locations_data = response.json()
        
        # Filter for our target countries - need to look inside entities/locations
        target_locations = []
        for program in locations_data:
            for entity in program.get('entities', []):
                for location in entity.get('locations', []):
                    descriptor = location.get('descriptor', '')
                    if descriptor.startswith(('AT-', 'SK-', 'SG-')):
                        target_locations.append(location)
        
        print(f"Found {len(target_locations)} POTA locations for target countries")
        return target_locations
        
    except Exception as e:
        print(f"Error fetching POTA locations: {e}")
        return []

def fetch_parks_for_location(descriptor, max_retries=3):
    """Fetch parks for a specific location with retry logic."""
    if requests is None:
        print(f"Error: requests module not available for {descriptor}")
        return []
        
    for attempt in range(max_retries):
        try:
            url = f"https://api.pota.app/location/parks/{descriptor}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            parks_data = response.json()
            print(f"  {descriptor}: {len(parks_data)} parks")
            return parks_data
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  {descriptor}: Retry {attempt + 1} after error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                print(f"  {descriptor}: Failed after {max_retries} attempts: {e}")
                return []
    
    return []

def generate_sota_data():
    """Generate SOTA summits data using memory-channels-processor."""
    memory_processor = find_memory_processor()
    if not memory_processor:
        return False
    
    print("Generating SOTA summits data...")
    
    try:
        result = subprocess.run([
            memory_processor,
            '--source', 'sota-summits',
            '--output-file', 'sota_summits.csv',
            '--country', 'AUT', 'SVK', 'SGP',
            '--output-format', 'csv'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("SOTA summits data generated successfully")
            return True
        else:
            print(f"Error generating SOTA data: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Timeout generating SOTA data")
        return False
    except Exception as e:
        print(f"Error running memory-channels-processor: {e}")
        return False

def create_pota_gps_files():
    """Create POTA parks GPS format files by country."""
    print("POTA Parks GPS Format Generator")
    print("=" * 60)
    
    # Group assignments
    group_map = {
        'AT': {'group': 'U', 'group_name': 'POTA-AT'},
        'SK': {'group': 'V', 'group_name': 'POTA-SK'},
        'SG': {'group': 'W', 'group_name': 'POTA-SG'}
    }
    
    # Create output directories
    Path('POTA-GPS').mkdir(exist_ok=True)
    Path('POTA-GPS/Austria').mkdir(exist_ok=True)
    Path('POTA-GPS/Slovakia').mkdir(exist_ok=True)
    Path('POTA-GPS/Singapore').mkdir(exist_ok=True)
    
    current_date = datetime.now().strftime('%m/%d/%Y')
    country_parks = {'AT': [], 'SK': [], 'SG': []}
    location_parks = {}
    country_totals = {}
    
    # Fetch POTA data
    locations = fetch_pota_locations()
    if not locations:
        print("Failed to fetch POTA location data")
        return 0
    
    # Process each location
    for location in locations:
        descriptor = location.get('descriptor', '')
        country_prefix = descriptor.split('-')[0]
        
        if country_prefix not in group_map:
            continue
        
        parks = fetch_parks_for_location(descriptor)
        location_parks[descriptor] = []
        
        for park in parks:
            try:
                park_ref = park.get('reference', '')
                name = park.get('name', '')
                grid = park.get('grid', '')
                
                if not park_ref or not name or not grid:
                    continue
                
                # Convert grid to GPS coordinates
                lat, lon = maidenhead_to_gps(grid)
                if lat is None or lon is None:
                    continue
                
                # Clean name for display
                clean_name = convert_umlauts(name)
                if len(clean_name) > 50:
                    clean_name = clean_name[:47] + "..."
                
                # Format park number (remove prefix and leading zeros)
                park_number = park_ref.split('-')[1].lstrip('0') if '-' in park_ref else park_ref
                
                group_info = group_map[country_prefix]
                
                gps_entry = {
                    'Group': group_info['group'],
                    'Group Name': group_info['group_name'],
                    'Name': f"{park_number} {clean_name}",
                    'Date': current_date,
                    'Time': '00:00:00',
                    'Latitude': lat,
                    'Longitude': lon,
                    'Altitude': '',
                    'Alarm': 'OFF'
                }
                
                country_parks[country_prefix].append(gps_entry)
                location_parks[descriptor].append(gps_entry)
                
            except Exception as e:
                print(f"Error processing park {park.get('reference', 'unknown')}: {e}")
                continue
    
    total_parks = 0
    
    # Write country files
    for country_code, parks in country_parks.items():
        if not parks:
            continue
            
        country_name = {'AT': 'Austria', 'SK': 'Slovakia', 'SG': 'Singapore'}[country_code]
        group_info = group_map[country_code]
        
        # Write country-wide file
        country_filename = f"POTA-GPS/pota_{country_code.lower()}_all.csv"
        write_gps_csv(country_filename, parks)
        
        country_totals[country_code] = {
            'name': country_name,
            'parks': len(parks),
            'group': group_info['group']
        }
        
        total_parks += len(parks)
        print(f"Created {country_name}: {len(parks)} parks (Group {group_info['group']})")
    
    # Write location-specific files
    for descriptor, parks in location_parks.items():
        if parks:
            country_name = {'AT': 'Austria', 'SK': 'Slovakia', 'SG': 'Singapore'}[descriptor.split('-')[0]]
            location_filename = f"POTA-GPS/{country_name}/{descriptor}.csv"
            write_gps_csv(location_filename, parks)
    
    # Create master combined file
    print("Creating master combined file...")
    all_parks = []
    for parks in country_parks.values():
        all_parks.extend(parks)
    
    if all_parks:
        write_gps_csv('POTA-GPS/pota_all_countries.csv', all_parks)
        print(f"Created master file with {len(all_parks)} parks")
    
    # Print summary
    print(f"\nSuccessfully processed {total_parks} POTA parks")
    for country_code, stats in country_totals.items():
        print(f"   {stats['name']}: {stats['parks']} parks (Group {stats['group']})")
    
    return total_parks

def create_sota_gps_files():
    """Create SOTA summits GPS format files by country."""
    print("SOTA Summits GPS Format Generator")
    print("=" * 60)
    
    # Group assignments compatible with POTA format
    group_map = {
        'AUT': {'group': 'X', 'group_name': 'SOTA-AT'},
        'SVK': {'group': 'Y', 'group_name': 'SOTA-SK'},
        'SGP': {'group': 'Z', 'group_name': 'SOTA-SG'}
    }
    
    # Check if SOTA data exists, generate if needed
    if not Path('sota_summits.csv').exists():
        print("SOTA data not found, generating...")
        if not generate_sota_data():
            print("Failed to generate SOTA data")
            return 0
    
    # Create output directories
    Path('SOTA-GPS').mkdir(exist_ok=True)
    Path('SOTA-GPS/Austria').mkdir(exist_ok=True)
    Path('SOTA-GPS/Slovakia').mkdir(exist_ok=True)
    Path('SOTA-GPS/Singapore').mkdir(exist_ok=True)
    
    current_date = datetime.now().strftime('%m/%d/%Y')
    country_summits = {'AUT': [], 'SVK': [], 'SGP': []}
    country_totals = {}
    
    # Read and process SOTA data
    try:
        with open('sota_summits.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                country_code = row.get('country_code', '').upper()
                if country_code not in group_map:
                    continue
                
                try:
                    name = row.get('name', '')
                    lat = float(row.get('lat', 0))
                    lon = float(row.get('long', 0))
                    
                    if not name or lat == 0 or lon == 0:
                        continue
                    
                    # Clean name for display
                    clean_name = convert_umlauts(name)
                    
                    # Format for GPS display (summit name, truncate if needed)
                    display_name = clean_name
                    if len(display_name) > 50:
                        display_name = display_name[:47] + "..."
                    
                    group_info = group_map[country_code]
                    
                    gps_entry = {
                        'Group': group_info['group'],
                        'Group Name': group_info['group_name'],
                        'Name': display_name,
                        'Date': current_date,
                        'Time': '00:00:00',
                        'Latitude': lat,
                        'Longitude': lon,
                        'Altitude': '',
                        'Alarm': 'OFF'
                    }
                    
                    country_summits[country_code].append(gps_entry)
                    
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid summit entry: {e}")
                    continue
                    
    except FileNotFoundError:
        print("Error: sota_summits.csv not found")
        return 0
    except Exception as e:
        print(f"Error reading SOTA data: {e}")
        return 0
    
    total_summits = 0
    
    # Write country files
    for country_code, summits in country_summits.items():
        if not summits:
            continue
            
        country_name = {'AUT': 'Austria', 'SVK': 'Slovakia', 'SGP': 'Singapore'}[country_code]
        group_info = group_map[country_code]
        
        # Write country-wide file
        country_filename = f"SOTA-GPS/sota_{country_code.lower()}_all.csv"
        write_gps_csv(country_filename, summits)
        
        # Create region-specific files (simplified - one file per country for SOTA)
        region_filename = f"SOTA-GPS/{country_name}/sota_{country_code.lower()}.csv"
        write_gps_csv(region_filename, summits)
        
        country_totals[country_code] = {
            'name': country_name,
            'summits': len(summits),
            'group': group_info['group']
        }
        
        total_summits += len(summits)
        print(f"Created {country_name}: {len(summits)} summits (Group {group_info['group']})")
    
    # Create master combined file
    print("Creating master combined file...")
    all_summits = []
    for summits in country_summits.values():
        all_summits.extend(summits)
    
    if all_summits:
        write_gps_csv('SOTA-GPS/sota_all_countries.csv', all_summits)
        print(f"Created master file with {len(all_summits)} summits")
    
    # Print summary
    print(f"\nSuccessfully processed {total_summits} SOTA summits")
    for country_code, stats in country_totals.items():
        print(f"   {stats['name']}: {stats['summits']} summits (Group {stats['group']})")
    
    return total_summits

def write_gps_csv(filename, gps_data):
    """Write GPS data in CSV format."""
    if not gps_data:
        return
    
    # GPS CSV header
    fieldnames = ['Group', 'Group Name', 'Name', 'Date', 'Time', 'Latitude', 'Longitude', 'Altitude', 'Alarm']
    
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in gps_data:
            writer.writerow(entry)

def main():
    parser = argparse.ArgumentParser(
        description='Unified GPS Data Generator for Icom ID-52PLUS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_gps_data.py --pota                # Generate POTA parks only
  python3 generate_gps_data.py --sota                # Generate SOTA summits only
  python3 generate_gps_data.py --pota --sota         # Generate both POTA and SOTA
  python3 generate_gps_data.py --all                 # Generate all GPS data
        """
    )
    
    parser.add_argument('--pota', action='store_true',
                       help='Generate POTA parks GPS data')
    parser.add_argument('--sota', action='store_true', 
                       help='Generate SOTA summits GPS data')
    parser.add_argument('--all', action='store_true',
                       help='Generate all GPS data (POTA and SOTA)')
    parser.add_argument('--countries', nargs='+', choices=['AT', 'SK', 'SG'],
                       help='Limit generation to specific countries')
    
    args = parser.parse_args()
    
    # If no specific flags, show help
    if not any([args.pota, args.sota, args.all]):
        parser.print_help()
        return
    
    # Set flags for --all
    if args.all:
        args.pota = True
        args.sota = True
    
    print("Unified GPS Data Generator for Icom ID-52PLUS")
    print("=" * 70)
    
    total_generated = 0
    
    # Generate POTA data
    if args.pota:
        pota_count = create_pota_gps_files()
        total_generated += pota_count
        print()
    
    # Generate SOTA data
    if args.sota:
        sota_count = create_sota_gps_files()
        total_generated += sota_count
        print()
    
    if total_generated > 0:
        print(f"Successfully generated {total_generated} GPS waypoints")
        print("\nGPS Format Features:")
        print("- gpsexample.csv compatible format")
        print("- Group letters: U/V/W (POTA), X/Y/Z (SOTA)")
        print("- ASCII-converted names for radio display")
        print("- Current date timestamps")
        print("- Precise GPS coordinates")
        print("\nUsage with Icom ID-52PLUS:")
        print("1. Import individual country files for specific areas")
        print("2. Or import master files for complete datasets")
        print("3. Groups are designed to complement each other")
        print("\nPerfect for amateur radio activations and navigation!")
        
    else:
        print("No GPS data generated")

if __name__ == "__main__":
    main()