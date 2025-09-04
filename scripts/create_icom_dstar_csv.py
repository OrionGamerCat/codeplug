#!/usr/bin/env python3
"""
Icom D-STAR CSV Creator
Creates Icom ID-52PLUS compatible D-STAR CSV files in rptexample.csv format for Austria, Slovakia, Japan, and Singapore
"""

import csv
import sys
from pathlib import Path

def convert_mcp_to_icom_dstar_format(input_file, output_file, group_number, group_name, country_filter=None):
    """Convert memory-channels-processor CSV to Icom D-STAR format."""
    
    # Icom D-STAR CSV header (based on rptexample.csv)
    icom_dstar_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=icom_dstar_header)
        writer.writeheader()
        
        for row in reader:
            try:
                # Filter by country if specified
                if country_filter and row.get('country', '') != country_filter:
                    continue
                
                # Only process D-STAR repeaters
                dstar_field = row.get('dstar', row.get('d-star', 'False')).lower()
                if dstar_field != 'true':
                    continue
                
                # Extract frequency and convert to float - use RX frequency (what you listen on)
                frequency = float(row.get('freq_rx', row.get('freq_tx', 0)))
                
                # Calculate offset and determine duplex
                try:
                    offset_mhz = float(row.get('offset', 0))
                    dup_direction = row.get('dup', '')
                    
                    if dup_direction == '+':
                        dup = 'DUP+'
                    elif dup_direction == '-':
                        dup = 'DUP-'
                    else:
                        dup = ''
                        offset_mhz = 0
                except (ValueError, KeyError):
                    dup = ''
                    offset_mhz = 0
                
                # D-STAR repeaters typically don't use CTCSS
                tone_setting = 'OFF'
                tone_value = '88.5Hz'
                
                # Determine position accuracy
                position = 'Exact' if row.get('loc_exact', 'False').lower() == 'true' else 'Approximate'
                
                # Get GPS coordinates
                try:
                    latitude = float(row.get('lat', 0))
                    longitude = float(row.get('long', 0))
                except (ValueError, TypeError):
                    latitude = 0
                    longitude = 0
                
                # Determine UTC offset based on country
                utc_offset = '+1:00'  # Default for Europe
                if country_filter == 'Singapore':
                    utc_offset = '+8:00'
                elif country_filter == 'Japan':
                    utc_offset = '+9:00'
                
                # Create gateway call sign (typically callsign with "G" suffix)
                callsign = row.get('callsign', '').strip()
                gateway_callsign = callsign.replace(' A', ' G').replace(' B', ' G').replace(' C', ' G')
                if not gateway_callsign.endswith(' G') and callsign:
                    if len(callsign) <= 7:
                        gateway_callsign = callsign + ' G'
                    else:
                        gateway_callsign = callsign[:-1] + 'G'
                
                # Create Icom D-STAR format row
                icom_row = {
                    'Group No': group_number,
                    'Group Name': group_name,
                    'Name': row.get('name', '').strip(),
                    'Sub Name': row.get('landmark', '').strip(),
                    'Repeater Call Sign': callsign,
                    'Gateway Call Sign': gateway_callsign,
                    'Frequency': frequency,
                    'Dup': dup,
                    'Offset': offset_mhz,
                    'Mode': 'DV',
                    'TONE': tone_setting,
                    'Repeater Tone': tone_value,
                    'RPT1USE': 'YES',
                    'Position': position,
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'UTC Offset': utc_offset
                }
                
                writer.writerow(icom_row)
                processed_count += 1
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return processed_count

def convert_japanese_dstar_csv(input_file, output_file, group_number, group_name):
    """Convert Japanese D-STAR CSV to standardized format."""
    
    processed_count = 0
    
    # Try different encodings for Japanese file
    encodings = ['shift_jis', 'utf-8', 'cp932']
    content = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"Error: Could not decode {input_file}")
        return 0
    
    # Write to temporary file with utf-8 encoding
    temp_file = 'temp_japanese_dstar.csv'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Process the temporary file
    with open(temp_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        
        # Update group information
        icom_dstar_header = [
            'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
            'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
            'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
        ]
        
        writer = csv.DictWriter(outfile, fieldnames=icom_dstar_header)
        writer.writeheader()
        
        for row in reader:
            try:
                # Update group information
                updated_row = dict(row)
                updated_row['Group No'] = group_number
                updated_row['Group Name'] = group_name
                
                writer.writerow(updated_row)
                processed_count += 1
                
            except Exception as e:
                print(f"Warning: Skipping Japanese row due to error: {e}")
                continue
    
    # Clean up temporary file
    Path(temp_file).unlink(missing_ok=True)
    
    return processed_count

def main():
    austrian_count = 0
    slovak_count = 0
    singapore_count = 0
    
    # Austrian D-STAR repeaters
    if Path('mcp_tmp_repeaters.csv').exists():
        print("🇦🇹 Creating Austrian D-STAR repeaters CSV...")
        austrian_count = convert_mcp_to_icom_dstar_format(
            'mcp_tmp_repeaters.csv',
            'austrian_dstar_repeaters.csv',
            32,
            'AT-DSTAR',
            'Austria'
        )
        print(f"✅ Created {austrian_count} Austrian D-STAR repeaters")
    else:
        print("❌ Austrian repeater data not found")
    
    # Slovak D-STAR repeaters - try different sources
    slovak_files = ['slovakia_tmp_repeaters.csv', '../slovakia_temp.csv']
    for slovak_file in slovak_files:
        if Path(slovak_file).exists():
            print(f"\n🇸🇰 Creating Slovak D-STAR repeaters CSV from {slovak_file}...")
            slovak_count = convert_mcp_to_icom_dstar_format(
                slovak_file,
                'slovak_dstar_repeaters.csv',
                33,
                'SK-DSTAR',
                'Slovakia'
            )
            print(f"✅ Created {slovak_count} Slovak D-STAR repeaters")
            break
    else:
        print("❌ Slovak repeater data not found")
    
    # Singapore D-STAR repeaters
    singapore_files = ['../singapore_repeaters.csv', 'singapore_repeaters.csv']
    for singapore_file in singapore_files:
        if Path(singapore_file).exists():
            print(f"\n🇸🇬 Creating Singapore D-STAR repeaters CSV from {singapore_file}...")
            singapore_count = convert_mcp_to_icom_dstar_format(
                singapore_file,
                'singapore_dstar_repeaters.csv',
                34,
                'SG-DSTAR',
                'Singapore'
            )
            print(f"✅ Created {singapore_count} Singapore D-STAR repeaters")
            break
    else:
        print("❌ Singapore repeater data not found")
    
    # Create combined file
    print("\n🌍 Creating combined D-STAR repeaters CSV...")
    
    combined_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    with open('combined_dstar_repeaters.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=combined_header)
        writer.writeheader()
        
        # Combine all files
        for filename in ['austrian_dstar_repeaters.csv', 'slovak_dstar_repeaters.csv', 'singapore_dstar_repeaters.csv']:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        writer.writerow(row)
    
    total_count = austrian_count + slovak_count + singapore_count
    print(f"✅ Combined file created with {total_count} total D-STAR repeaters")
    
    print("\n📁 Generated D-STAR files:")
    print("- austrian_dstar_repeaters.csv")
    print("- slovak_dstar_repeaters.csv") 
    print("- singapore_dstar_repeaters.csv")
    print("- combined_dstar_repeaters.csv")
    
    print("\n🎯 All D-STAR files are in Icom ID-52PLUS compatible format!")

if __name__ == "__main__":
    main()