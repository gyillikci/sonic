# SONIC Quick Start Guide

This guide will help you get SONIC up and running in just a few minutes.

## Prerequisites

- MATLAB with the following toolboxes:
  - Image Processing Toolbox version 24.1 or later
  - Computer Vision System Toolbox version 24.1 or later
- Python 3 (optional, for download helper script)
- Bash (optional, for download helper script)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/opnavlab/sonic.git
cd sonic
```

### 2. Download Data Files

**Option A: Using the helper script (recommended)**

```bash
# Using Python
python3 download_data.py

# OR using Bash
./download_data.sh
```

Follow the on-screen instructions to download the required data files from Box.

**Option B: Manual download**

1. Visit: https://gatech.box.com/s/24ntu8h8ty0v8nyxplhl94ck39q7wtc0
2. Download all four `.mat` files
3. Place them in `+sonic/+data/` directory

### 3. Verify Installation

Open MATLAB in the SONIC root directory and run:

```matlab
verify_installation
```

This will check:
- All required data files are present
- Catalogs can be loaded successfully
- Required MATLAB toolboxes are installed

### 4. Add to MATLAB Path

```matlab
addpath(pwd)
```

## Quick Test

Try loading a star catalog:

```matlab
% Load Hipparcos catalog
hip = sonic.Hipparcos();
fprintf('Loaded %d stars from Hipparcos catalog\n', hip.n);

% Load Robbins crater catalog
rbn = sonic.Robbins();
fprintf('Loaded %d craters from Robbins catalog\n', rbn.n);
```

## Example Usage

Explore the tutorials in the `+examples` directory:

- `CraterEllipseFittingTutorial.mlx` - Crater detection and fitting
- `ReflectanceModelingTutorial.mlx` - Surface reflectance modeling
- `RenderOrthoSphereTutorial.mlx` - Orthographic sphere rendering
- `ScanLinesTutorial.mlx` - Horizon detection
- `SyntheticStarImgTutorial.mlx` - Star field generation
- `TriangVestaReconTutorial.mlx` - 3D reconstruction

Open any tutorial in MATLAB:

```matlab
open +examples/SyntheticStarImgTutorial.mlx
```

## Troubleshooting

### Data files not found

If you get errors about missing `.mat` files:

1. Ensure you've downloaded all files from the Box link
2. Verify files are in `+sonic/+data/` directory
3. Run `verify_installation` in MATLAB to check

### Cannot access Box.com

If you cannot access the Box link:

- Try from a different network
- Contact the SONIC maintainers for alternative download options
- See `DOWNLOAD_DATA.md` for more information

### MATLAB toolbox errors

If you get errors about missing toolboxes:

1. Check your MATLAB installation: `ver` 
2. Install required toolboxes from MATLAB Add-Ons
3. Ensure toolboxes are version 24.1 or later

## Next Steps

- **Documentation:** https://opnavlab.github.io/sonic/
- **Examples:** Explore the `+examples/` directory
- **Contributing:** See `CONTRIBUTING.md`
- **Issues:** https://github.com/opnavlab/sonic/issues

## Getting Help

If you encounter issues:

1. Check the documentation: https://opnavlab.github.io/sonic/
2. Review `DOWNLOAD_DATA.md` for data setup issues
3. Search existing issues: https://github.com/opnavlab/sonic/issues
4. Open a new issue if needed

## Citation

If you use SONIC in your research, please cite:

[![DOI](https://joss.theoj.org/papers/10.21105/joss.06916/status.svg)](https://doi.org/10.21105/joss.06916)

## License

SONIC is available under the MIT License. See `LICENSE` for details.
