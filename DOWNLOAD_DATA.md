# SONIC Data Files Setup Guide

This guide explains how to download and set up the required data files for SONIC.

## Overview

SONIC requires four `.mat` data files containing catalog data for optical navigation:

| File | Description | Source |
|------|-------------|--------|
| `hipparcos.mat` | Hipparcos star catalog | [ESA Hipparcos Interactive Data Access](https://www.cosmos.esa.int/web/hipparcos/interactive-data-access) |
| `usnognc.mat` | US Naval Observatory GNC catalog | [USNO ICRS](https://crf.usno.navy.mil/icrs) |
| `robbins.mat` | Robbins lunar crater catalog (~1.3M craters) | [USGS Robbins Crater Database](https://astrogeology.usgs.gov/search/map/moon_crater_database_v1_robbins) |
| `constellations.mat` | IAU constellation boundaries | Parsed from IAU constellation boundary files |

All files must be placed in the `+sonic/+data/` directory.

## Quick Start

### Method 1: Using Download Helper Scripts (Recommended)

We provide helper scripts to check for missing data files and guide you through the download process:

**Using Python:**
```bash
python3 download_data.py
```

**Using Bash:**
```bash
./download_data.sh
```

These scripts will:
- Check which data files are already present
- List missing files
- Provide direct instructions for downloading them
- Verify successful installation

### Method 2: Manual Download

1. **Download the data files:**
   
   Visit the Box shared folder: https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0
   
   Download all four `.mat` files:
   - `hipparcos.mat`
   - `usnognc.mat`
   - `robbins.mat`
   - `constellations.mat`

2. **Place files in the correct location:**
   
   Move all downloaded files to the `+sonic/+data/` directory in your SONIC installation:
   ```
   sonic/
   ├── +sonic/
   │   ├── +data/
   │   │   ├── hipparcos.mat          ← Place here
   │   │   ├── usnognc.mat            ← Place here
   │   │   ├── robbins.mat            ← Place here
   │   │   ├── constellations.mat     ← Place here
   │   │   └── readme.md
   ```

3. **Verify installation:**
   
   Run one of the download helper scripts to verify all files are in place:
   ```bash
   python3 download_data.py
   ```
   
   Or test in MATLAB:
   ```matlab
   % Test Hipparcos catalog
   hip = sonic.Hipparcos();
   disp(['Hipparcos catalog loaded: ', num2str(hip.n), ' stars']);
   
   % Test USNO GNC catalog
   gnc = sonic.USNOGNC();
   disp(['USNO GNC catalog loaded: ', num2str(gnc.n), ' stars']);
   
   % Test Robbins crater catalog
   rbn = sonic.Robbins();
   disp(['Robbins catalog loaded: ', num2str(rbn.n), ' craters']);
   ```

## Troubleshooting

### File Not Found Errors

If you get errors like:
```
Error using load
Unable to read file '+sonic/+data/hipparcos.mat'. No such file or directory.
```

**Solution:** Ensure you've downloaded all required `.mat` files and placed them in `+sonic/+data/`.

### Permission Errors

If you cannot write to the `+sonic/+data/` directory:

**Solution:** Check file permissions and ensure you have write access to the directory.

### Verification Failed

If the download scripts report missing files after you've downloaded them:

**Solution:** 
1. Verify files are in the correct location: `+sonic/+data/`
2. Check that filenames match exactly (case-sensitive)
3. Ensure files are not corrupted (try re-downloading)

## Data File Details

### hipparcos.mat
- **Size:** ~3 MB
- **Contents:** Hipparcos star catalog with positions, proper motions, parallax, and visual magnitudes
- **Epoch:** J1991.25
- **Stars:** ~118,000 entries

### usnognc.mat
- **Size:** ~10 MB  
- **Contents:** US Naval Observatory Guide Star Catalog for navigation with multiple photometric bands
- **Epoch:** J2016
- **Stars:** ~300,000+ entries

### robbins.mat
- **Size:** ~130 MB
- **Contents:** Comprehensive lunar crater database with positions, sizes, and ellipse fits
- **Source Date:** October 21, 2024
- **Craters:** ~1.3 million entries
- **Reference:** Robbins, S. J. (2019). Journal of Geophysical Research: Planets, 124(4), 871-892.

### constellations.mat
- **Size:** ~100 KB
- **Contents:** IAU constellation boundary definitions as spherical polygons
- **Constellations:** 89 entries (88 constellations, Serpens split into two parts)

## Additional Resources

- **SONIC Documentation:** https://opnavlab.github.io/sonic/
- **Data Sources:** See `+sonic/+data/readme.md` for original data source links
- **Repository:** https://github.com/opnavlab/sonic

## License

The data files are provided under their respective original licenses. Please refer to the original data sources for specific license information. SONIC itself is provided under the MIT License.
