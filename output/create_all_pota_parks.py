#!/usr/bin/env python3
"""
All POTA Parks Generator for Austria, Slovakia, and Singapore
Creates CSV data for all registered POTA parks from official POTA database
Uses the complete parks list from pota.app/all_parks_ext.csv
"""

import csv
import subprocess
import time
from pathlib import Path
import sys

def download_pota_parks():
    """Download the official POTA parks CSV with coordinates."""
    try:
        print("📡 Downloading official POTA parks database...")
        result = subprocess.run(
            ['curl', '-s', 'https://pota.app/all_parks_ext.csv', '-o', 'all_parks_ext.csv'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Downloaded POTA parks database")
            return True
        else:
            print(f"❌ Error downloading POTA data: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"❌ Error downloading POTA data: {e}")
        return False

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

def create_all_pota_parks_csv(countries=['AT', 'SK', 'SG'], output_file='all_pota_parks.csv'):
    """Create comprehensive POTA parks CSV for specified countries."""
    
    if not Path('all_parks_ext.csv').exists():
        if not download_pota_parks():
            return 0
    
    print(f"🏞️ Processing POTA parks for countries: {', '.join(countries)}")
    
    # Country mapping
    country_map = {
        'AT': 'Austria',
        'SK': 'Slovakia', 
        'SG': 'Singapore'
    }
    
    # Read and process POTA parks
    parks = {}
    
    try:
        with open('all_parks_ext.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                ref = row.get('reference', '').strip('"')
                name = row.get('name', '').strip('"')
                active = row.get('active', '').strip('"')
                location = row.get('locationDesc', '').strip('"')
                lat = row.get('latitude', '').strip('"')
                lon = row.get('longitude', '').strip('"')
                grid = row.get('grid', '').strip('"')
                
                # Filter by country prefix
                country_prefix = ref.split('-')[0] if '-' in ref else ''
                if country_prefix not in countries:
                    continue
                
                # Skip invalid entries
                if not ref or not name or not lat or not lon:
                    continue
                
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    continue
                
                # Clean names for Icom display
                clean_name = convert_umlauts(name)
                clean_ref = convert_umlauts(ref)
                clean_location = convert_umlauts(location)
                
                country_name = country_map.get(country_prefix, country_prefix)
                
                parks[ref] = {
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
                    'state': clean_location,
                    'country': country_name,
                    'country_code': country_prefix,
                    'loc_exact': 'True',
                    'lat': lat,
                    'long': lon,
                    'locator': grid,
                    'sea_level': '',
                    'skip': 'False',
                    'scan_group': '',
                    'source_id': 'pota-all-parks',
                    'source_name': 'POTA All Parks',
                    'source_provider': 'Parks on the Air',
                    'source_type': 'static',
                    'source_license': '',
                    'source_url': 'https://pota.app/',
                    'offset': '0',
                    'dup': '',
                    'ctcss': 'False',
                    'simplex': 'True',
                    'split': 'False',
                    'multimode': 'False',
                    'name_formatted': f"{clean_ref} {clean_name}",
                    'distance': '',
                    'heading': '',
                    'active': active
                }
                
    except Exception as e:
        print(f"❌ Error reading POTA parks: {e}")
        return 0
    
    if not parks:
        print("❌ No valid parks found")
        return 0
    
    # Write CSV file in memory-channels-processor format
    fieldnames = [
        'callsign', 'name', 'band', 'freq_tx', 'freq_rx', 'ctcss_tx', 'ctcss_rx',
        'c4fm', 'dmr', 'dmr_id', 'dmr_cc', 'dstar', 'dstar_rpt1', 'dstar_rpt2',
        'fm', 'landmark', 'state', 'country', 'country_code', 'loc_exact',
        'lat', 'long', 'locator', 'sea_level', 'skip', 'scan_group',
        'source_id', 'source_name', 'source_provider', 'source_type',
        'source_license', 'source_url', 'offset', 'dup', 'ctcss',
        'simplex', 'split', 'multimode', 'name_formatted', 'distance', 'heading', 'active'
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for park_data in parks.values():
            writer.writerow(park_data)
    
    # Print statistics
    country_counts = {}
    active_counts = {}
    for park in parks.values():
        country = park['country_code']
        country_counts[country] = country_counts.get(country, 0) + 1
        if park['active'] == '1':
            active_counts[country] = active_counts.get(country, 0) + 1
    
    print(f"✅ Created {len(parks)} POTA parks in {output_file}")
    for country in countries:
        total = country_counts.get(country, 0)
        active = active_counts.get(country, 0)
        country_name = country_map.get(country, country)
        print(f"   📍 {country_name}: {total} parks ({active} active)")
    
    return len(parks)

def create_icom_gps_format():
    """Convert to Icom GPS format."""
    
    print("\n🎯 Converting to Icom ID-52PLUS GPS format...")
    
    if not Path('all_pota_parks.csv').exists():
        print("❌ all_pota_parks.csv not found")
        return 0
    
    # Icom GPS format
    icom_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open('all_pota_parks_icom.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=icom_header)
        writer.writeheader()
        
        with open('all_pota_parks.csv', 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                try:
                    country_code = row['country_code']
                    park_ref = row['callsign']
                    park_name = row['name']
                    lat = row['lat']
                    lon = row['long']
                    
                    # Truncate names for Icom display
                    name = park_ref[:16]
                    sub_name = park_name[:16]
                    
                    # Determine group number and UTC offset by country
                    group_no = 75  # Default
                    group_name = 'POTA-All'
                    utc_offset = '+1:00'  # Default Central Europe
                    
                    if country_code == 'AT':
                        group_no = 75
                        group_name = 'POTA-AT'
                        utc_offset = '+1:00'
                    elif country_code == 'SK':
                        group_no = 76
                        group_name = 'POTA-SK'
                        utc_offset = '+1:00'
                    elif country_code == 'SG':
                        group_no = 77
                        group_name = 'POTA-SG'
                        utc_offset = '+8:00'
                    
                    icom_row = {
                        'Group No': group_no,
                        'Group Name': group_name,
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
                        'UTC Offset': utc_offset
                    }
                    
                    writer.writerow(icom_row)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Warning: Skipping park due to error: {e}")
                    continue
    
    return processed_count

def main():
    print("🏞️ All POTA Parks Generator")
    print("=" * 50)
    print("📍 Target Countries: Austria, Slovakia, Singapore")
    print("📂 Source: Official POTA Database")
    print()
    
    park_count = create_all_pota_parks_csv()
    
    if park_count > 0:
        icom_count = create_icom_gps_format()
        
        print(f"\n✅ Successfully processed {park_count} POTA parks")
        print(f"📱 Created {icom_count} GPS waypoints for Icom ID-52PLUS")
        
        print("\n📁 Generated files:")
        print("- all_pota_parks.csv (memory-channels-processor format)")
        print("- all_pota_parks_icom.csv (Icom ID-52PLUS format)")
        
        print("\n🎯 Usage with memory-channels-processor:")
        print('memory-channels-processor \\')
        print('  --source csv \\')
        print('  --csv-input-file all_pota_parks.csv \\')
        print('  --output-format icom \\')
        print('  --icom-type gps \\')
        print('  --output-file pota_parks_processed.csv')
        
        print("\n📋 POTA Parks Details:")
        print("- ALL registered POTA parks (not just active ones)")
        print("- Austria: Group 75 (POTA-AT)")
        print("- Slovakia: Group 76 (POTA-SK)")
        print("- Singapore: Group 77 (POTA-SG)")
        print("- GPS waypoints with precise coordinates")
        print("- ASCII-converted names for proper display")
        print("- Includes park references and locations")
        
        print("\n🏞️ Perfect for POTA hunting and activations!")
        print("📍 Complete database of all registered parks")
        
    else:
        print("\n❌ No POTA parks data generated")

if __name__ == "__main__":
    main()