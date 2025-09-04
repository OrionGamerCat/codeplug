#!/bin/bash

# Icom ID-52 Codeplug Generator
# Generates codeplugs with Austrian, Slovak, and Singaporean repeaters plus SOTA POIs
# Based on memory-channels-processor examples

set -e

echo "=== Icom ID-52 Codeplug Generator ==="
echo "Generating codeplugs with repeaters and SOTA POIs for Austria, Slovakia, and Singapore"
echo

# Try to find memory-channels-processor in PATH first, then fallback to local installation
if command -v memory-channels-processor &> /dev/null; then
    MEMORY_PROCESSOR="memory-channels-processor"
    echo "Found memory-channels-processor in PATH"
elif [[ -f "/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe" ]]; then
    MEMORY_PROCESSOR="/mnt/c/Users/sebastian.schiegl/Github/memory-channels-processor/Scripts/memory-channels-processor.exe"
    echo "Using local memory-channels-processor installation"
else
    echo "Error: memory-channels-processor not found in PATH or local installation"
    echo "Please install memory-channels-processor or ensure it's in your PATH"
    echo "Download from: https://oe3lrt.gitlab.io/memory-channels-processor/"
    exit 1
fi

# Create output directory
mkdir -p output
cd output

echo "=== Generating Austrian Repeaters by County ==="

# First generate intermediate CSV file with all Austrian repeaters
echo "Generating intermediate Austrian repeaters file..."
"$MEMORY_PROCESSOR" --source "oevsv-repeater-db" \
    --output-file "mcp_tmp_repeaters.csv" \
    --country "AUT" \
    --output-format "csv"

# Filter by Austrian federal states using callsign prefixes
echo "Processing OE1 - Wien (Vienna)..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe1_wien.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "35" \
    --icom-group-name "Wien" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE1"

echo "Processing OE2 - Salzburg..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe2_salzburg.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "36" \
    --icom-group-name "Salzburg" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE2"

echo "Processing OE3 - Niederösterreich..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe3_niederoesterreich.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "37" \
    --icom-group-name "Niederösterreich" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE3"

echo "Processing OE4 - Burgenland..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe4_burgenland.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "38" \
    --icom-group-name "Burgenland" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE4"

echo "Processing OE5 - Oberösterreich..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe5_oberoesterreich.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "39" \
    --icom-group-name "Oberösterreich" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE5"

echo "Processing OE6 - Steiermark..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe6_steiermark.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "40" \
    --icom-group-name "Steiermark" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE6"

echo "Processing OE7 - Tirol..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe7_tirol.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "41" \
    --icom-group-name "Tirol" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE7"

echo "Processing OE8 - Kärnten..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe8_kaernten.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "42" \
    --icom-group-name "Kärnten" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE8"

echo "Processing OE9 - Vorarlberg..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe9_vorarlberg.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --type "fm" \
    --output-format "icom" \
    --name-format "name" \
    --icom-group-number "43" \
    --icom-group-name "Vorarlberg" \
    --icom-type "fm" \
    --sort "freq_rx" --sort "callsign" --sort "name" \
    --filter "callsign~=OE9"

echo
echo "=== Generating GPS-Enhanced FM Repeater Files ==="

# Generate GPS-enhanced versions of Austrian FM repeater files
echo "Creating GPS-enhanced FM repeater files for Icom ID-52PLUS..."

counties=("oe1_wien" "oe2_salzburg" "oe3_niederoesterreich" "oe4_burgenland" "oe5_oberoesterreich" "oe6_steiermark" "oe7_tirol" "oe8_kaernten" "oe9_vorarlberg")

for county in "${counties[@]}"; do
    input_file="icom_id52_austria_${county}.csv"
    output_file="icom_id52_austria_${county}_gps_enhanced.csv"
    
    if [[ -f "$input_file" ]]; then
        echo "Enhancing $county with GPS coordinates..."
        python3 "../add_gps_to_fm.py" "$input_file" "mcp_tmp_repeaters.csv" "$output_file"
    fi
done

echo
echo "=== Generating Austrian Repeater GPS POIs ==="

# Generate GPS POI files for Austrian repeaters by county
echo "Processing OE1 GPS POIs - Wien (Vienna)..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe1_wien_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "60" \
    --icom-group-name "AT-Wien-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE1"

echo "Processing OE2 GPS POIs - Salzburg..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe2_salzburg_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "61" \
    --icom-group-name "AT-Salzburg-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE2"

echo "Processing OE3 GPS POIs - Niederösterreich..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe3_niederoesterreich_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "62" \
    --icom-group-name "AT-NÖ-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE3"

echo "Processing OE4 GPS POIs - Burgenland..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe4_burgenland_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "63" \
    --icom-group-name "AT-Burgenland-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE4"

echo "Processing OE5 GPS POIs - Oberösterreich..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe5_oberoesterreich_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "64" \
    --icom-group-name "AT-OÖ-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE5"

echo "Processing OE6 GPS POIs - Steiermark..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe6_steiermark_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "65" \
    --icom-group-name "AT-Steiermark-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE6"

echo "Processing OE7 GPS POIs - Tirol..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe7_tirol_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "66" \
    --icom-group-name "AT-Tirol-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE7"

echo "Processing OE8 GPS POIs - Kärnten..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe8_kaernten_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "67" \
    --icom-group-name "AT-Kärnten-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE8"

echo "Processing OE9 GPS POIs - Vorarlberg..."
"$MEMORY_PROCESSOR" --output-file "icom_id52_austria_oe9_vorarlberg_gps.csv" \
    --source "csv" \
    --csv-input-file "mcp_tmp_repeaters.csv" \
    --output-format "icom" \
    --name-format "callsign" \
    --icom-group-number "68" \
    --icom-group-name "AT-Vorarlberg-GPS" \
    --icom-type "gps" \
    --sort "callsign" \
    --filter "callsign~=OE9"

echo
echo "=== Generating Slovak Repeaters (2m/70cm only) ==="

# First generate intermediate Slovak repeater CSV with GPS data
echo "Generating intermediate Slovak repeaters file with GPS data..."
"$MEMORY_PROCESSOR" --source "slovakia-repeater-list" \
    --output-file "slovakia_tmp_repeaters.csv" \
    --output-format "csv" \
    --band "2m" "70cm"

# Slovak repeaters (2m and 70cm bands only)
echo "Processing Slovak repeaters (2m/70cm only)..."
"$MEMORY_PROCESSOR" --source "csv" \
    --csv-input-file "slovakia_tmp_repeaters.csv" \
    --output-file "icom_id52_slovakia_repeaters.csv" \
    --output-format "icom" \
    --icom-group-number "44" \
    --icom-group-name "SK-Repeaters" \
    --icom-type "fm" \
    --sort "freq_tx" \
    --name-format "callsign"

# Generate GPS-enhanced Slovak repeaters
echo "Creating GPS-enhanced Slovak repeaters..."
python3 "../add_gps_to_fm.py" "icom_id52_slovakia_repeaters.csv" "slovakia_tmp_repeaters.csv" "icom_id52_slovakia_repeaters_gps_enhanced.csv"

echo
echo "=== Generating Singapore Repeaters ==="

# Singapore repeaters from local CSV file
echo "Processing Singapore repeaters from local database..."
"$MEMORY_PROCESSOR" --source "csv" \
    --csv-input-file "../singapore_repeaters.csv" \
    --output-file "icom_id52_singapore_repeaters.csv" \
    --output-format "icom" \
    --icom-group-number "45" \
    --icom-group-name "SG-Repeaters" \
    --icom-type "fm" \
    --sort "freq_tx" \
    --name-format "name"

echo
echo "=== Generating Japanese Repeaters ==="

# First convert Japanese Icom CSV to memory-channels-processor format
echo "Converting Japanese Icom CSV to memory-channels-processor format..."
python3 "../process_japan_repeaters.py"

# Filter Japanese repeaters to 2m, 70cm, and 23cm bands only
echo "Processing Japanese repeaters (2m/70cm/23cm only)..."
"$MEMORY_PROCESSOR" --source "csv" \
    --csv-input-file "japan_tmp_repeaters.csv" \
    --output-file "icom_id52_japan_repeaters.csv" \
    --output-format "icom" \
    --icom-group-number "46" \
    --icom-group-name "JP-Repeaters" \
    --icom-type "fm" \
    --band "2m" "70cm" "23cm" \
    --sort "freq_tx" \
    --name-format "callsign"

# Generate GPS-enhanced Japanese repeaters
echo "Creating GPS-enhanced Japanese repeaters..."
python3 "../add_gps_to_fm.py" "icom_id52_japan_repeaters.csv" "japan_tmp_repeaters.csv" "icom_id52_japan_repeaters_gps_enhanced.csv"

echo
echo "=== Generating Vienna Radio Frequencies ==="

# Vienna radio frequencies from RTR database using group P
echo "Processing Vienna radio frequencies from RTR database..."
"$MEMORY_PROCESSOR" --source "rtr-radio-db" \
    --band "radio" \
    --type "fm" \
    --output-file "icom_id52_vienna_radio_frequencies.csv" \
    --output-format "icom" \
    --locator "JN88EF" \
    --distance-max 30 \
    --name-format "custom" \
    --name-format-custom "{{ name + '-' + remove_spaces(landmark) }}" \
    --icom-type "fm-radio" \
    --icom-group-number "80" \
    --icom-group-name "Wien-Radio"

echo
echo "=== Generating SOTA POIs ==="

# Austrian SOTA summits
echo "Processing Austrian SOTA summits..."
"$MEMORY_PROCESSOR" --source "sota-summits" \
    --output-file "icom_id52_austria_sota.csv" \
    --country "AUT" \
    --output-format "icom" \
    --icom-group-number "50" \
    --icom-group-name "SOTA-AT" \
    --icom-type "gps" \
    --sort "name" \
    --sort "callsign" \
    --name-format "custom" \
    --name-format-custom "{{ remove_prefix(remove_spaces(callsign), 'OE/') + ' ' + name }}"

# Slovak SOTA summits
echo "Processing Slovak SOTA summits..."
"$MEMORY_PROCESSOR" --source "sota-summits" \
    --output-file "icom_id52_slovakia_sota.csv" \
    --country "SVK" \
    --output-format "icom" \
    --icom-group-number "51" \
    --icom-group-name "SOTA-SK" \
    --icom-type "gps" \
    --sort "name" \
    --sort "callsign" \
    --name-format "custom" \
    --name-format-custom "{{ remove_prefix(remove_spaces(callsign), 'OM/') + ' ' + name }}"

# Singaporean SOTA summits  
echo "Processing Singaporean SOTA summits..."
"$MEMORY_PROCESSOR" --source "sota-summits" \
    --output-file "icom_id52_singapore_sota.csv" \
    --country "SGP" \
    --output-format "icom" \
    --icom-group-number "52" \
    --icom-group-name "SOTA-SG" \
    --icom-type "gps" \
    --sort "name" \
    --sort "callsign" \
    --name-format "custom" \
    --name-format-custom "{{ remove_prefix(remove_spaces(callsign), '9V1/') + ' ' + name }}"

echo
echo "=== Generating GPS-Enhanced Master Codeplug for ID-52PLUS ==="

# Create GPS-enhanced master file for ID-52PLUS only
echo "Creating GPS-enhanced master codeplug file for ID-52PLUS..."
{
    echo "# Icom ID-52PLUS GPS-Enhanced Master Codeplug"
    echo "# Generated on $(date)"
    echo "# Includes Austrian and Slovak repeaters with GPS coordinates, Singapore repeaters, and SOTA POIs"
    echo "# FM repeaters include GPS coordinates for navigation"
    echo
    
    # Include GPS-enhanced Austrian files
    for file in icom_id52_austria_*_gps_enhanced.csv; do
        if [[ -f "$file" ]]; then
            echo "# From: $file (GPS-Enhanced Austrian Repeaters)"
            cat "$file"
            echo
        fi
    done
    
    # Include GPS-enhanced Slovak file
    if [[ -f "icom_id52_slovakia_repeaters_gps_enhanced.csv" ]]; then
        echo "# From: icom_id52_slovakia_repeaters_gps_enhanced.csv (GPS-Enhanced Slovak Repeaters)"
        cat "icom_id52_slovakia_repeaters_gps_enhanced.csv"
        echo
    fi
    
    # Include GPS-enhanced Japanese file
    if [[ -f "icom_id52_japan_repeaters_gps_enhanced.csv" ]]; then
        echo "# From: icom_id52_japan_repeaters_gps_enhanced.csv (GPS-Enhanced Japanese Repeaters)"
        cat "icom_id52_japan_repeaters_gps_enhanced.csv"
        echo
    fi
    
    # Add other files (Singapore, SOTA, Vienna radio)
    for file in icom_id52_singapore_*.csv icom_id52_*_sota.csv icom_id52_vienna_*.csv; do
        if [[ -f "$file" ]]; then
            echo "# From: $file"
            cat "$file"
            echo
        fi
    done
} > icom_id52_master_gps_enhanced_temp.csv && mv icom_id52_master_gps_enhanced_temp.csv icom_id52_master_gps_enhanced.csv

echo
echo "=== Organizing Files for SD Card Deployment ==="

# Create ID-52 directory structure for SD card
echo "Creating ID-52 directory structure for SD card deployment..."

# Create main ID-52 directory
mkdir -p "ID-52"

# Create subdirectories
mkdir -p "ID-52/Austria-Counties"
mkdir -p "ID-52/Slovakia"
mkdir -p "ID-52/Singapore"
mkdir -p "ID-52/Japan"
mkdir -p "ID-52/SOTA-POIs"
mkdir -p "ID-52/Vienna-Radio"
mkdir -p "ID-52/GPS-POIs"
mkdir -p "ID-52/Complete"

echo "Copying files to organized directory structure..."

# Copy Austrian county GPS-enhanced files
echo "Organizing Austrian county files..."
cp icom_id52_austria_*_gps_enhanced.csv "ID-52/Austria-Counties/" 2>/dev/null || true

# Copy Slovak files
echo "Organizing Slovak files..."
cp icom_id52_slovakia_*.csv "ID-52/Slovakia/" 2>/dev/null || true

# Copy Singapore files
echo "Organizing Singapore files..."
cp icom_id52_singapore_*.csv "ID-52/Singapore/" 2>/dev/null || true

# Copy Japanese files
echo "Organizing Japanese files..."
cp icom_id52_japan_*.csv "ID-52/Japan/" 2>/dev/null || true

# Copy SOTA POI files
echo "Organizing SOTA POI files..."
cp icom_id52_*_sota.csv "ID-52/SOTA-POIs/" 2>/dev/null || true

# Copy Vienna radio files
echo "Organizing Vienna radio files..."
cp icom_id52_vienna_*.csv "ID-52/Vienna-Radio/" 2>/dev/null || true

# Copy Austrian GPS POI files
echo "Organizing Austrian GPS POI files..."
cp icom_id52_austria_*_gps.csv "ID-52/GPS-POIs/" 2>/dev/null || true

# Copy master file
echo "Copying master file..."
cp icom_id52_master_gps_enhanced.csv "ID-52/Complete/"

# Create README files for each directory
echo "Creating README files for each directory..."

cat > "ID-52/README.txt" << 'EOF'
# Icom ID-52PLUS SD Card Files
Generated on $(date)

This directory structure is organized for easy deployment to your Icom ID-52PLUS SD card.

QUICK START:
1. Copy the entire ID-52 folder to your SD card
2. Import ID-52/Complete/icom_id52_master_gps_enhanced.csv for everything
3. Or import individual files from subdirectories as needed

DIRECTORY STRUCTURE:
- Austria-Counties/  - Austrian repeaters by federal state (GPS-enhanced)
- Slovakia/         - Slovak repeaters (2m/70cm, GPS-enhanced)
- Japan/            - Japanese repeaters (2m/70cm/23cm, GPS-enhanced)
- Singapore/        - Singapore repeaters (GPS-enhanced)
- SOTA-POIs/        - SOTA summit POIs for activation
- Vienna-Radio/     - Vienna radio station frequencies
- GPS-POIs/         - Austrian repeater GPS waypoints
- Complete/         - Master file with all data

All FM repeater files include GPS coordinates for navigation!
EOF

cat > "ID-52/Austria-Counties/README.txt" << 'EOF'
# Austrian Amateur Radio Repeaters by County (GPS-Enhanced)

Files include GPS coordinates for navigation to repeater locations.

Counties (Federal States):
- oe1_wien_gps_enhanced.csv          - Vienna (Wien)
- oe2_salzburg_gps_enhanced.csv      - Salzburg
- oe3_niederoesterreich_gps_enhanced.csv - Lower Austria
- oe4_burgenland_gps_enhanced.csv    - Burgenland
- oe5_oberoesterreich_gps_enhanced.csv - Upper Austria
- oe6_steiermark_gps_enhanced.csv    - Styria
- oe7_tirol_gps_enhanced.csv         - Tyrol
- oe8_kaernten_gps_enhanced.csv      - Carinthia
- oe9_vorarlberg_gps_enhanced.csv    - Vorarlberg

Groups: 35-43 (Wien=35, Salzburg=36, etc.)
EOF

cat > "ID-52/Slovakia/README.txt" << 'EOF'
# Slovak Amateur Radio Repeaters (GPS-Enhanced)

2m and 70cm repeaters only with GPS coordinates.

Files:
- icom_id52_slovakia_repeaters_gps_enhanced.csv - All Slovak repeaters with GPS

Group: 44 (SK-Repeaters)
EOF

cat > "ID-52/Singapore/README.txt" << 'EOF'
# Singapore Amateur Radio Repeaters (GPS-Enhanced)

Files:
- icom_id52_singapore_repeaters.csv - Singapore repeaters with GPS

Group: 45 (SG-Repeaters)
EOF

cat > "ID-52/Japan/README.txt" << 'EOF'
# Japanese Amateur Radio Repeaters (GPS-Enhanced)

2m, 70cm, and 23cm repeaters with GPS coordinates from Icom Japan.

Files:
- icom_id52_japan_repeaters_gps_enhanced.csv - All Japanese repeaters with GPS

Group: 46 (JP-Repeaters)
Includes D-STAR and FM repeaters with precise GPS coordinates.
EOF

cat > "ID-52/SOTA-POIs/README.txt" << 'EOF'
# SOTA (Summits on the Air) POIs

GPS waypoints for SOTA summit activation.

Files:
- icom_id52_austria_sota.csv    - Austrian summits (Group 50)
- icom_id52_slovakia_sota.csv   - Slovak summits (Group 51)
- icom_id52_singapore_sota.csv  - Singapore summits (Group 52)
EOF

cat > "ID-52/Vienna-Radio/README.txt" << 'EOF'
# Vienna Radio Station Frequencies

Local radio stations within 30km of Vienna (JN88EF).

Files:
- icom_id52_vienna_radio_frequencies.csv

Group: 80 (Wien-Radio)
EOF

cat > "ID-52/GPS-POIs/README.txt" << 'EOF'
# Austrian Repeater GPS POIs

Separate GPS waypoint files for Austrian repeater locations.
Use these for navigation without frequency data.

Files:
- icom_id52_austria_*_gps.csv - GPS waypoints by county

Groups: 60-68 (AT-County-GPS)
EOF

cat > "ID-52/Complete/README.txt" << 'EOF'
# Complete Master File

This file contains ALL data in one file:
- Austrian repeaters (by county) with GPS coordinates
- Slovak repeaters (2m/70cm) with GPS coordinates
- Japanese repeaters (2m/70cm/23cm) with GPS coordinates
- Singapore repeaters with GPS coordinates
- SOTA POIs for all countries
- Vienna radio frequencies

File: icom_id52_master_gps_enhanced.csv

Import this single file for complete codeplug.
EOF

echo
echo "=== SD Card Organization Complete ==="
echo
echo "Directory structure created: ID-52/"
tree ID-52/ 2>/dev/null || find ID-52/ -type f | sort

echo
echo "📁 READY FOR SD CARD DEPLOYMENT!"
echo
echo "🚀 QUICK START:"
echo "1. Copy the entire 'ID-52' folder to your SD card"
echo "2. Import ID-52/Complete/icom_id52_master_gps_enhanced.csv for everything"
echo "3. Or import individual files from subdirectories as needed"
echo
echo "📍 ALL FM REPEATERS INCLUDE GPS COORDINATES!"
echo
echo "Files organized in: $(pwd)/ID-52/"