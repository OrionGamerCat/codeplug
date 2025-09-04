#!/usr/bin/env python3
"""
Japanese Repeater Processor
Converts Japanese repeater CSV to memory-channels-processor format and creates GPS-enhanced version
"""

import csv
import sys
from pathlib import Path

def convert_japanese_csv_to_mcp_format(input_file, output_file):
    """Convert Japanese Icom CSV to memory-channels-processor CSV format."""
    
    # Memory-channels-processor CSV header
    mcp_header = [
        'callsign', 'name', 'band', 'freq_tx', 'freq_rx', 'ctcss_tx', 'ctcss_rx',
        'c4fm', 'dmr', 'dmr_id', 'dmr_cc', 'dstar', 'dstar_rpt1', 'dstar_rpt2',
        'fm', 'landmark', 'state', 'country', 'country_code', 'loc_exact',
        'lat', 'long', 'locator', 'sea_level', 'skip', 'scan_group',
        'source_id', 'source_name', 'source_provider', 'source_type',
        'source_license', 'source_url', 'offset', 'dup', 'ctcss',
        'simplex', 'split', 'multimode', 'name_formatted', 'distance', 'heading'
    ]
    
    processed_count = 0
    
    # Try different encodings for Japanese text
    encodings_to_try = ['shift_jis', 'utf-8', 'cp932', 'euc-jp', 'iso-2022-jp']
    
    infile = None
    for encoding in encodings_to_try:
        try:
            infile = open(input_file, 'r', encoding=encoding)
            infile.read(100)  # Test read
            infile.seek(0)  # Reset to beginning
            print(f"Using encoding: {encoding}")
            break
        except UnicodeDecodeError:
            if infile:
                infile.close()
            continue
    
    if not infile:
        raise ValueError("Could not determine file encoding")
    
    with infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=mcp_header)
        writer.writeheader()
        
        for row in reader:
            try:
                # Extract frequency and convert to float
                frequency = float(row['Frequency'])
                
                # Determine band based on frequency
                if 28 <= frequency <= 30:
                    band = '10m'
                elif 50 <= frequency <= 54:
                    band = '6m'  
                elif 144 <= frequency <= 148:
                    band = '2m'
                elif 430 <= frequency <= 450:
                    band = '70cm'
                elif 1240 <= frequency <= 1300:
                    band = '23cm'
                else:
                    band = 'unknown'
                
                # Calculate offset and determine duplex
                try:
                    offset_mhz = float(row['Offset'])
                    if row['Dup'] == 'DUP+':
                        dup = '+'
                        freq_rx = frequency - offset_mhz
                    elif row['Dup'] == 'DUP-':
                        dup = '-'
                        freq_rx = frequency + offset_mhz
                    else:
                        dup = ''
                        freq_rx = frequency
                except (ValueError, KeyError):
                    dup = ''
                    freq_rx = frequency
                    offset_mhz = 0
                
                # Determine mode
                mode_str = row.get('Mode', 'FM')
                is_dstar = (mode_str == 'DV')
                is_fm = (mode_str == 'FM' or mode_str == 'DV')  # D-STAR can do FM too
                
                # Extract CTCSS
                ctcss_tone = row.get('Repeater Tone', '88.5Hz').replace('Hz', '')
                try:
                    ctcss_freq = float(ctcss_tone)
                except ValueError:
                    ctcss_freq = 88.5
                
                # Create MCP format row
                mcp_row = {
                    'callsign': row.get('Repeater Call Sign', '').replace(' A', '').replace(' B', '').strip(),
                    'name': row.get('Name', '').strip(),
                    'band': band,
                    'freq_tx': frequency,
                    'freq_rx': freq_rx,
                    'ctcss_tx': ctcss_freq if row.get('TONE') != 'OFF' else '',
                    'ctcss_rx': ctcss_freq if row.get('TONE') != 'OFF' else '',
                    'c4fm': False,
                    'dmr': False,
                    'dmr_id': '',
                    'dmr_cc': '',
                    'dstar': is_dstar,
                    'dstar_rpt1': row.get('Repeater Call Sign', '') if is_dstar else '',
                    'dstar_rpt2': row.get('Gateway Call Sign', '') if is_dstar else '',
                    'fm': is_fm,
                    'landmark': row.get('Sub Name', '').strip(),
                    'state': row.get('Group Name', '').strip(),
                    'country': 'Japan',
                    'country_code': 'JPN',
                    'loc_exact': row.get('Position') == 'Exact',
                    'lat': float(row.get('Latitude', 0)),
                    'long': float(row.get('Longitude', 0)),
                    'locator': '',  # Could calculate from lat/long if needed
                    'sea_level': '',
                    'skip': False,
                    'scan_group': '',
                    'source_id': 'japan-icom-csv',
                    'source_name': 'Japan Icom Repeater CSV',
                    'source_provider': 'Icom Japan',
                    'source_type': 'static',
                    'source_license': '',
                    'source_url': 'https://www.icom.co.jp/support/drivers/8557/',
                    'offset': abs(offset_mhz),
                    'dup': dup,
                    'ctcss': row.get('TONE') != 'OFF',
                    'simplex': (dup == ''),
                    'split': False,
                    'multimode': is_dstar,  # D-STAR can do multiple modes
                    'name_formatted': row.get('Name', '').strip(),
                    'distance': '',
                    'heading': ''
                }
                
                writer.writerow(mcp_row)
                processed_count += 1
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return processed_count

def main():
    input_file = '/mnt/c/Users/sebastian.schiegl/Github/memoryicomscript/rptexample.csv'
    output_file = 'japan_tmp_repeaters.csv'
    
    print("Converting Japanese repeater CSV to memory-channels-processor format...")
    
    count = convert_japanese_csv_to_mcp_format(input_file, output_file)
    
    print(f"✅ Converted {count} Japanese repeaters")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()