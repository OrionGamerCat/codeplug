#!/usr/bin/env python3
"""
Filter CSV files to remove repeaters outside standard VHF/UHF amateur bands
Keeps only 2m (144-146 MHz), 70cm (430-440 MHz), and 23cm (1240-1300 MHz) bands
"""

import csv
from pathlib import Path

def filter_amateur_bands(input_file, output_file):
    """Filter CSV to keep only standard amateur radio bands."""
    
    kept_count = 0
    filtered_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                frequency = float(row['Frequency'])
                
                # Check if frequency is in standard amateur bands
                if (144 <= frequency <= 146) or \
                   (430 <= frequency <= 440) or \
                   (1240 <= frequency <= 1300) or \
                   (2300 <= frequency <= 2450):
                    writer.writerow(row)
                    kept_count += 1
                else:
                    print(f"Filtered out: {frequency} MHz ({row.get('Repeater Call Sign', 'Unknown')})")
                    filtered_count += 1
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return kept_count, filtered_count

def main():
    print("📡 Filtering CSV files for standard amateur radio bands...")
    
    files_to_filter = [
        'austrian_all_repeaters.csv',
        'slovak_all_repeaters.csv', 
        'singapore_all_repeaters.csv',
        'all_repeaters_combined.csv'
    ]
    
    total_kept = 0
    total_filtered = 0
    
    for filename in files_to_filter:
        if Path(filename).exists():
            print(f"\n📻 Processing {filename}...")
            output_filename = filename.replace('.csv', '_filtered.csv')
            
            kept_count, filtered_count = filter_amateur_bands(filename, output_filename)
            total_kept += kept_count
            total_filtered += filtered_count
            
            print(f"✅ Kept: {kept_count}, Filtered: {filtered_count} -> {output_filename}")
        else:
            print(f"⚠️ File not found: {filename}")
    
    print(f"\n🎯 Total kept: {total_kept}, Total filtered: {total_filtered}")
    print("✅ All CSV files filtered for standard VHF/UHF amateur bands!")
    print("\n📋 Standard bands kept:")
    print("- 2m: 144-146 MHz")  
    print("- 70cm: 430-440 MHz")
    print("- 23cm: 1240-1300 MHz")
    print("- 13cm: 2300-2450 MHz")

if __name__ == "__main__":
    main()