#!/usr/bin/env python3
"""
Icom PMR CSV Creator
Creates Icom ID-52PLUS compatible CSV file for PMR channels
"""

import csv
import sys
from pathlib import Path

def convert_pmr_to_icom_format(input_file, output_file, group_number, group_name):
    """Convert PMR channels to Icom format."""
    
    # Icom CSV header (based on fmexample.csv)
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
                # PMR channels are simplex (same TX/RX frequency)
                frequency = float(row['freq_rx'])  # Use RX frequency
                
                # PMR channels are simplex - no offset
                dup = ''
                offset_mhz = 0.0
                
                # PMR typically doesn't use CTCSS by default
                tone_setting = 'OFF'
                tone_value = '88.5Hz'
                
                # Create Icom format row
                icom_row = {
                    'Group No': group_number,
                    'Group Name': group_name,
                    'Name': row.get('name', '').strip(),
                    'Sub Name': 'PMR',
                    'Repeater Call Sign': '',  # PMR doesn't have call signs
                    'Gateway Call Sign': '',
                    'Frequency': frequency,
                    'Dup': dup,
                    'Offset': offset_mhz,
                    'Mode': 'FM',
                    'TONE': tone_setting,
                    'Repeater Tone': tone_value,
                    'RPT1USE': 'NO',
                    'Position': 'Approximate',
                    'Latitude': 0,
                    'Longitude': 0,
                    'UTC Offset': '+1:00'  # Central Europe
                }
                
                writer.writerow(icom_row)
                processed_count += 1
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return processed_count

def main():
    if not Path('pmr_channels.csv').exists():
        print("❌ PMR channel data not found - please generate it first")
        return
    
    print("📻 Creating PMR channels CSV for Icom ID-52PLUS...")
    
    pmr_count = convert_pmr_to_icom_format(
        'pmr_channels.csv',
        'pmr_channels_icom.csv',
        80,  # Use group 80 for PMR
        'PMR-Channels'
    )
    
    print(f"✅ Created {pmr_count} PMR channels")
    print("\n📁 Generated file:")
    print("- pmr_channels_icom.csv")
    print("\n🎯 PMR channels ready for Icom ID-52PLUS!")
    print("\n📋 PMR Channel Details:")
    print("- Frequency Range: 446.006 - 446.194 MHz")
    print("- Mode: FM Simplex")
    print("- Group: 80 (PMR-Channels)")
    print("- License-free operation in Europe")

if __name__ == "__main__":
    main()