#!/usr/bin/env python3
"""
Icom Vienna FM Radio CSV Creator
Creates Icom ID-52PLUS compatible CSV file for FM radio stations around Vienna
"""

import csv
import sys
from pathlib import Path
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km."""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def convert_vienna_radio_to_icom_format(input_file, output_file, group_number, group_name):
    """Convert Vienna FM radio stations to Icom format."""
    
    # Vienna coordinates (city center)
    vienna_lat = 48.2082
    vienna_lon = 16.3738
    max_distance = 150  # 150 km radius around Vienna
    
    # Icom CSV header
    icom_header = [
        'Group No', 'Group Name', 'Name', 'Sub Name', 'Repeater Call Sign',
        'Gateway Call Sign', 'Frequency', 'Dup', 'Offset', 'Mode', 'TONE',
        'Repeater Tone', 'RPT1USE', 'Position', 'Latitude', 'Longitude', 'UTC Offset'
    ]
    
    # Priority stations and major networks (higher score = more important)
    priority_stations = {
        'Ö1': 100, 'Ö3': 95, 'FM4': 90, 'Kronehit': 85, 'ENERGY': 80, 'oe24': 75,
        'Hitradio Ö3': 70, 'Radio Wien': 65, 'ROCK ANTENNE': 60, 'Life Radio': 55,
        'Stadtradio Krems': 95  # Add Stadtradio Krems with high priority
    }
    
    stations = []
    seen_stations = set()  # Track unique station names to avoid duplicates
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            try:
                # Get coordinates
                lat = float(row.get('lat', 0))
                lon = float(row.get('long', 0))
                
                # Calculate distance from Vienna
                distance = calculate_distance(vienna_lat, vienna_lon, lat, lon)
                
                # Filter for Vienna area (within max_distance km)
                if distance > max_distance:
                    continue
                
                # Get frequency
                frequency = float(row['freq_rx'])
                
                # Only include FM broadcast band (87.5 - 108 MHz)
                if not (87.5 <= frequency <= 108.0):
                    continue
                
                # Get station name and location
                station_name = row.get('name', '').strip()
                location = row.get('landmark', '').strip()
                state = row.get('state', '').strip()
                
                # Format name
                if not station_name:
                    station_name = f"FM {frequency}"
                
                # Skip duplicates - use station name as key
                station_key = station_name.lower().replace(' ', '')
                if station_key in seen_stations:
                    continue
                seen_stations.add(station_key)
                
                # Calculate priority score
                priority_score = priority_stations.get(station_name, 0)
                # Add distance bonus (closer = higher score)
                distance_bonus = max(0, 50 - distance)
                total_score = priority_score + distance_bonus
                
                # Format sub name with location info
                sub_name = f"{location}" if location else f"{state}" if state else "Austria"
                
                # Store station data with score
                station_data = {
                    'score': total_score,
                    'name': station_name,
                    'sub_name': sub_name,
                    'frequency': frequency,
                    'lat': lat,
                    'lon': lon,
                    'loc_exact': row.get('loc_exact', '').lower() == 'true'
                }
                
                stations.append(station_data)
                
            except (ValueError, KeyError, TypeError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    # Sort by score (highest first) and take top 50
    stations.sort(key=lambda x: x['score'], reverse=True)
    top_stations = stations[:50]
    
    # Write to CSV
    processed_count = 0
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=icom_header)
        writer.writeheader()
        
        for station in top_stations:
            icom_row = {
                'Group No': group_number,
                'Group Name': group_name,
                'Name': station['name'],
                'Sub Name': station['sub_name'],
                'Repeater Call Sign': '',
                'Gateway Call Sign': '',
                'Frequency': station['frequency'],
                'Dup': '',
                'Offset': 0.0,
                'Mode': 'FM',
                'TONE': 'OFF',
                'Repeater Tone': '88.5Hz',
                'RPT1USE': 'NO',
                'Position': 'Exact' if station['loc_exact'] else 'Approximate',
                'Latitude': station['lat'],
                'Longitude': station['lon'],
                'UTC Offset': '+1:00'
            }
            
            writer.writerow(icom_row)
            processed_count += 1
    
    return processed_count

def main():
    if not Path('vienna_fm_radio.csv').exists():
        print("❌ Vienna FM radio data not found - please generate it first")
        return
    
    print("📻 Creating Vienna FM radio stations CSV for Icom ID-52PLUS...")
    
    radio_count = convert_vienna_radio_to_icom_format(
        'vienna_fm_radio.csv',
        'vienna_fm_radio_icom.csv',
        81,  # Use group 81 for Vienna FM radio
        'Vienna-FM-Radio'
    )
    
    # Add Stadtradio Krems manually if not found in data
    stadtradio_added = False
    try:
        with open('vienna_fm_radio_icom.csv', 'r', encoding='utf-8') as check_file:
            content = check_file.read()
            if 'Stadtradio Krems' not in content:
                # Add Stadtradio Krems manually
                with open('vienna_fm_radio_icom.csv', 'a', encoding='utf-8', newline='') as append_file:
                    writer = csv.writer(append_file)
                    # Stadtradio Krems on 97.2 MHz
                    writer.writerow([81, 'Vienna-FM-Radio', 'Stadtradio Krems', 'Krems', '', '', 97.2, '', 0.0, 'FM', 'OFF', '88.5Hz', 'NO', 'Exact', 48.408, 15.61, '+1:00'])
                    radio_count += 1
                    stadtradio_added = True
                    print("✅ Added Stadtradio Krems manually")
    except:
        pass
    
    print(f"✅ Created {radio_count} top Vienna area FM radio stations (no duplicates)")
    print("\n📁 Generated file:")
    print("- vienna_fm_radio_icom.csv")
    print("\n🎯 Vienna FM radio stations ready for Icom ID-52PLUS!")
    print("\n📋 Vienna FM Radio Details:")
    print("- Top 50 biggest FM stations (no duplicates)")
    print("- Frequency Range: 87.5 - 108 MHz (FM Broadcast Band)")
    print("- Coverage: 150 km radius around Vienna")
    print("- Group: 81 (Vienna-FM-Radio)")
    print("- Prioritizes major networks and Vienna-area stations")
    if stadtradio_added:
        print("- Includes Stadtradio Krems (97.2 MHz)")

if __name__ == "__main__":
    main()