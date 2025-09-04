#!/usr/bin/env python3
"""
Combined FM and D-STAR Repeaters CSV Creator
Creates single CSV files per country containing both FM and D-STAR repeaters
"""

import csv
from pathlib import Path

def create_combined_country_csv(country_name, fm_file, dstar_file, output_file):
    """Combine FM and D-STAR repeaters for a country into one CSV."""
    
    header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    total_count = 0
    
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        
        # Add FM repeaters first
        if Path(fm_file).exists():
            with open(fm_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    writer.writerow(row)
                    total_count += 1
        
        # Add D-STAR repeaters
        if Path(dstar_file).exists():
            with open(dstar_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    writer.writerow(row)
                    total_count += 1
    
    return total_count

def main():
    print("🌍 Creating combined FM and D-STAR repeater files by country...")
    
    # Austria
    print("\n🇦🇹 Creating Austrian combined repeaters...")
    austrian_count = create_combined_country_csv(
        "Austria",
        "austrian_fm_repeaters.csv",
        "austrian_dstar_repeaters.csv",
        "austrian_all_repeaters.csv"
    )
    print(f"✅ Created {austrian_count} total Austrian repeaters")
    
    # Slovakia
    print("\n🇸🇰 Creating Slovak combined repeaters...")
    slovak_count = create_combined_country_csv(
        "Slovakia", 
        "slovak_fm_repeaters.csv",
        "slovak_dstar_repeaters.csv",
        "slovak_all_repeaters.csv"
    )
    print(f"✅ Created {slovak_count} total Slovak repeaters")
    
    # Singapore
    print("\n🇸🇬 Creating Singapore combined repeaters...")
    singapore_count = create_combined_country_csv(
        "Singapore",
        "singapore_fm_repeaters.csv", 
        "singapore_dstar_repeaters.csv",
        "singapore_all_repeaters.csv"
    )
    print(f"✅ Created {singapore_count} total Singapore repeaters")
    
    # Create master combined file
    print("\n🌍 Creating master combined file...")
    
    header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    with open('all_repeaters_combined.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        
        # Combine all country files
        for filename in ['austrian_all_repeaters.csv', 'slovak_all_repeaters.csv', 'singapore_all_repeaters.csv']:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        writer.writerow(row)
    
    total_all = austrian_count + slovak_count + singapore_count
    print(f"✅ Master combined file created with {total_all} total repeaters")
    
    print("\n📁 Generated combined files:")
    print("- austrian_all_repeaters.csv (FM + D-STAR)")
    print("- slovak_all_repeaters.csv (FM + D-STAR)") 
    print("- singapore_all_repeaters.csv (FM + D-STAR)")
    print("- all_repeaters_combined.csv (All countries)")
    
    print("\n🎯 All files ready for Icom ID-52PLUS!")

if __name__ == "__main__":
    main()