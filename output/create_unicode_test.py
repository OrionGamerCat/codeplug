#!/usr/bin/env python3
"""
Create Unicode test CSV for Icom ID-52PLUS umlaut display testing
Tests different Unicode encoding approaches for German umlauts
"""

import csv
from pathlib import Path

def create_unicode_test_csv():
    """Create a test CSV with various Unicode encoding approaches."""
    
    # Test data with different Unicode representations
    test_data = [
        {
            'name': 'Ö3 (UTF-8)',
            'sub_name': 'Österreich Test',
            'frequency': 89.4,
            'encoding': 'UTF-8 Normal'
        },
        {
            'name': 'Ö3 (Composed)',
            'sub_name': 'Österreich NFC',
            'frequency': 89.5,
            'encoding': 'Unicode NFC'
        },
        {
            'name': 'O\u0308\u0033 (Decomposed)',  # Ö as O + combining diaeresis
            'sub_name': 'O\u0308sterreich NFD',
            'frequency': 89.6,
            'encoding': 'Unicode NFD'
        },
        {
            'name': 'Radio Kärnten',
            'sub_name': 'äöüß Test',
            'frequency': 88.8,
            'encoding': 'All Umlauts'
        },
        {
            'name': 'Grün Weiß',
            'sub_name': 'ü-Test Grün',
            'frequency': 95.0,
            'encoding': 'ü and ü'
        },
        {
            'name': 'Heiß & Süß',
            'sub_name': 'ß-Test Weiß',
            'frequency': 96.0,
            'encoding': 'ß Tests'
        }
    ]
    
    # Create test CSV in standard Icom format
    header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    # Create UTF-8 encoded file (default)
    with open('unicode_umlaut_test_utf8.csv', 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        
        for i, test in enumerate(test_data):
            row = {
                'Group No': 90,
                'Group Name': 'Unicode-Test',
                'Name': test['name'],
                'Sub Name': f"{test['sub_name']} ({test['encoding']})",
                'Repeater Call Sign': '',
                'Gateway Call Sign': '',
                'Frequency': test['frequency'],
                'Dup': '',
                'Offset': 0.0,
                'Mode': 'FM',
                'TONE': 'OFF',
                'Repeater Tone': '88.5Hz',
                'RPT1USE': 'NO',
                'Position': 'Exact',
                'Latitude': 48.2 + (i * 0.1),
                'Longitude': 16.4 + (i * 0.1),
                'UTC Offset': '+1:00'
            }
            writer.writerow(row)
    
    # Create UTF-16 encoded file (alternative encoding)
    with open('unicode_umlaut_test_utf16.csv', 'w', encoding='utf-16', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        
        for i, test in enumerate(test_data):
            row = {
                'Group No': 91,
                'Group Name': 'Unicode-UTF16',
                'Name': test['name'],
                'Sub Name': f"{test['sub_name']} (UTF-16)",
                'Repeater Call Sign': '',
                'Gateway Call Sign': '',
                'Frequency': test['frequency'] + 1.0,
                'Dup': '',
                'Offset': 0.0,
                'Mode': 'FM',
                'TONE': 'OFF',
                'Repeater Tone': '88.5Hz',
                'RPT1USE': 'NO',
                'Position': 'Exact',
                'Latitude': 48.3 + (i * 0.1),
                'Longitude': 16.5 + (i * 0.1),
                'UTC Offset': '+1:00'
            }
            writer.writerow(row)
    
    # Create ISO-8859-1 (Latin-1) encoded file
    try:
        with open('unicode_umlaut_test_latin1.csv', 'w', encoding='iso-8859-1', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            
            for i, test in enumerate(test_data):
                # Only include characters that exist in Latin-1
                name = test['name'].replace('\u0308', '')  # Remove combining diaeresis
                sub_name = test['sub_name'].replace('\u0308', '').replace(' NFD', ' Latin1')
                
                row = {
                    'Group No': 92,
                    'Group Name': 'Unicode-Latin1',
                    'Name': name,
                    'Sub Name': f"{sub_name} (Latin-1)",
                    'Repeater Call Sign': '',
                    'Gateway Call Sign': '',
                    'Frequency': test['frequency'] + 2.0,
                    'Dup': '',
                    'Offset': 0.0,
                    'Mode': 'FM',
                    'TONE': 'OFF',
                    'Repeater Tone': '88.5Hz',
                    'RPT1USE': 'NO',
                    'Position': 'Exact',
                    'Latitude': 48.4 + (i * 0.1),
                    'Longitude': 16.6 + (i * 0.1),
                    'UTC Offset': '+1:00'
                }
                writer.writerow(row)
    except UnicodeEncodeError:
        print("⚠️ Some characters cannot be encoded in Latin-1")
    
    print("✅ Created Unicode test files:")
    print("- unicode_umlaut_test_utf8.csv (UTF-8 encoding)")
    print("- unicode_umlaut_test_utf16.csv (UTF-16 encoding)")
    print("- unicode_umlaut_test_latin1.csv (Latin-1 encoding)")
    
    return len(test_data)

def main():
    print("🧪 Creating Unicode umlaut test files for Icom ID-52PLUS...")
    
    test_count = create_unicode_test_csv()
    
    print(f"\n🎯 Created {test_count} test entries per encoding")
    print("\n📋 Test Instructions:")
    print("1. Import each CSV file into your Icom ID-52PLUS")
    print("2. Check how the umlauts display on the radio screen:")
    print("   - Group 90: UTF-8 encoding test")
    print("   - Group 91: UTF-16 encoding test") 
    print("   - Group 92: Latin-1 encoding test")
    print("3. Compare display quality:")
    print("   - Normal umlauts: ä, ö, ü, ß")
    print("   - Composed vs Decomposed Unicode")
    print("   - Different encoding approaches")
    print("\n💡 If any version displays correctly, we can update all CSV files!")
    print("🔍 Look for: Ö3, Österreich, Kärnten, Grün Weiß, ß characters")

if __name__ == "__main__":
    main()