"""Units — unit conversions (port of +sonic/Units.m).

All functions are vectorized over numpy arrays and accept scalars.
"""

import numpy as np

_AU_KM = 149597870.7            # 1 AU in km (IAU 2012)
_DEG = 180.0 / np.pi
_SEC_PER_YEAR = 365.25 * 24 * 3600


class Units:
    @staticmethod
    def RADtoDEG(v):
        return np.asarray(v) * _DEG

    @staticmethod
    def DEGtoRAD(v):
        return np.asarray(v) / _DEG

    @staticmethod
    def MAStoDEG(v):
        """Milliarcseconds -> degrees."""
        return np.asarray(v) / (1000.0 * 3600.0)

    @staticmethod
    def MAStoRAD(v):
        """Milliarcseconds -> radians."""
        return Units.DEGtoRAD(Units.MAStoDEG(v))

    @staticmethod
    def PYtoPS(v):
        """Per-year -> per-second."""
        return np.asarray(v) / _SEC_PER_YEAR

    @staticmethod
    def MASPYtoRPS(v):
        """Milliarcseconds/year -> radians/second (proper motion)."""
        return Units.PYtoPS(Units.MAStoRAD(v))

    @staticmethod
    def AUtoKM(v):
        return np.asarray(v) * _AU_KM

    @staticmethod
    def KMtoAU(v):
        return np.asarray(v) / _AU_KM

    @staticmethod
    def DEGtoHMS(deg):
        """Degrees -> (hours, minutes, seconds)."""
        deg = np.asarray(deg, float)
        hour = np.floor(deg / 15.0)
        min_raw = 4.0 * np.mod(deg, 15.0)
        minutes = np.floor(min_raw)
        sec = 60.0 * np.mod(min_raw, 1.0)
        return np.vstack((hour, minutes, sec))

    @staticmethod
    def HMStoDEG(hms):
        """(hours, minutes, seconds) -> degrees. `hms` is 3xn."""
        hms = np.atleast_2d(np.asarray(hms, float))
        return hms[0] * 15.0 + hms[1] / 4.0 + hms[2] / 240.0
