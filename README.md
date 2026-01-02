![SONIC](https://github.com/opnavlab/sonic/blob/main/logos/sonic_banner.png)
# **S**oftware for **O**ptical **N**avigation and **I**nstrument **C**alibration
This open-sourced, object oriented MATLAB package is a toolkit built on years of research in
optical navigation (OPNAV), with a foundation in principled projective geometry. Many 
capabilities needed for space-flight OPNAV are made transparent and configurable within the SONIC classes, 
with minimal assumption of the analyst's intentions. This allows each user to construct their own 
unique workflows for a specific research or analysis problems. SONIC was designed to help simplify navigation solutions such as (but not limited to):

- Horizon-Based OPNAV
- Triangulation
- Star Identification
- 3D-Reconstruction
- And more

SONIC was created by the researchers and students of the [Space Exploration Analysis 
Laboratory](https://seal.ae.gatech.edu/) at the Georgia Institute of Technology for student, 
academic researchers, space science professionals, or anyone curious to learn more about OPNAV.

For **API documentation**, please visit [https://opnavlab.github.io/sonic/](https://opnavlab.github.io/sonic/).

**If you would like to reference SONIC** in your work, please cite our publication from the Journal of Open Source Software publication. The paper can be found here:
[![DOI](https://joss.theoj.org/papers/10.21105/joss.06916/status.svg)](https://doi.org/10.21105/joss.06916)

# Getting Started

> **Quick Start:** See [QUICKSTART.md](QUICKSTART.md) for a streamlined setup guide.

Minimal preparation is needed to begin using SONIC. Simply follow these steps:
1. Clone the repository locally.
2. Download the required data files:
   
   > **⚠️ NOTE:** The Box shared folder link is currently unavailable. Please contact the repository maintainers for access to the data files, or see the [DOWNLOAD_DATA.md](DOWNLOAD_DATA.md) guide for information about the original data sources.
   
   - **Option A (Recommended):** Run the provided download helper script:
     ```bash
     # Using Python
     python3 download_data.py
     
     # OR using Bash
     ./download_data.sh
     ```
     The script will check for existing files and provide instructions for obtaining the data files.
   
   - **Option B (Manual):** If you have access to the data files, place the .mat files in the `+sonic/+data` folder within your local repository.
   
   Required data files:
   - `hipparcos.mat` - Hipparcos star catalog
   - `usnognc.mat` - US Naval Observatory GNC catalog
   - `robbins.mat` - Robbins lunar crater catalog
   - `constellations.mat` - IAU constellation boundaries

3. Add the sonic directory to the search path that you're working in (i.e. using addpath). 

4. **Verify your installation** by running the verification script in MATLAB:
   ```matlab
   verify_installation
   ```
   This will check that all data files are present and the catalogs can be loaded correctly.

A few MATLAB live tutorials are provided under [+examples](https://github.com/opnavlab/sonic/tree/main/%2Bexamples)
for demonstrative purposes.

To further verify your installation of SONIC, please run these examples locally and compare the outputs to the pre-run demos in the SONIC API documentation, linked below.

Note: SONIC requires the following MATLAB toolboxes installed:
- Image Processing Toolbox version 24.1
- Computer Vision System Toolbox version 24.1

# Contributing
If you are interesting in contributing, have a feature request, or have found a bug in SONIC, please checkout [CONTRIBUTING.md](https://github.com/opnavlab/sonic/blob/main/CONTRIBUTING.md) for more information.

# References
Please see [REFERENCES.md](https://github.com/opnavlab/sonic/blob/main/REFERENCES.md) for a list of references used in the development of SONIC.
