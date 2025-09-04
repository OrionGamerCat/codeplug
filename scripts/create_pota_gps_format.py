#!/usr/bin/env python3
"""
POTA Parks GPS Format Generator
Creates GPS format files like gpsexample.csv with groups U (Austria), V (Slovakia), W (Singapore)
Generates separate files for each location (AT-NO, AT-WI, SK-BC, etc.)
"""

import json
import csv
import subprocess
import time
from pathlib import Path
import sys
from datetime import datetime

def convert_umlauts(text):
    """Convert umlauts and special characters to ASCII equivalents."""
    if not text:
        return text
    
    umlaut_map = {
        'ä': 'ae', 'Ä': 'Ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue', 'Ü': 'Ue',
        'ß': 'ss', 'é': 'e', 'É': 'E', 'è': 'e', 'È': 'E',
        'á': 'a', 'Á': 'A', 'à': 'a', 'À': 'A', 'í': 'i', 'Í': 'I',
        'ì': 'i', 'Ì': 'I', 'ó': 'o', 'Ó': 'O', 'ò': 'o', 'Ò': 'O',
        'ú': 'u', 'Ú': 'U', 'ù': 'u', 'Ù': 'U', 'ñ': 'n', 'Ñ': 'N',
        'ç': 'c', 'Ç': 'C', '–': '-', '—': '-', '"': '"', '"': '"',
        ''': "'", ''': "'", '…': '...', 'ř': 'r', 'Ř': 'R',
        'ľ': 'l', 'Ľ': 'L', 'š': 's', 'Š': 'S', 'ť': 't', 'Ť': 'T',
        'ž': 'z', 'Ž': 'Z', 'ý': 'y', 'Ý': 'Y', 'č': 'c', 'Č': 'C',
        'ď': 'd', 'Ď': 'D', 'ň': 'n', 'Ň': 'N', 'ô': 'o', 'Ô': 'O'
    }
    
    result = text
    for umlaut, replacement in umlaut_map.items():
        result = result.replace(umlaut, replacement)
    
    return result

def fetch_pota_locations():
    """Fetch POTA program locations to get descriptors for countries."""
    try:
        print("📡 Fetching POTA program locations...")
        result = subprocess.run(
            ['curl', '-s', 'https://api.pota.app/programs/locations'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"❌ Error fetching locations: {result.stderr}")
            return {}
        
        data = json.loads(result.stdout)
        
        # Extract location descriptors for target countries
        countries = {}
        target_prefixes = {'AT', 'SK', 'SG'}
        
        for program in data:
            prefix = program.get('prefix', '')
            if prefix in target_prefixes:
                country_name = program.get('name', '')
                countries[prefix] = {
                    'name': country_name,
                    'locations': []
                }
                
                for entity in program.get('entities', []):
                    for location in entity.get('locations', []):
                        descriptor = location.get('descriptor', '')
                        loc_name = location.get('name', '')
                        parks_count = location.get('parks', 0)
                        
                        if parks_count > 0:  # Only include locations with parks
                            countries[prefix]['locations'].append({
                                'descriptor': descriptor,
                                'name': loc_name,
                                'parks': parks_count
                            })
        
        return countries
        
    except Exception as e:
        print(f"❌ Error processing locations data: {e}")
        return {}

def fetch_parks_for_location(descriptor):
    """Fetch all parks for a specific location descriptor."""
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://api.pota.app/location/parks/{descriptor}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return []
        
        parks_data = json.loads(result.stdout)
        return parks_data
        
    except Exception as e:
        print(f"❌ Error fetching parks for {descriptor}: {e}")
        return []

def create_pota_gps_files():
    """Create POTA parks GPS format files by country and location."""
    
    print("🏞️ POTA Parks GPS Format Generator")
    print("=" * 60)
    
    # Group assignments
    group_map = {
        'AT': {'group': 'U', 'group_name': 'POTA-AT'},
        'SK': {'group': 'V', 'group_name': 'POTA-SK'},
        'SG': {'group': 'W', 'group_name': 'POTA-SG'}
    }
    
    # Get location descriptors
    countries = fetch_pota_locations()
    if not countries:
        print("❌ Failed to fetch country locations")
        return 0
    
    # Create output directories
    Path('POTA-GPS').mkdir(exist_ok=True)
    Path('POTA-GPS/Austria').mkdir(exist_ok=True)
    Path('POTA-GPS/Slovakia').mkdir(exist_ok=True)
    Path('POTA-GPS/Singapore').mkdir(exist_ok=True)
    
    country_totals = {}
    current_date = datetime.now().strftime('%m/%d/%Y')
    
    # Process each country
    for country_code, country_info in countries.items():
        country_name = country_info['name']
        locations = country_info['locations']
        group_info = group_map[country_code]
        
        print(f"\n🏞️ Processing {country_name} ({country_code}) - Group {group_info['group']}")
        print(f"   Found {len(locations)} locations with parks")
        
        country_parks = []
        location_files = {}
        
        # Process each location
        for location in locations:
            descriptor = location['descriptor']
            location_name = location['name']
            expected_parks = location['parks']
            
            print(f"   📍 {descriptor}: {location_name} ({expected_parks} parks)")
            
            parks = fetch_parks_for_location(descriptor)
            location_parks = []
            
            for park in parks:
                try:
                    ref = park.get('reference', '')
                    name = park.get('name', '')
                    lat = park.get('latitude', 0)
                    lon = park.get('longitude', 0)
                    grid = park.get('grid', '')
                    
                    # Clean names for display
                    clean_ref = convert_umlauts(ref)
                    clean_name = convert_umlauts(name)
                    
                    # Skip if no valid coordinates
                    if not lat or not lon or lat == 0 or lon == 0:
                        print(f"      ⚠️  Skipping {ref}: No valid coordinates")
                        continue
                    
                    # Extract just the number from reference (e.g. "AT-0001" -> "1", "SG-0014" -> "14")
                    park_number = ref.split('-')[-1].lstrip('0') if '-' in ref else ref
                    if not park_number:  # If all zeros, use "0"
                        park_number = "0"
                    
                    # Format name for GPS display (number + name, truncate if needed)
                    display_name = f"{park_number} {clean_name}"
                    if len(display_name) > 50:  # Reasonable limit for GPS display
                        display_name = display_name[:47] + "..."
                    
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
                    
                    country_parks.append(gps_entry)
                    location_parks.append(gps_entry)
                    
                except Exception as e:
                    print(f"      ❌ Error processing park: {e}")
                    continue
            
            # Create location-specific file
            if location_parks:
                location_filename = f"POTA-GPS/{country_name}/{descriptor}.csv"
                location_files[descriptor] = {
                    'filename': location_filename,
                    'parks': location_parks,
                    'location_name': location_name
                }
            
            # Small delay to be nice to API
            time.sleep(0.1)
        
        # Write country-wide file
        if country_parks:
            country_filename = f"POTA-GPS/pota_{country_code.lower()}_all.csv"
            write_gps_csv(country_filename, country_parks)
            print(f"   ✅ Created {country_filename} with {len(country_parks)} parks")
        
        # Write location-specific files
        for descriptor, file_info in location_files.items():
            write_gps_csv(file_info['filename'], file_info['parks'])
            print(f"      📁 Created {descriptor}.csv with {len(file_info['parks'])} parks")
        
        country_totals[country_code] = {
            'name': country_name,
            'parks': len(country_parks),
            'locations': len(location_files)
        }
    
    # Create combined master file
    print(f"\n🌍 Creating master combined file...")
    all_parks = []
    
    for country_code in ['AT', 'SK', 'SG']:
        country_file = f"POTA-GPS/pota_{country_code.lower()}_all.csv"
        if Path(country_file).exists():
            with open(country_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_parks.append(row)
    
    if all_parks:
        write_gps_csv('POTA-GPS/pota_all_countries.csv', all_parks)
        print(f"   ✅ Created master file with {len(all_parks)} parks")
    
    # Print summary
    total_parks = sum(stats['parks'] for stats in country_totals.values())
    print(f"\n🎉 Successfully processed {total_parks} POTA parks")
    
    for country_code, stats in country_totals.items():
        group_letter = group_map[country_code]['group']
        print(f"   📊 {stats['name']}: {stats['parks']} parks, {stats['locations']} locations (Group {group_letter})")
    
    return total_parks

def write_gps_csv(filename, parks_data):
    """Write parks data in GPS CSV format."""
    if not parks_data:
        return
    
    # GPS CSV header
    fieldnames = ['Group', 'Group Name', 'Name', 'Date', 'Time', 'Latitude', 'Longitude', 'Altitude', 'Alarm']
    
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for park in parks_data:
            writer.writerow(park)

def main():
    print("POTA Parks GPS Format Generator")
    print("Uses official POTA API to create GPS format files")
    print("=" * 70)
    print("Target Countries:")
    print("   Austria (Group U)")
    print("   Slovakia (Group V)") 
    print("   Singapore (Group W)")
    print("Source: https://api.pota.app/")
    print()
    
    park_count = create_pota_gps_files()
    
    if park_count > 0:
        print("\n📁 Generated files structure:")
        print("POTA-GPS/")
        print("├── pota_at_all.csv        # All Austria parks")
        print("├── pota_sk_all.csv        # All Slovakia parks") 
        print("├── pota_sg_all.csv        # All Singapore parks")
        print("├── pota_all_countries.csv # Combined master file")
        print("├── Austria/")
        print("│   ├── AT-WI.csv          # Vienna parks")
        print("│   ├── AT-NO.csv          # Lower Austria parks")
        print("│   └── ... (all Austrian locations)")
        print("├── Slovakia/")
        print("│   ├── SK-BC.csv          # Banskobystricky parks")
        print("│   ├── SK-BL.csv          # Bratislavsky parks")
        print("│   └── ... (all Slovak locations)")
        print("└── Singapore/")
        print("    ├── SG-CS.csv          # Central Singapore parks")
        print("    ├── SG-NW.csv          # North West parks")
        print("    └── ... (all Singapore locations)")
        
        print("\n📋 GPS Format Features:")
        print("- gpsexample.csv compatible format")
        print("- Group letters: U (Austria), V (Slovakia), W (Singapore)")
        print("- Separate files for each location/region")
        print("- ASCII-converted names for radio display")
        print("- Current date timestamps")
        print("- Precise GPS coordinates from POTA API")
        
        print("\n🎯 Usage with Icom ID-52PLUS:")
        print("1. Import individual location files for specific areas")
        print("2. Or import country-wide files for complete coverage")
        print("3. Or import master file for all countries")
        
        print("\nPerfect for POTA activations and navigation!")
        print("Real-time data from official POTA API")
        
    else:
        print("\nNo POTA parks data generated")

if __name__ == "__main__":
    main()