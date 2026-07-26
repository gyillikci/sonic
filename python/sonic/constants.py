"""Constants — physical + celestial constants (port of the subset of +sonic/Constants.m
that the OPNAV / star-tracker pipeline uses).

Body radii are triaxial [a; b; c] in km (JPL/NAIF PCK00010). Only the commonly
used bodies are ported here; extend as needed.
"""

import numpy as np


class Constants:
    c_KMS = 299792.458          # speed of light, km/s (used by Aberration)

    # Triaxial body radii [a, b, c] in km (JPL/NAIF PCK00010).
    SUN_radii_KM = np.array([696000.0, 696000.0, 696000.0])
    MERCURY_radii_KM = np.array([2439.7, 2439.7, 2439.7])
    VENUS_radii_KM = np.array([6051.8, 6051.8, 6051.8])
    EARTH_radii_KM = np.array([6378.1366, 6378.1366, 6356.7519])
    MOON_radii_KM = np.array([1737.4, 1737.4, 1737.4])
    MARS_radii_KM = np.array([3396.19, 3396.19, 3376.20])
    JUPITER_radii_KM = np.array([71492.0, 71492.0, 66854.0])
    SATURN_radii_KM = np.array([60268.0, 60268.0, 54364.0])
    URANUS_radii_KM = np.array([25559.0, 25559.0, 24973.0])
    NEPTUNE_radii_KM = np.array([24764.0, 24764.0, 24341.0])
    PLUTO_radii_KM = np.array([1195.0, 1195.0, 1195.0])

    # Gravitational parameters, km^3/s^2 (JPL DE440).
    MERCURY_GM = 22031.868551
    VENUS_GM = 324858.592000
    EARTH_GM = 398600.435507
    MOON_GM = 4902.800118
    MARS_SYS_GM = 42828.375816
    JUPITER_SYS_GM = 126712764.100000
    SATURN_SYS_GM = 37940584.841800
    URANUS_SYS_GM = 5794556.400000
    NEPTUNE_SYS_GM = 6836527.100580
    PLUTO_SYS_GM = 975.500000
