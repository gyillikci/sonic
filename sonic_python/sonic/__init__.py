"""
SONIC: Software for Optical Navigation and Instrument Calibration
Python Implementation
"""

__version__ = "0.1.0"

# Core geometry classes
from .geometry.points2 import Points2
from .geometry.points3 import Points3
from .geometry.conic import Conic
from .geometry.attitude import Attitude
from .geometry.pose import Pose

# Navigation classes
from .navigation.ellipse_fitter import EllipseFitter
from .navigation.position_estimation import PositionEstimation
from .navigation.robbins import Robbins

# Utilities
from .utils.units import Units
from .utils.math_utils import Math
from .utils.sample_geom_2d import SampleGeom2D
from .utils.tolerances import Tolerances

__all__ = [
    # Geometry
    'Points2',
    'Points3',
    'Conic',
    'Attitude',
    'Pose',
    # Navigation
    'EllipseFitter',
    'PositionEstimation',
    'Robbins',
    # Utils
    'Units',
    'Math',
    'SampleGeom2D',
    'Tolerances',
]
