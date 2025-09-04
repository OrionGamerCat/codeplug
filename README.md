# Icom ID-52PLUS Codeplug Generator Suite

[![Generate CSV Files](https://github.com/username/memoryicomscript/actions/workflows/generate-csvs.yml/badge.svg)](https://github.com/username/memoryicomscript/actions/workflows/generate-csvs.yml)
[![Test Scripts](https://github.com/username/memoryicomscript/actions/workflows/test.yml/badge.svg)](https://github.com/username/memoryicomscript/actions/workflows/test.yml)

A comprehensive collection of tools for generating codeplugs, GPS waypoints, and data files for the Icom ID-52PLUS transceiver. This suite provides automated data collection and formatting for amateur radio repeaters, POTA parks, SOTA summits, and more.

**Latest Data Update**: Generated automatically every Sunday at 06:00 UTC

## Features

### Repeater Data Management
- **Austrian Repeaters**: Separated by federal states (OE1-OE9 callsign prefixes)
- **Slovak Repeaters**: Complete 2m/70cm repeater database
- **Singapore Repeaters**: VHF/UHF with GPS coordinates
- **Japanese Repeaters**: Official Icom CSV integration
- **D-STAR Support**: Separate D-STAR repeater files with gateway configuration
- **FM/Mixed Mode**: Both FM and D-STAR combined by country

### POTA (Parks on the Air) Integration
- **Complete POTA Database**: All registered parks (not just active ones)
- **API-Powered**: Direct integration with official POTA API
- **GPS Format**: gpsexample.csv compatible files
- **Location-Specific Files**: Separate files for each region (AT-WI, SK-BC, etc.)
- **Country Groups**: U (Austria), V (Slovakia), W (Singapore)
- **684 Parks Total**: 373 Austria + 247 Slovakia + 64 Singapore

### SOTA (Summits on the Air) Support
- **GPS Waypoints**: All SOTA summits with precise coordinates
- **Multi-Country**: Austria, Slovakia, Singapore
- **Elevation Data**: Summit heights included

### Specialized Channels
- **PMR Channels**: Complete PMR446 channel list
- **Vienna FM Radio**: Top 50 local FM stations + Stadtradio Krems
- **ASCII Conversion**: Proper character handling for radio display

### Technical Features
- **GPS Enhancement**: Adds GPS coordinates to FM repeater entries
- **Character Encoding**: Handles German/Slovak umlauts and special characters
- **Band Filtering**: Automatic filtering of out-of-band frequencies
- **Multiple Formats**: CSV, GPS, and Icom native formats
- **SD Card Organization**: Directory structure for easy Icom ID-52PLUS deployment

## Repository Structure

```
memoryicomscript/
├── scripts/                           # Python generators and utilities
│   ├── create_pota_gps_format.py      # POTA GPS format generator (main)
│   ├── create_pota_parks_api.py       # POTA API integration
│   ├── create_icom_sota_csv.py        # SOTA summits GPS waypoints
│   ├── create_icom_vienna_radio_csv.py # Vienna FM radio stations
│   └── ... (additional utility scripts)
├── examples/                          # Example CSV files
│   ├── gpsexample.csv                 # GPS format template
│   ├── fmexample.csv                  # FM repeater template  
│   └── rptexample.csv                 # D-STAR repeater template
├── output/
│   ├── final-exports/                 # Ready-to-use files
│   │   └── POTA-GPS/                  # Complete POTA GPS files
│   ├── generated-data/                # Intermediate processing files
│   └── ID-52/                         # Organized SD card structure
└── generate_icom_id52_codeplug.sh     # Main generation script
```

## Quick Start

### Prerequisites
1. **memory-channels-processor** installed and in PATH
   - Download: https://oe3lrt.gitlab.io/memory-channels-processor/
2. **curl** for API access
3. **Python 3** for advanced generators

### Basic Usage
```bash
# Generate complete codeplug
./generate_icom_id52_codeplug.sh

# Generate POTA parks (recommended)
python3 scripts/create_pota_gps_format.py

# Generate SOTA summits
python3 scripts/create_icom_sota_csv.py
```

## Generated Files Overview

### POTA Parks (GPS Format)
Perfect for POTA hunting and activations:
```
output/final-exports/POTA-GPS/
├── pota_at_all.csv        # All Austria parks (Group U)
├── pota_sk_all.csv        # All Slovakia parks (Group V)  
├── pota_sg_all.csv        # All Singapore parks (Group W)
├── pota_all_countries.csv # Master combined file
├── Austria/
│   ├── AT-WI.csv          # Vienna (18 parks)
│   ├── AT-NO.csv          # Lower Austria (112 parks)
│   └── ... (all 9 Austrian states)
├── Slovakia/
│   ├── SK-BL.csv          # Bratislava region (16 parks)
│   └── ... (all 8 Slovak regions)
└── Singapore/
    ├── SG-CS.csv          # Central Singapore (16 parks)
    └── ... (all 5 Singapore districts)
```

### Repeater Files
- **Austrian**: 9 files by federal state (Groups 35-43)
- **Slovak**: 2m/70cm repeaters (Group 44)
- **Singapore**: VHF/UHF with GPS (Group 45)
- **Japanese**: Official Icom data integration (Group 46)

### GPS Waypoints
- **SOTA Summits**: Groups 50-52
- **Vienna Radio**: Group 81
- **PMR Channels**: Complete PMR446 list

## Advanced Features

### POTA API Integration
The POTA generator uses official POTA API endpoints:
- `https://api.pota.app/programs/locations` - Location discovery
- `https://api.pota.app/location/parks/[ID]` - Park details
- Real-time data with activation statistics
- Grid square to GPS coordinate conversion

### Format Compatibility
- **gpsexample.csv**: Compatible GPS waypoint format
- **fmexample.csv**: FM repeater format with GPS enhancement
- **rptexample.csv**: D-STAR repeater format
- **ASCII Conversion**: Handles special characters for radio display

### Icom ID-52PLUS Specific
- **Group Letters**: Single-letter groups (U, V, W)
- **Compact Names**: Optimized for radio display limits
- **GPS Integration**: Precise coordinates for navigation
- **SD Card Structure**: Organized directories for easy import

## Group Organization

| Group | Type | Content | Count |
|-------|------|---------|--------|
| 35-43 | Repeaters | Austrian states (OE1-OE9) | ~200 |
| 44 | Repeaters | Slovakia 2m/70cm | ~50 |
| 45 | Repeaters | Singapore VHF/UHF | ~5 |
| 46 | Repeaters | Japan (official data) | ~1000 |
| 50-52 | GPS | SOTA summits | ~300 |
| 75-77 | GPS | POTA parks (old format) | 684 |
| U | GPS | POTA Austria parks | 373 |
| V | GPS | POTA Slovakia parks | 247 |  
| W | GPS | POTA Singapore parks | 64 |
| 81 | Radio | Vienna FM stations | 50 |

## Import Instructions

### For Icom ID-52PLUS:
1. Copy files to SD card in organized folders
2. Use CS-ID52 software to import CSV files
3. GPS waypoints appear in GPS menu
4. Repeaters organized by groups for easy access

### Recommended Import Order:
1. `pota_all_countries.csv` - Complete POTA database
2. Country-specific repeater files
3. SOTA summits for your operating area
4. PMR channels and local radio stations

## Data Sources

- **ÖVSV Database**: Austrian repeaters
- **Slovakia Repeater List**: Slovak repeaters  
- **POTA API**: Official Parks on the Air database
- **SOTA Database**: Summits on the Air
- **RTR Database**: Austrian radio stations
- **Icom Official**: Japanese repeater data

## Customization

### Adding Countries:
Edit scripts to include new country codes and API endpoints

### Modifying Groups:
Change group numbers and names in generator scripts

### Custom Filters:
Add band filtering, distance limits, or activity requirements

### Character Sets:
Modify ASCII conversion maps for additional languages

## Important Notes

### POTA Data:
- Updates automatically from official API
- Includes both active and inactive parks
- Grid square coordinates converted to precise GPS
- Run regularly for current activation data

### Encoding:
- All files use ASCII conversion for radio compatibility
- UTF-8 and UTF-16 cause "illegal data" errors
- Special characters properly converted (ä→ae, ö→oe, etc.)

### Frequency Ranges:
- Automatic filtering removes out-of-band frequencies
- Uses RX frequencies for proper radio operation
- Band-specific filtering (2m, 70cm, 23cm, etc.)

## Troubleshooting

### Common Issues:
- **"illegal data" error**: File encoding issue, use ASCII version
- **Missing coordinates**: GPS enhancement may be required
- **API timeout**: Run script again, includes retry logic
- **Empty files**: Check internet connection and API availability

### Debug Mode:
Run scripts with verbose output to identify specific issues

## License

This project is provided for amateur radio use. Please respect:
- POTA API terms of service
- Individual data source licensing
- Amateur radio band plans and regulations

## Contributing

Contributions welcome for:
- Additional country support
- New data source integration  
- Format improvements
- Bug fixes and optimizations

## Support

For issues and feature requests, please use the GitHub issues tracker.

---
*Generated for Icom ID-52PLUS amateur radio transceiver*  
*Perfect for POTA activations, SOTA expeditions, and comprehensive repeater coverage*