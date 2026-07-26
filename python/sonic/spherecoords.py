"""SphereCoords — spherical <-> Cartesian conversions (port of +sonic/SphereCoords.m)."""

import numpy as np


class SphereCoords:
    @staticmethod
    def raDecToCart(ra_rad, dec_rad, r=1.0):
        """(RA, Dec) radians [+ optional radius] -> 3xn Cartesian vectors."""
        ra = np.atleast_1d(np.asarray(ra_rad, float))
        dec = np.atleast_1d(np.asarray(dec_rad, float))
        r = np.asarray(r, float)
        v = np.vstack((np.cos(dec) * np.cos(ra),
                       np.cos(dec) * np.sin(ra),
                       np.sin(dec)))
        return r * v

    @staticmethod
    def cartToRaDec(v):
        """3xn Cartesian -> (ra_rad, dec_rad, r). RA is atan2-based (may be negative)."""
        v = np.asarray(v, float)
        if v.ndim == 1:
            v = v[:, None]
        r = np.linalg.norm(v, axis=0)
        dec = np.arctan2(v[2], np.sqrt(v[0] ** 2 + v[1] ** 2))
        ra = np.arctan2(v[1], v[0])
        return ra, dec, r

    @staticmethod
    def azZenToCart(az, zen, radi=1.0):
        """Azimuth (from +x) and zenith (from +z), radians -> 3xn Cartesian."""
        az = np.atleast_1d(np.asarray(az, float))
        zen = np.atleast_1d(np.asarray(zen, float))
        if np.any((zen < 0) | (zen > np.pi)):
            raise ValueError("all zenith values must be between 0 and pi")
        return radi * np.vstack((np.sin(zen) * np.cos(az),
                                 np.sin(zen) * np.sin(az),
                                 np.cos(zen)))

    @staticmethod
    def cartToAzZen(v):
        """3xn Cartesian -> (az in [0,2pi), zen in [0,pi], radius)."""
        v = np.asarray(v, float)
        if v.ndim == 1:
            v = v[:, None]
        radi = np.linalg.norm(v, axis=0)
        radi_xy = np.linalg.norm(v[:2], axis=0)
        az = np.mod(np.arctan2(v[1], v[0]), 2 * np.pi)
        zen = np.pi / 2 - np.arctan2(v[2], radi_xy)
        return az, zen, radi
