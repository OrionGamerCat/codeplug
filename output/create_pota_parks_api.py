#!/usr/bin/env python3
"""
POTA Parks API Generator for Austria, Slovakia, and Singapore
Uses official POTA API endpoints to get all registered parks with precise coordinates
"""

import json
import csv
import subprocess
import time
from pathlib import Path
import sys
import re

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

def maidenhead_to_latlon(grid):
    """Convert Maidenhead grid locator to latitude/longitude."""
    if not grid or len(grid) < 4:
        return None, None
    
    try:
        # Maidenhead grid format: AB12cd34ef56
        grid = grid.upper()
        
        # Field (first 2 letters): 20° longitude, 10° latitude
        if len(grid) >= 2:
            lon_field = (ord(grid[0]) - ord('A')) * 20 - 180
            lat_field = (ord(grid[1]) - ord('A')) * 10 - 90
        else:
            return None, None
        
        # Square (next 2 digits): 2° longitude, 1° latitude
        if len(grid) >= 4:
            lon_square = int(grid[2]) * 2
            lat_square = int(grid[3]) * 1
        else:
            lon_square = lat_square = 0
        
        # Subsquare (next 2 letters): 5' longitude, 2.5' latitude
        if len(grid) >= 6:
            lon_subsquare = (ord(grid[4]) - ord('A')) * (5/60)
            lat_subsquare = (ord(grid[5]) - ord('A')) * (2.5/60)
        else:
            lon_subsquare = lat_subsquare = 0
        
        # Extended square (next 2 digits): 0.5' longitude, 0.25' latitude
        if len(grid) >= 8:
            lon_extended = int(grid[6]) * (0.5/60)
            lat_extended = int(grid[7]) * (0.25/60)
        else:
            lon_extended = lat_extended = 0
        
        # Calculate final coordinates (center of grid square)
        longitude = lon_field + lon_square + lon_subsquare + lon_extended + (1/60)  # Center offset
        latitude = lat_field + lat_square + lat_subsquare + lat_extended + (1.25/60)  # Center offset
        
        return round(latitude, 6), round(longitude, 6)
    
    except (ValueError, IndexError):
        return None, None

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

def create_comprehensive_pota_parks():
    """Create comprehensive POTA parks database using API."""
    
    print("🏞️ POTA Parks API Generator")
    print("=" * 50)
    
    # Get location descriptors
    countries = fetch_pota_locations()
    if not countries:
        print("❌ Failed to fetch country locations")
        return 0
    
    all_parks = []
    country_stats = {}
    
    # Process each country
    for country_code, country_info in countries.items():
        country_name = country_info['name']
        locations = country_info['locations']
        
        print(f"\n🇦🇹 Processing {country_name} ({country_code})...")
        print(f"   Found {len(locations)} locations with parks")
        
        country_parks = []
        
        # Fetch parks for each location
        for location in locations:
            descriptor = location['descriptor']
            location_name = location['name']
            expected_parks = location['parks']
            
            print(f"   📍 {descriptor}: {location_name} ({expected_parks} parks)")
            
            parks = fetch_parks_for_location(descriptor)
            
            for park in parks:
                try:
                    ref = park.get('reference', '')
                    name = park.get('name', '')
                    lat = park.get('latitude', 0)
                    lon = park.get('longitude', 0)
                    grid = park.get('grid', '')
                    location_desc = park.get('locationDesc', '')
                    attempts = park.get('attempts', 0)
                    activations = park.get('activations', 0)
                    qsos = park.get('qsos', 0)
                    
                    # Clean names
                    clean_ref = convert_umlauts(ref)
                    clean_name = convert_umlauts(name)
                    clean_location = convert_umlauts(location_desc)
                    
                    # Use provided coordinates, fallback to grid conversion if needed
                    final_lat, final_lon = lat, lon
                    
                    if (not lat or not lon or lat == 0 or lon == 0) and grid:
                        print(f"      Converting grid {grid} to coordinates...")
                        grid_lat, grid_lon = maidenhead_to_latlon(grid)
                        if grid_lat and grid_lon:
                            final_lat, final_lon = grid_lat, grid_lon
                    
                    # Skip if no valid coordinates
                    if not final_lat or not final_lon or final_lat == 0 or final_lon == 0:
                        print(f"      ⚠️  Skipping {ref}: No valid coordinates")
                        continue
                    
                    park_data = {
                        'callsign': clean_ref,
                        'name': clean_name,
                        'band': 'gps',
                        'freq_tx': '',
                        'freq_rx': '',
                        'ctcss_tx': '',
                        'ctcss_rx': '',
                        'c4fm': 'False',
                        'dmr': 'False',
                        'dmr_id': '',
                        'dmr_cc': '',
                        'dstar': 'False',
                        'dstar_rpt1': '',
                        'dstar_rpt2': '',
                        'fm': 'False',
                        'landmark': clean_location,
                        'state': location_name,
                        'country': country_name,
                        'country_code': country_code,
                        'loc_exact': 'True',
                        'lat': final_lat,
                        'long': final_lon,
                        'locator': grid,
                        'sea_level': '',
                        'skip': 'False',
                        'scan_group': '',
                        'source_id': 'pota-api',
                        'source_name': 'POTA API',
                        'source_provider': 'Parks on the Air',
                        'source_type': 'api',
                        'source_license': '',
                        'source_url': f'https://api.pota.app/location/parks/{descriptor}',
                        'offset': '0',
                        'dup': '',
                        'ctcss': 'False',
                        'simplex': 'True',
                        'split': 'False',
                        'multimode': 'False',
                        'name_formatted': f"{clean_ref} {clean_name}",
                        'distance': '',
                        'heading': '',
                        'attempts': attempts,
                        'activations': activations,
                        'qsos': qsos,
                        'grid': grid
                    }
                    
                    country_parks.append(park_data)
                    all_parks.append(park_data)
                    
                except Exception as e:
                    print(f"      ❌ Error processing park: {e}")
                    continue
            
            # Small delay to be nice to API
            time.sleep(0.1)
        
        country_stats[country_code] = {
            'name': country_name,
            'parks': len(country_parks),
            'locations': len(locations)
        }
        
        print(f"   ✅ Processed {len(country_parks)} parks for {country_name}")
    
    if not all_parks:
        print("❌ No parks data retrieved")
        return 0
    
    # Write comprehensive CSV
    fieldnames = [
        'callsign', 'name', 'band', 'freq_tx', 'freq_rx', 'ctcss_tx', 'ctcss_rx',
        'c4fm', 'dmr', 'dmr_id', 'dmr_cc', 'dstar', 'dstar_rpt1', 'dstar_rpt2',
        'fm', 'landmark', 'state', 'country', 'country_code', 'loc_exact',
        'lat', 'long', 'locator', 'sea_level', 'skip', 'scan_group',
        'source_id', 'source_name', 'source_provider', 'source_type',
        'source_license', 'source_url', 'offset', 'dup', 'ctcss',
        'simplex', 'split', 'multimode', 'name_formatted', 'distance', 'heading',
        'attempts', 'activations', 'qsos', 'grid'
    ]
    
    with open('pota_parks_api.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for park in all_parks:
            writer.writerow(park)
    
    # Print statistics
    total_parks = len(all_parks)
    print(f"\n✅ Successfully created {total_parks} POTA parks")
    for country_code, stats in country_stats.items():
        print(f"   🏞️ {stats['name']}: {stats['parks']} parks from {stats['locations']} locations")
    
    return total_parks

def create_icom_format():
    """Convert to Icom ID-52PLUS GPS format."""
    
    print("\n🎯 Converting to Icom ID-52PLUS format...")
    
    if not Path('pota_parks_api.csv').exists():
        print("❌ pota_parks_api.csv not found")
        return 0
    
    # Group assignments
    group_map = {
        'AT': {'number': 75, 'name': 'POTA-AT', 'utc': '+1:00'},
        'SK': {'number': 76, 'name': 'POTA-SK', 'utc': '+1:00'},
        'SG': {'number': 77, 'name': 'POTA-SG', 'utc': '+8:00'}
    }
    
    # Icom format
    icom_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open('pota_parks_api_icom.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=icom_header)
        writer.writeheader()
        
        with open('pota_parks_api.csv', 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                try:
                    country_code = row['country_code']
                    park_ref = row['callsign']
                    park_name = row['name']
                    lat = row['lat']
                    lon = row['long']
                    
                    if country_code not in group_map:
                        continue
                    
                    group_info = group_map[country_code]
                    
                    # Truncate names for Icom display (16 chars max)
                    name = park_ref[:16]
                    sub_name = park_name[:16]
                    
                    icom_row = {
                        'Group No': group_info['number'],
                        'Group Name': group_info['name'],
                        'Name': name,
                        'Sub Name': sub_name,
                        'Repeater Call Sign': '',
                        'Gateway Call Sign': '',
                        'Frequency': '',  # GPS waypoint
                        'Dup': '',
                        'Offset': '',
                        'Mode': 'GPS',
                        'TONE': '',
                        'Repeater Tone': '',
                        'RPT1USE': '',
                        'Position': 'Exact',
                        'Latitude': lat,
                        'Longitude': lon,
                        'UTC Offset': group_info['utc']
                    }
                    
                    writer.writerow(icom_row)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Warning: Skipping park due to error: {e}")
                    continue
    
    return processed_count

def main():
    print("🏞️ POTA Parks API Generator")
    print("Uses official POTA API endpoints")
    print("=" * 60)
    print("📍 Target Countries: Austria, Slovakia, Singapore")
    print("🌐 Source: https://api.pota.app/")
    print()
    
    park_count = create_comprehensive_pota_parks()
    
    if park_count > 0:
        icom_count = create_icom_format()
        
        print(f"\n🎉 Successfully processed {park_count} POTA parks")
        print(f"📱 Created {icom_count} GPS waypoints for Icom ID-52PLUS")
        
        print("\n📁 Generated files:")
        print("- pota_parks_api.csv (memory-channels-processor format)")
        print("- pota_parks_api_icom.csv (Icom ID-52PLUS format)")
        
        print("\n🎯 Usage with memory-channels-processor:")
        print('memory-channels-processor \\')
        print('  --source csv \\')
        print('  --csv-input-file pota_parks_api.csv \\')
        print('  --output-format icom \\')
        print('  --icom-type gps \\')
        print('  --output-file pota_parks_final.csv')
        
        print("\n📋 POTA Parks Features:")
        print("- Official API data (most current)")
        print("- All registered parks (active and inactive)")
        print("- Precise GPS coordinates from grid squares")
        print("- Activation statistics included")
        print("- ASCII-converted names for radio display")
        print("- Country-specific groups:")
        print("  * Austria: Group 75 (POTA-AT)")
        print("  * Slovakia: Group 76 (POTA-SK)")  
        print("  * Singapore: Group 77 (POTA-SG)")
        
        print("\n🏞️ Perfect for POTA activations and hunting!")
        print("📡 Real-time data from POTA API")
        
    else:
        print("\n❌ No POTA parks data generated")

if __name__ == "__main__":
    main()