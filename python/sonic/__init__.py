"""SONIC (Python) — Software for Optical Navigation and Instrument Calibration.

A Python port of the OPNAV / star-tracker core of the SONIC MATLAB toolkit
(opnavlab/sonic). Class names and semantics mirror the MATLAB `+sonic` package so
workflows translate directly; methods use snake_case with the MATLAB name noted
in each docstring.

Ported subset (the image -> RA/Dec plate-solving pipeline and its foundations):
    geometry:   Points2, Points3, PointsS2, SphereCoords
    attitude:   Attitude (DCM/quat/rotvec, Wahba/SVD, slerp)
    camera:     Camera, DistortionModel/Pinhole/BrownConrady, Project, Aberration
    detection:  Image, Centroider
    star ID:    StarCatalog/Hipparcos, Kvector, StarId
    support:    Units, Constants, Tolerances

Not ported: horizon-based OPNAV / conics, rendering + reflectance models, PnP /
pose / triangulation. See ../README.md for status and the parity test suite.
"""

from .aberration import Aberration
from .attitude import Attitude
from .camera import Camera
from .centroider import Centroider
from .constants import Constants
from .distortion import BrownConrady, DistortionModel, Pinhole
from .image import Image
from .kvector import Kvector
from .points import Points2, Points3, PointsS2
from .project import Project
from .spherecoords import SphereCoords
from .starcatalog import Hipparcos, StarCatalog
from .starid import StarId
from .tolerances import Tolerances
from .units import Units

__all__ = [
    "Aberration", "Attitude", "Camera", "Centroider", "Constants",
    "BrownConrady", "DistortionModel", "Pinhole", "Image", "Kvector",
    "Points2", "Points3", "PointsS2", "Project", "SphereCoords",
    "Hipparcos", "StarCatalog", "StarId", "Tolerances", "Units",
]
__version__ = "0.1.0"
