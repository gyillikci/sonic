"""
Unit conversion utilities
Converted from MATLAB sonic.Units
"""

import numpy as np


class Units:
    """Unit conversion utilities for angles and distances"""

    @staticmethod
    def rad_to_deg(val_rad):
        """
        Convert radians to degrees

        Args:
            val_rad: Angle(s) in radians (scalar or array)

        Returns:
            Angle(s) in degrees
        """
        return np.rad2deg(val_rad)

    @staticmethod
    def deg_to_rad(val_deg):
        """
        Convert degrees to radians

        Args:
            val_deg: Angle(s) in degrees (scalar or array)

        Returns:
            Angle(s) in radians
        """
        return np.deg2rad(val_deg)

    @staticmethod
    def deg_to_hms(val_deg):
        """
        Convert degrees to Hours/Minutes/Seconds

        Args:
            val_deg: Angle(s) in degrees (scalar or array)

        Returns:
            3xN array [hours; minutes; seconds]
        """
        val_deg = np.atleast_1d(val_deg)

        # Hours
        hour = np.floor(val_deg / 15)

        # Minutes
        min_raw = 4 * np.mod(val_deg, 15)
        minute = np.floor(min_raw)

        # Seconds
        second = 60 * np.mod(min_raw, 1)

        return np.vstack([hour, minute, second])

    @staticmethod
    def hms_to_deg(val_hms):
        """
        Convert Hours/Minutes/Seconds to degrees

        Args:
            val_hms: 3xN array [hours; minutes; seconds]

        Returns:
            Angle(s) in degrees
        """
        return (val_hms[0, :] * 15) + (val_hms[1, :] / 4) + (val_hms[2, :] / 240)

    @staticmethod
    def urad_to_arcsec(val_urad):
        """
        Convert microradians to arcseconds

        Args:
            val_urad: Angle(s) in microradians

        Returns:
            Angle(s) in arcseconds
        """
        return val_urad * (180 * 3600) / (np.pi * 1e6)

    @staticmethod
    def arcsec_to_urad(val_arcsec):
        """
        Convert arcseconds to microradians

        Args:
            val_arcsec: Angle(s) in arcseconds

        Returns:
            Angle(s) in microradians
        """
        return val_arcsec * (np.pi * 1e6) / (180 * 3600)

    @staticmethod
    def au_to_km(val_au):
        """
        Convert astronomical units to kilometers

        Args:
            val_au: Distance(s) in AU

        Returns:
            Distance(s) in kilometers
        """
        return val_au * 149597870.7  # IAU 2012 definition

    @staticmethod
    def km_to_au(val_km):
        """
        Convert kilometers to astronomical units

        Args:
            val_km: Distance(s) in kilometers

        Returns:
            Distance(s) in AU
        """
        return val_km / 149597870.7
