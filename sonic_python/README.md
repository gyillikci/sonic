# SONIC Python

Python implementation of **S**oftware for **O**ptical **N**avigation and **I**nstrument **C**alibration

This is a Python port of the MATLAB SONIC toolkit, providing tools for:
- Crater-based optical navigation
- Ellipse fitting and conic geometry
- Spacecraft position estimation
- Parallactic angle determination

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import numpy as np
from sonic import Conic, EllipseFitter, Points2

# Generate crater rim points
crater_pts = Points2(np.random.randn(2, 100))

# Fit ellipse
fitter = EllipseFitter()
conic = fitter.fit_ellipse(crater_pts, method='hls')

# Extract parallactic angle
angle_rad = conic.explicit[4]
print(f"Parallactic angle: {np.rad2deg(angle_rad):.2f}°")
```

## Features

### Core Geometry
- `Points2`, `Points3`: 2D and 3D point representations
- `Conic`: Ellipse/conic section handling (implicit, explicit, locus forms)
- `Attitude`: Rotation representations (DCM, quaternions, euler angles)
- `Pose`: Combined rotation and translation

### Navigation
- `EllipseFitter`: Least squares ellipse fitting (LS, SHLS, HLS methods)
- `Robbins`: Lunar crater database interface
- `PositionEstimation`: Spacecraft positioning from crater observations

### Utilities
- `Units`: Angle and distance conversions
- `SampleGeom2D`: Generate points on conics
- `Math`: Linear algebra utilities

## Examples

See `examples/` directory for:
- `crater_parallactic_angle.py`: Crater angle determination
- `ellipse_fitting_tutorial.py`: Ellipse fitting demonstration
- `position_estimation.py`: Spacecraft positioning example

## Original MATLAB Version

This is a Python port of the MATLAB SONIC toolkit:
https://github.com/opnavlab/sonic

## License

MIT License - See LICENSE file

## Citation

If you use SONIC in your research, please cite:
[![DOI](https://joss.theoj.org/papers/10.21105/joss.06916/status.svg)](https://doi.org/10.21105/joss.06916)
