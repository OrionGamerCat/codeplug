#!/usr/bin/env python3
"""
POTA Parks Generator for memory-channels-processor
Creates CSV data for POTA parks using the publicly available POTA API
"""

import json
import csv
import subprocess
import time
from pathlib import Path
import sys

def fetch_pota_spots():
    """Fetch current POTA spots to collect park data using curl."""
    try:
        result = subprocess.run(
            ['curl', '-s', 'https://api.pota.app/spot/activator'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error fetching POTA data: {result.stderr}")
            return []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        print(f"Error fetching POTA data: {e}")
        return []

def create_pota_parks_csv(output_file='pota_parks.csv'):
    """Create POTA parks CSV compatible with memory-channels-processor."""
    
    print("🏞️ Fetching POTA park data from API...")
    
    # Fetch active spots
    spots_data = fetch_pota_spots()
    if not spots_data:
        print("❌ No POTA data retrieved")
        return 0
    
    print(f"📡 Retrieved {len(spots_data)} active POTA spots")
    
    # Extract unique parks from spots
    parks = {}
    for spot in spots_data:
        try:
            ref = spot.get('reference', '')
            name = spot.get('name', '')
            location = spot.get('locationDesc', '')
            lat = spot.get('latitude', 0)
            lon = spot.get('longitude', 0)
            grid4 = spot.get('grid4', '')
            grid6 = spot.get('grid6', '')
            
            # Skip invalid entries
            if not ref or not name or lat == 0 or lon == 0:
                continue
            
            # Use reference as key to avoid duplicates
            if ref not in parks:
                # Determine country from reference
                country_code = ref.split('-')[0] if '-' in ref else 'Unknown'
                country_map = {
                    'US': 'United States', 'CA': 'Canada', 'AU': 'Australia',
                    'JP': 'Japan', 'DE': 'Germany', 'UK': 'United Kingdom',
                    'VK': 'Australia', 'VE': 'Canada', 'BY': 'Belarus',
                    'TH': 'Thailand', 'CN': 'China', 'OE': 'Austria',
                    'OK': 'Czech Republic', 'OM': 'Slovakia'
                }
                country = country_map.get(country_code, country_code)
                
                parks[ref] = {
                    'callsign': ref,
                    'name': name,
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
                    'landmark': location,
                    'state': location.split(',')[0] if ',' in location else location,
                    'country': country,
                    'country_code': country_code,
                    'loc_exact': 'True',
                    'lat': lat,
                    'long': lon,
                    'locator': grid6 if grid6 else grid4,
                    'sea_level': '',
                    'skip': 'False',
                    'scan_group': '',
                    'source_id': 'pota-parks',
                    'source_name': 'POTA Parks',
                    'source_provider': 'Parks on the Air',
                    'source_type': 'dynamic',
                    'source_license': '',
                    'source_url': 'https://pota.app/',
                    'offset': '0',
                    'dup': '',
                    'ctcss': 'False',
                    'simplex': 'True',
                    'split': 'False',
                    'multimode': 'False',
                    'name_formatted': f"{ref} {name}",
                    'distance': '',
                    'heading': ''
                }
        except Exception as e:
            print(f"Warning: Error processing spot: {e}")
            continue
    
    # Write CSV file in memory-channels-processor format
    if not parks:
        print("❌ No valid parks found")
        return 0
    
    # CSV header matching memory-channels-processor format
    fieldnames = [
        'callsign', 'name', 'band', 'freq_tx', 'freq_rx', 'ctcss_tx', 'ctcss_rx',
        'c4fm', 'dmr', 'dmr_id', 'dmr_cc', 'dstar', 'dstar_rpt1', 'dstar_rpt2',
        'fm', 'landmark', 'state', 'country', 'country_code', 'loc_exact',
        'lat', 'long', 'locator', 'sea_level', 'skip', 'scan_group',
        'source_id', 'source_name', 'source_provider', 'source_type',
        'source_license', 'source_url', 'offset', 'dup', 'ctcss',
        'simplex', 'split', 'multimode', 'name_formatted', 'distance', 'heading'
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for park_data in parks.values():
            writer.writerow(park_data)
    
    print(f"✅ Created {len(parks)} POTA parks in {output_file}")
    return len(parks)

def main():
    print("🏞️ POTA Parks Generator for memory-channels-processor")
    print("=" * 60)
    
    park_count = create_pota_parks_csv()
    
    if park_count > 0:
        print("\n📁 Generated file:")
        print("- pota_parks.csv")
        print("\n🎯 Usage with memory-channels-processor:")
        print('memory-channels-processor \\')
        print('  --source csv \\')
        print('  --csv-input-file pota_parks.csv \\')
        print('  --output-format icom \\')
        print('  --icom-type gps \\')
        print('  --output-file pota_parks_icom.csv')
        print("\n📋 POTA Parks Details:")
        print(f"- {park_count} currently active POTA parks")
        print("- GPS waypoint format (no frequencies)")
        print("- Includes park references, names, and precise coordinates")
        print("- Compatible with memory-channels-processor CSV input")
        print("\n⚠️  Note: Data is from currently active POTA spots only")
        print("   Not a complete database of all POTA parks")
    else:
        print("\n❌ No POTA parks data generated")

if __name__ == "__main__":
    main()