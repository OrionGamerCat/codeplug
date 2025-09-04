#!/usr/bin/env python3
"""
SOTA Summits GPS Format Generator
Creates GPS format files like gpsexample.csv with groups X (Austria), Y (Slovakia), Z (Singapore)
Compatible with POTA GPS format for consistent Icom ID-52PLUS usage
"""

import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def convert_umlauts(text):
    """Convert German, Slovak and special characters to ASCII equivalents."""
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

def generate_sota_data():
    """Generate SOTA summits data using memory-channels-processor."""
    
    # Try to find memory-channels-processor
    memory_processor = None
    
    if subprocess.run(['which', 'memory-channels-processor'], capture_output=True).returncode == 0:
        memory_processor = 'memory-channels-processor'
    elif Path('/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe').exists():
        memory_processor = '/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe'
    else:
        print("Error: memory-channels-processor not found")
        print("Please install memory-channels-processor or ensure it's in your PATH")
        return False
    
    print("Generating SOTA summits data...")
    
    try:
        result = subprocess.run([
            memory_processor,
            '--source', 'sota-summits',
            '--output-file', 'sota_summits.csv',
            '--country', 'AUT', 'SVK', 'SGP',
            '--output-format', 'csv'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("SOTA summits data generated successfully")
            return True
        else:
            print(f"Error generating SOTA data: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Timeout generating SOTA data")
        return False
    except Exception as e:
        print(f"Error running memory-channels-processor: {e}")
        return False

def create_sota_gps_files():
    """Create SOTA summits GPS format files by country."""
    
    print("SOTA Summits GPS Format Generator")
    print("=" * 60)
    
    # Group assignments compatible with POTA format
    group_map = {
        'AUT': {'group': 'X', 'group_name': 'SOTA-AT'},
        'SVK': {'group': 'Y', 'group_name': 'SOTA-SK'},
        'SGP': {'group': 'Z', 'group_name': 'SOTA-SG'}
    }
    
    # Check if SOTA data exists, generate if needed
    if not Path('sota_summits.csv').exists():
        print("SOTA data not found, generating...")
        if not generate_sota_data():
            print("Failed to generate SOTA data")
            return 0
    
    # Create output directories
    Path('SOTA-GPS').mkdir(exist_ok=True)
    Path('SOTA-GPS/Austria').mkdir(exist_ok=True)
    Path('SOTA-GPS/Slovakia').mkdir(exist_ok=True)
    Path('SOTA-GPS/Singapore').mkdir(exist_ok=True)
    
    current_date = datetime.now().strftime('%m/%d/%Y')
    country_totals = {}
    
    # Read and process SOTA data
    country_summits = {'AUT': [], 'SVK': [], 'SGP': []}
    
    try:
        with open('sota_summits.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                country_code = row.get('country_code', '').upper()
                if country_code not in group_map:
                    continue
                
                try:
                    name = row.get('name', '')
                    lat = float(row.get('lat', 0))
                    lon = float(row.get('long', 0))
                    
                    if not name or lat == 0 or lon == 0:
                        continue
                    
                    # Clean name for display
                    clean_name = convert_umlauts(name)
                    
                    # Format for GPS display (summit name, truncate if needed)
                    display_name = clean_name
                    if len(display_name) > 50:
                        display_name = display_name[:47] + "..."
                    
                    group_info = group_map[country_code]
                    
                    gps_entry = {
                        'Group': group_info['group'],
                        'Group Name': group_info['group_name'],
                        'Name': display_name,
                        'Date': current_date,
                        'Time': '00:00:00',
                        'Latitude': lat,
                        'Longitude': lon,
                        'Altitude': '',
                        'Alarm': 'OFF'
                    }
                    
                    country_summits[country_code].append(gps_entry)
                    
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid summit entry: {e}")
                    continue
                    
    except FileNotFoundError:
        print("Error: sota_summits.csv not found")
        return 0
    except Exception as e:
        print(f"Error reading SOTA data: {e}")
        return 0
    
    total_summits = 0
    
    # Write country files
    for country_code, summits in country_summits.items():
        if not summits:
            continue
            
        country_name = {'AUT': 'Austria', 'SVK': 'Slovakia', 'SGP': 'Singapore'}[country_code]
        group_info = group_map[country_code]
        
        # Write country-wide file
        country_filename = f"SOTA-GPS/sota_{country_code.lower()}_all.csv"
        write_gps_csv(country_filename, summits)
        
        # Create region-specific files (simplified - one file per country for SOTA)
        region_filename = f"SOTA-GPS/{country_name}/sota_{country_code.lower()}.csv"
        write_gps_csv(region_filename, summits)
        
        country_totals[country_code] = {
            'name': country_name,
            'summits': len(summits),
            'group': group_info['group']
        }
        
        total_summits += len(summits)
        print(f"Created {country_name}: {len(summits)} summits (Group {group_info['group']})")
    
    # Create master combined file
    print("Creating master combined file...")
    all_summits = []
    for summits in country_summits.values():
        all_summits.extend(summits)
    
    if all_summits:
        write_gps_csv('SOTA-GPS/sota_all_countries.csv', all_summits)
        print(f"Created master file with {len(all_summits)} summits")
    
    # Print summary
    print(f"\nSuccessfully processed {total_summits} SOTA summits")
    for country_code, stats in country_totals.items():
        print(f"   {stats['name']}: {stats['summits']} summits (Group {stats['group']})")
    
    return total_summits

def write_gps_csv(filename, summits_data):
    """Write summits data in GPS CSV format."""
    if not summits_data:
        return
    
    # GPS CSV header (same as POTA format)
    fieldnames = ['Group', 'Group Name', 'Name', 'Date', 'Time', 'Latitude', 'Longitude', 'Altitude', 'Alarm']
    
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for summit in summits_data:
            writer.writerow(summit)

def main():
    print("SOTA Summits GPS Format Generator")
    print("Uses memory-channels-processor to create GPS format files")
    print("=" * 70)
    print("Target Countries:")
    print("   Austria (Group X)")
    print("   Slovakia (Group Y)") 
    print("   Singapore (Group Z)")
    print("Compatible with POTA GPS format")
    print()
    
    summit_count = create_sota_gps_files()
    
    if summit_count > 0:
        print("\nGenerated files structure:")
        print("SOTA-GPS/")
        print("├── sota_aut_all.csv       # All Austria summits")
        print("├── sota_svk_all.csv       # All Slovakia summits") 
        print("├── sota_sgp_all.csv       # All Singapore summits")
        print("├── sota_all_countries.csv # Combined master file")
        print("├── Austria/")
        print("│   └── sota_aut.csv       # Austria summits")
        print("├── Slovakia/")
        print("│   └── sota_svk.csv       # Slovakia summits")
        print("└── Singapore/")
        print("    └── sota_sgp.csv       # Singapore summits")
        
        print("\nGPS Format Features:")
        print("- gpsexample.csv compatible format")
        print("- Group letters: X (Austria), Y (Slovakia), Z (Singapore)")
        print("- Compatible with POTA GPS format")
        print("- ASCII-converted names for radio display")
        print("- Current date timestamps")
        print("- Precise GPS coordinates")
        
        print("\nUsage with Icom ID-52PLUS:")
        print("1. Import individual country files for specific areas")
        print("2. Or import master file for all countries")
        print("3. Groups X/Y/Z complement POTA groups U/V/W")
        
        print("\nPerfect for SOTA activations and navigation!")
        print("Compatible with existing POTA GPS format")
        
    else:
        print("\nNo SOTA summits data generated")

if __name__ == "__main__":
    main()