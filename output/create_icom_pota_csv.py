#!/usr/bin/env python3
"""
Convert POTA Parks to Icom ID-52PLUS format
Converts POTA park data to fmexample.csv compatible format
"""

import csv
import json
import subprocess
from pathlib import Path

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
        ''': "'", ''': "'", '…': '...', 'ř': 'r', 'Ř': 'R'
    }
    
    result = text
    for umlaut, replacement in umlaut_map.items():
        result = result.replace(umlaut, replacement)
    
    return result

def fetch_and_convert_pota_parks():
    """Fetch POTA parks and convert to Icom format."""
    
    print("🏞️ Fetching current POTA parks from API...")
    
    # Fetch current spots using curl
    try:
        result = subprocess.run(
            ['curl', '-s', 'https://api.pota.app/spot/activator'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"❌ Error fetching POTA data")
            return 0
        
        spots_data = json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Error processing POTA data: {e}")
        return 0
    
    print(f"📡 Retrieved {len(spots_data)} active POTA spots")
    
    # Extract unique parks
    parks = {}
    for spot in spots_data:
        try:
            ref = spot.get('reference', '')
            name = spot.get('name', '')
            location = spot.get('locationDesc', '')
            lat = spot.get('latitude', 0)
            lon = spot.get('longitude', 0)
            
            if not ref or not name or lat == 0 or lon == 0:
                continue
                
            if ref not in parks:
                parks[ref] = {
                    'reference': ref,
                    'name': name,
                    'location': location,
                    'lat': lat,
                    'lon': lon
                }
        except:
            continue
    
    if not parks:
        print("❌ No valid POTA parks found")
        return 0
    
    # Convert to Icom format
    icom_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open('pota_parks_icom.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=icom_header)
        writer.writeheader()
        
        for park in parks.values():
            try:
                # Clean and format names
                park_ref = convert_umlauts(park['reference'])
                park_name = convert_umlauts(park['name'])
                park_location = convert_umlauts(park['location'])
                
                # Truncate names for Icom display
                name = f"{park_ref}"[:16]
                sub_name = park_name[:16] if park_name else park_location[:16]
                
                # Determine UTC offset based on reference
                utc_offset = '+1:00'  # Default Central Europe
                if park_ref.startswith('US') or park_ref.startswith('CA'):
                    utc_offset = '-5:00'  # North America (EST)
                elif park_ref.startswith('AU') or park_ref.startswith('VK'):
                    utc_offset = '+10:00'  # Australia
                elif park_ref.startswith('JP'):
                    utc_offset = '+9:00'  # Japan
                elif park_ref.startswith('TH'):
                    utc_offset = '+7:00'  # Thailand
                elif park_ref.startswith('CN'):
                    utc_offset = '+8:00'  # China
                
                icom_row = {
                    'Group No': 75,
                    'Group Name': 'POTA-Parks',
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
                    'Latitude': park['lat'],
                    'Longitude': park['lon'],
                    'UTC Offset': utc_offset
                }
                
                writer.writerow(icom_row)
                processed_count += 1
                
            except Exception as e:
                print(f"Warning: Skipping park due to error: {e}")
                continue
    
    return processed_count

def main():
    print("🏞️ POTA Parks to Icom ID-52PLUS Converter")
    print("=" * 50)
    
    park_count = fetch_and_convert_pota_parks()
    
    if park_count > 0:
        print(f"✅ Created {park_count} POTA parks for Icom ID-52PLUS")
        print("\n📁 Generated file:")
        print("- pota_parks_icom.csv")
        print("\n🎯 POTA Parks ready for Icom ID-52PLUS!")
        print("\n📋 POTA Park Details:")
        print("- GPS waypoints (no frequencies)")
        print("- Group: 75 (POTA-Parks)")
        print("- ASCII-converted names for proper display")
        print("- Currently active POTA parks only")
        print("- Includes park references and precise coordinates")
        print("\n🏞️ Perfect for POTA activations and navigation!")
        print("\n⚠️  Note: Shows only currently active parks")
        print("   Run this script regularly to get different parks")
    else:
        print("\n❌ No POTA parks data generated")

if __name__ == "__main__":
    main()