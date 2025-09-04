#!/usr/bin/env python3
"""
Fix umlaut display issues in Icom CSV files
Converts German umlauts and special characters to ASCII equivalents
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

def fix_csv_umlauts(input_file, output_file):
    """Fix umlauts in all text fields of a CSV file."""
    
    fixed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for row in reader:
            original_row = dict(row)
            
            # Fix umlauts in text fields
            for field in ['Name', 'Sub Name', 'Group Name']:
                if field in row and row[field]:
                    original_text = row[field]
                    fixed_text = convert_umlauts(original_text)
                    if original_text != fixed_text:
                        print(f"Fixed: '{original_text}' -> '{fixed_text}'")
                        fixed_count += 1
                    row[field] = fixed_text
            
            writer.writerow(row)
    
    return fixed_count

def main():
    print("🔧 Fixing umlaut display issues for Icom ID-52PLUS...")
    
    files_to_fix = [
        'austrian_all_repeaters_filtered.csv',
        'slovak_all_repeaters_filtered.csv', 
        'singapore_all_repeaters_filtered.csv',
        'all_repeaters_combined_filtered.csv',
        'vienna_fm_radio_icom.csv',
        'pmr_channels_icom.csv'
    ]
    
    total_fixed = 0
    
    for filename in files_to_fix:
        if Path(filename).exists():
            print(f"\n📝 Processing {filename}...")
            output_filename = filename.replace('.csv', '_ascii.csv')
            
            fixed_count = fix_csv_umlauts(filename, output_filename)
            total_fixed += fixed_count
            
            print(f"✅ Fixed {fixed_count} umlauts -> {output_filename}")
        else:
            print(f"⚠️ File not found: {filename}")
    
    print(f"\n🎯 Total umlauts fixed: {total_fixed}")
    print("✅ All CSV files converted to ASCII-compatible format!")
    print("\n📋 Umlaut Conversions Applied:")
    print("- ä/Ä -> ae/Ae")
    print("- ö/Ö -> oe/Oe") 
    print("- ü/Ü -> ue/Ue")
    print("- ß -> ss")
    print("- Special characters -> ASCII equivalents")

if __name__ == "__main__":
    main()