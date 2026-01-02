# Data Files Required

> **⚠️ IMPORTANT:** The Box shared folder link is currently unavailable. Please contact the repository maintainers at https://github.com/opnavlab/sonic/issues for access to the data files.

Download the .mat data files and place them in the +sonic/+data folder within your local repository. 

## Quick Setup

Run the download helper script from the SONIC root directory:
```bash
# Python
python3 download_data.py

# OR Bash  
./download_data.sh
```

These scripts will check for missing files and guide you through the download process.

## Required Files

These .mat files to be placed in +sonic/+data contain catalog data for use with SONIC. The data fields are as given in the original sources, but when the catalog objects are instantiated, units are converted to be consistent with SONIC standards. The current catalogs and their sources are listed below:

| File | Description | Original Source |
|------|-------------|-----------------|
| `hipparcos.mat` | Hipparcos star catalog (~118k stars) | https://www.cosmos.esa.int/web/hipparcos/interactive-data-access |
| `usnognc.mat` | US Naval Observatory GNC catalog (~300k+ stars) | https://crf.usno.navy.mil/icrs |
| `robbins.mat` | Robbins lunar crater catalog (~1.3M craters) | https://astrogeology.usgs.gov/search/map/moon_crater_database_v1_robbins |
| `constellations.mat` | IAU constellation boundaries (89 entries) | Parsed from IAU constellation boundary files |

## Download Location

~~All data files are available at: https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0~~

**The Box link is currently unavailable.** Please contact the repository maintainers at https://github.com/opnavlab/sonic/issues to request access to the preprocessed data files.

For detailed setup instructions, see the DOWNLOAD_DATA.md file in the SONIC root directory.

