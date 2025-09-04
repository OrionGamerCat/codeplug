#!/usr/bin/env python3
"""
Icom SOTA CSV Creator
Creates Icom ID-52PLUS compatible CSV file for SOTA summits as GPS waypoints
"""

import csv
import sys
from pathlib import Path
import unicodedata

def convert_umlauts(text):
    """Convert German umlauts and special characters to ASCII equivalents."""
    if not text:
        return text
    
    # German umlaut conversions
    umlaut_map = {
        'ä': 'ae', 'Ä': 'Ae',
        'ö': 'oe', 'Ö': 'Oe', 
        'ü': 'ue', 'Ü': 'Ue',
        'ß': 'ss',
        'é': 'e', 'É': 'E',
        'è': 'e', 'È': 'E',
        'á': 'a', 'Á': 'A',
        'à': 'a', 'À': 'A',
        'í': 'i', 'Í': 'I',
        'ì': 'i', 'Ì': 'I',
        'ó': 'o', 'Ó': 'O',
        'ò': 'o', 'Ò': 'O',
        'ú': 'u', 'Ú': 'U',
        'ù': 'u', 'Ù': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ç': 'c', 'Ç': 'C',
        '–': '-', '—': '-',
        '"': '"', '"': '"',
        ''': "'", ''': "'",
        'ľ': 'l', 'Ľ': 'L',
        'ž': 'z', 'Ž': 'Z',
        'č': 'c', 'Č': 'C',
        'š': 's', 'Š': 'S',
        'ý': 'y', 'Ý': 'Y',
        'ť': 't', 'Ť': 'T',
        'ň': 'n', 'Ň': 'N',
        'ď': 'd', 'Ď': 'D',
        'ř': 'r', 'Ř': 'R',
        '…': '...'
    }
    
    # Apply umlaut conversions
    result = text
    for umlaut, replacement in umlaut_map.items():
        result = result.replace(umlaut, replacement)
    
    # Remove any remaining non-ASCII characters
    result = unicodedata.normalize('NFD', result)
    result = ''.join(char for char in result if ord(char) < 128)
    
    return result

def convert_sota_to_icom_format(input_file, output_file, group_number, group_name):
    """Convert SOTA summits to Icom GPS format."""
    
    # Icom CSV header for GPS waypoints
    icom_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=icom_header)
        writer.writeheader()
        
        for row in reader:
            try:
                # Get coordinates
                lat = float(row.get('lat', 0))
                lon = float(row.get('long', 0))
                
                # Skip entries without valid coordinates
                if lat == 0 or lon == 0:
                    continue
                
                # Get summit info
                callsign = row.get('callsign', '').strip()
                summit_name = row.get('name', '').strip()
                state = row.get('state', '').strip()
                country_code = row.get('country_code', '').strip()
                elevation = row.get('sea_level', '').strip()
                
                # Format name - use SOTA callsign as primary identifier
                if not callsign:
                    continue
                    
                name = callsign
                if summit_name:
                    name = f"{callsign} {summit_name[:10]}"  # Limit length for display
                
                # Create sub name with state and elevation
                sub_parts = []
                if state:
                    sub_parts.append(convert_umlauts(state[:8]))  # Limit state name length
                if elevation:
                    try:
                        elev_m = int(float(elevation))
                        sub_parts.append(f"{elev_m}m")
                    except:
                        pass
                
                sub_name = " ".join(sub_parts) if sub_parts else country_code
                
                # Apply ASCII conversion to names
                name = convert_umlauts(name)
                sub_name = convert_umlauts(sub_name)
                
                # Determine UTC offset based on country
                utc_offset = '+1:00'  # Central Europe default
                if country_code == 'SGP':
                    utc_offset = '+8:00'
                
                # Create Icom GPS waypoint row
                icom_row = {
                    'Group No': group_number,
                    'Group Name': group_name,
                    'Name': name[:16],  # Limit name length for Icom display
                    'Sub Name': sub_name[:16],  # Limit sub name length
                    'Repeater Call Sign': '',
                    'Gateway Call Sign': '',
                    'Frequency': '',  # GPS waypoint - no frequency
                    'Dup': '',
                    'Offset': '',
                    'Mode': 'GPS',  # GPS waypoint mode
                    'TONE': '',
                    'Repeater Tone': '',
                    'RPT1USE': '',
                    'Position': 'Exact',  # SOTA coordinates are precise
                    'Latitude': lat,
                    'Longitude': lon,
                    'UTC Offset': utc_offset
                }
                
                writer.writerow(icom_row)
                processed_count += 1
                
            except (ValueError, KeyError, TypeError) as e:
                print(f"Warning: Skipping SOTA row due to error: {e}")
                continue
    
    return processed_count

def main():
    if not Path('sota_summits.csv').exists():
        print("❌ SOTA summits data not found - please generate it first")
        return
    
    print("🏔️ Creating SOTA summits CSV for Icom ID-52PLUS...")
    
    sota_count = convert_sota_to_icom_format(
        'sota_summits.csv',
        'sota_summits_icom.csv',
        70,  # Use group 70 for SOTA
        'SOTA-Summits'
    )
    
    print(f"✅ Created {sota_count} SOTA summits as GPS waypoints")
    print("\n📁 Generated file:")
    print("- sota_summits_icom.csv")
    print("\n🎯 SOTA summits ready for Icom ID-52PLUS!")
    print("\n📋 SOTA Summit Details:")
    print("- Mode: GPS waypoints (not frequencies)")
    print("- Group: 70 (SOTA-Summits)")
    print("- Countries: Austria, Slovakia, Singapore")
    print("- Includes summit names, elevations, and precise coordinates")
    print("- ASCII-converted names for proper display")
    print("\n🥾 Perfect for SOTA activations and navigation!")

if __name__ == "__main__":
    main()