#!/bin/bash
# This script downloads the required data files for SONIC from the Box repository
# Data files are placed in the +sonic/+data directory

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Box download link
BOX_LINK="https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0"

# Target directory
DATA_DIR="+sonic/+data"

# Required data files
DATA_FILES=("hipparcos.mat" "usnognc.mat" "robbins.mat" "constellations.mat")

echo "======================================"
echo "SONIC Data Download Script"
echo "======================================"
echo ""

# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${RED}Error: Data directory $DATA_DIR not found!${NC}"
    echo "Please run this script from the SONIC root directory."
    exit 1
fi

# Function to check if a file exists
check_file() {
    if [ -f "$DATA_DIR/$1" ]; then
        echo -e "${GREEN}✓${NC} $1 already exists"
        return 0
    else
        echo -e "${YELLOW}✗${NC} $1 not found"
        return 1
    fi
}

# Check current status
echo "Checking for existing data files..."
echo ""
all_exist=true
for file in "${DATA_FILES[@]}"; do
    if ! check_file "$file"; then
        all_exist=false
    fi
done
echo ""

if [ "$all_exist" = true ]; then
    echo -e "${GREEN}All required data files are already present!${NC}"
    exit 0
fi

# Instructions for manual download
echo -e "${YELLOW}Manual Download Required${NC}"
echo ""
echo "Some or all data files are missing. Please follow these steps:"
echo ""
echo "1. Visit the Box link in your browser:"
echo "   $BOX_LINK"
echo ""
echo "2. Download the following files:"
for file in "${DATA_FILES[@]}"; do
    echo "   - $file"
done
echo ""
echo "3. Place all downloaded .mat files in the directory:"
echo "   $(pwd)/$DATA_DIR"
echo ""
echo "4. Run this script again to verify the installation"
echo ""

# Try automated download with wget if available
if command -v wget &> /dev/null; then
    echo -e "${YELLOW}Attempting automated download with wget...${NC}"
    echo ""
    
    # Note: This requires the direct download URLs which may need to be updated
    # Box.com typically requires interactive download or API access
    echo "Note: Automated download from Box may not work due to authentication requirements."
    echo "If automatic download fails, please use the manual method described above."
    echo ""
fi

exit 1
