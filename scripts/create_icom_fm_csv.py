#!/usr/bin/env python3
"""
Icom FM CSV Creator
Creates Icom ID-52PLUS compatible CSV files in fmexample.csv format for Austria, Slovakia, and Singapore
"""

import csv
import sys
from pathlib import Path

def convert_mcp_to_icom_fm_format(input_file, output_file, group_number, group_name, country_filter=None):
    """Convert memory-channels-processor CSV to Icom FM format."""
    
    # Icom FM CSV header (based on fmexample.csv)
    icom_fm_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    processed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=icom_fm_header)
        writer.writeheader()
        
        for row in reader:
            try:
                # Filter by country if specified
                if country_filter and row.get('country', '') != country_filter:
                    continue
                
                # Only process FM repeaters
                if row.get('fm', 'True').lower() != 'true':
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
                
                # Extract CTCSS
                ctcss_tx = row.get('ctcss_tx', '')
                if ctcss_tx:
                    try:
                        tone_freq = float(ctcss_tx)
                        tone_setting = 'TONE'
                        tone_value = f"{tone_freq}Hz"
                    except ValueError:
                        tone_setting = 'OFF'
                        tone_value = '88.5Hz'
                else:
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
                
                # Create Icom FM format row
                icom_row = {
                    'Group No': group_number,
                    'Group Name': group_name,
                    'Name': row.get('name', '').strip(),
                    'Sub Name': row.get('landmark', '').strip(),
                    'Repeater Call Sign': row.get('callsign', '').strip(),
                    'Gateway Call Sign': '',  # FM doesn't use gateway
                    'Frequency': frequency,
                    'Dup': dup,
                    'Offset': offset_mhz,
                    'Mode': 'FM',
                    'TONE': tone_setting,
                    'Repeater Tone': tone_value,
                    'RPT1USE': 'YES' if tone_setting != 'OFF' else 'NO',
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

def main():
    austrian_count = 0
    slovak_count = 0
    singapore_count = 0
    
    # Austrian repeaters
    if Path('mcp_tmp_repeaters.csv').exists():
        print("🇦🇹 Creating Austrian FM repeaters CSV...")
        austrian_count = convert_mcp_to_icom_fm_format(
            'mcp_tmp_repeaters.csv',
            'austrian_fm_repeaters.csv',
            32,
            'AT-Repeaters',
            'Austria'
        )
        print(f"✅ Created {austrian_count} Austrian FM repeaters")
    else:
        print("❌ Austrian repeater data not found")
    
    # Slovak repeaters - try different sources
    slovak_files = ['slovakia_tmp_repeaters.csv', '../slovakia_temp.csv']
    for slovak_file in slovak_files:
        if Path(slovak_file).exists():
            print(f"\n🇸🇰 Creating Slovak FM repeaters CSV from {slovak_file}...")
            slovak_count = convert_mcp_to_icom_fm_format(
                slovak_file,
                'slovak_fm_repeaters.csv',
                33,
                'SK-Repeaters',
                'Slovakia'
            )
            print(f"✅ Created {slovak_count} Slovak FM repeaters")
            break
    else:
        print("❌ Slovak repeater data not found")
    
    # Singapore repeaters
    singapore_files = ['../singapore_repeaters.csv', 'singapore_repeaters.csv']
    for singapore_file in singapore_files:
        if Path(singapore_file).exists():
            print(f"\n🇸🇬 Creating Singapore FM repeaters CSV from {singapore_file}...")
            singapore_count = convert_mcp_to_icom_fm_format(
                singapore_file,
                'singapore_fm_repeaters.csv',
                34,
                'SG-Repeaters',
                'Singapore'
            )
            print(f"✅ Created {singapore_count} Singapore FM repeaters")
            break
    else:
        print("❌ Singapore repeater data not found")
    
    print(f"✅ Created {singapore_count} Singapore FM repeaters")
    
    # Create combined file
    print("\n🌍 Creating combined FM repeaters CSV...")
    
    combined_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    with open('combined_fm_repeaters.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=combined_header)
        writer.writeheader()
        
        # Combine all files
        for filename in ['austrian_fm_repeaters.csv', 'slovak_fm_repeaters.csv', 'singapore_fm_repeaters.csv']:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        writer.writerow(row)
    
    total_count = austrian_count + slovak_count + singapore_count
    print(f"✅ Combined file created with {total_count} total FM repeaters")
    
    print("\n📁 Generated files:")
    print("- austrian_fm_repeaters.csv")
    print("- slovak_fm_repeaters.csv") 
    print("- singapore_fm_repeaters.csv")
    print("- combined_fm_repeaters.csv")
    
    print("\n🎯 All files are in Icom ID-52PLUS compatible format!")

if __name__ == "__main__":
    main()