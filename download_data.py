#!/usr/bin/env python3
"""
SONIC Data Download Script

This script downloads the required .mat data files for SONIC from the Box repository
and places them in the +sonic/+data directory.

Required data files:
- hipparcos.mat: Hipparcos star catalog
- usnognc.mat: US Naval Observatory GNC catalog
- robbins.mat: Robbins lunar crater catalog
- constellations.mat: IAU constellation boundaries

Source: https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0
"""

import os
import sys
import urllib.request
from pathlib import Path

# Configuration
BOX_SHARED_LINK = "https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0"
DATA_DIR = Path("+sonic") / "+data"
REQUIRED_FILES = [
    "hipparcos.mat",
    "usnognc.mat", 
    "robbins.mat",
    "constellations.mat"
]

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header():
    """Print script header"""
    print("=" * 50)
    print("SONIC Data Download Script")
    print("=" * 50)
    print()

def check_data_dir():
    """Check if the data directory exists"""
    if not DATA_DIR.exists():
        print(f"{Colors.RED}Error: Data directory {DATA_DIR} not found!{Colors.NC}")
        print("Please run this script from the SONIC root directory.")
        return False
    return True

def check_existing_files():
    """Check which required files already exist"""
    existing = []
    missing = []
    
    print("Checking for existing data files...")
    print()
    
    for filename in REQUIRED_FILES:
        file_path = DATA_DIR / filename
        if file_path.exists():
            print(f"{Colors.GREEN}✓{Colors.NC} {filename} already exists")
            existing.append(filename)
        else:
            print(f"{Colors.YELLOW}✗{Colors.NC} {filename} not found")
            missing.append(filename)
    
    print()
    return existing, missing

def print_manual_instructions(missing_files):
    """Print instructions for manual download"""
    print(f"{Colors.YELLOW}Manual Download Required{Colors.NC}")
    print()
    print("Some or all data files are missing. Please follow these steps:")
    print()
    print("1. Visit the Box link in your browser:")
    print(f"   {BOX_SHARED_LINK}")
    print()
    print("2. Download the following files:")
    for filename in missing_files:
        print(f"   - {filename}")
    print()
    print("3. Place all downloaded .mat files in the directory:")
    print(f"   {Path.cwd() / DATA_DIR}")
    print()
    print("4. Run this script again to verify the installation")
    print()

def attempt_download(filename):
    """
    Attempt to download a file from Box.
    Note: This typically requires authentication or direct download links.
    """
    print(f"Attempting to download {filename}...")
    # Box.com typically requires authentication for downloading
    # This is a placeholder for potential future implementation
    return False

def main():
    """Main function"""
    print_header()
    
    # Check if we're in the right directory
    if not check_data_dir():
        return 1
    
    # Check existing files
    existing, missing = check_existing_files()
    
    # If all files exist, we're done
    if not missing:
        print(f"{Colors.GREEN}All required data files are already present!{Colors.NC}")
        return 0
    
    # Provide manual download instructions
    print_manual_instructions(missing)
    
    # Note about automated download
    print(f"{Colors.BLUE}Note:{Colors.NC} Automated download from Box.com requires")
    print("authentication and may not be available. Please use the manual")
    print("download method described above.")
    print()
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
