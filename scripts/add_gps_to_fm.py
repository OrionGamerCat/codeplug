#!/usr/bin/env python3
"""
GPS-Enhanced FM Repeater CSV Generator
Adds GPS coordinates to Icom ID-52PLUS FM repeater memory channels
"""

import csv
import sys
import argparse
from pathlib import Path

def read_csv_as_dict(filename, key_column):
    """Read CSV file and return as dictionary keyed by specified column."""
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                key = row[key_column]
                data[key] = row
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return {}
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}
    return data

def read_intermediate_csv(filename):
    """Read the intermediate repeater CSV with GPS data."""
    gps_data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                callsign = row['callsign']
                gps_data[callsign] = {
                    'lat': row.get('lat', ''),
                    'long': row.get('long', ''),
                    'landmark': row.get('landmark', ''),
                    'locator': row.get('locator', '')
                }
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}
    return gps_data

def enhance_fm_csv_with_gps(fm_csv_file, intermediate_csv_file, output_file):
    """Add GPS coordinates to FM repeater CSV file."""
    
    # Read GPS data from intermediate file
    print(f"Reading GPS data from {intermediate_csv_file}...")
    gps_data = read_intermediate_csv(intermediate_csv_file)
    
    if not gps_data:
        print("No GPS data found!")
        return False
    
    print(f"Found GPS data for {len(gps_data)} repeaters")
    
    # Process FM CSV file
    try:
        with open(fm_csv_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter=';')
            original_fieldnames = reader.fieldnames
            
            # Add GPS columns to fieldnames
            new_fieldnames = list(original_fieldnames) + ['Latitude', 'Longitude', 'Locator', 'Landmark']
            
            rows_processed = 0
            rows_with_gps = 0
            
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=new_fieldnames, delimiter=';')
                writer.writeheader()
                
                for row in reader:
                    rows_processed += 1
                    
                    # Extract callsign from RPT1 Call Sign column or Name column
                    callsign = row.get('RPT1 Call Sign', '').strip()
                    if not callsign:
                        callsign = row.get('Name', '').strip()
                    
                    # Add GPS data if available
                    if callsign in gps_data:
                        gps_info = gps_data[callsign]
                        row['Latitude'] = gps_info['lat']
                        row['Longitude'] = gps_info['long']
                        row['Locator'] = gps_info['locator']
                        row['Landmark'] = gps_info['landmark']
                        rows_with_gps += 1
                    else:
                        row['Latitude'] = ''
                        row['Longitude'] = ''
                        row['Locator'] = ''
                        row['Landmark'] = ''
                    
                    writer.writerow(row)
            
            print(f"Processed {rows_processed} memory channels")
            print(f"Added GPS data to {rows_with_gps} repeaters")
            print(f"Enhanced file saved as: {output_file}")
            return True
            
    except Exception as e:
        print(f"Error processing files: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Add GPS coordinates to Icom FM repeater CSV files')
    parser.add_argument('fm_csv', help='Input FM repeater CSV file')
    parser.add_argument('intermediate_csv', help='Intermediate CSV file with GPS data')
    parser.add_argument('output_csv', help='Output enhanced CSV file')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not Path(args.fm_csv).exists():
        print(f"Error: FM CSV file {args.fm_csv} does not exist")
        sys.exit(1)
        
    if not Path(args.intermediate_csv).exists():
        print(f"Error: Intermediate CSV file {args.intermediate_csv} does not exist")
        sys.exit(1)
    
    print(f"GPS-Enhanced FM Repeater CSV Generator")
    print(f"Input FM file: {args.fm_csv}")
    print(f"GPS data source: {args.intermediate_csv}")
    print(f"Output file: {args.output_csv}")
    print("-" * 50)
    
    success = enhance_fm_csv_with_gps(args.fm_csv, args.intermediate_csv, args.output_csv)
    
    if success:
        print("\n✅ GPS enhancement completed successfully!")
        print("\nThe enhanced CSV file includes these additional columns:")
        print("- Latitude: GPS latitude coordinate")
        print("- Longitude: GPS longitude coordinate") 
        print("- Locator: Maidenhead locator")
        print("- Landmark: Repeater location name")
        print("\nYou can now import this enhanced file into your Icom ID-52PLUS programming software.")
    else:
        print("\n❌ GPS enhancement failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()