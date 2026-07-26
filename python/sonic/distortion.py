"""Distortion models (port of +sonic DistortionModel / Pinhole / BrownConrady).

`distort` maps ideal image-plane coords -> distorted coords; `undistort` inverts
it. All operate on sonic.Points2 (image-plane, R2).
"""

import numpy as np

from .points import Points2
from .tolerances import Tolerances


class DistortionModel:
    def distort(self, points: Points2) -> Points2:
        raise NotImplementedError

    def undistort(self, points: Points2):
        raise NotImplementedError


class Pinhole(DistortionModel):
    """Pass-through (no distortion)."""

    def distort(self, points: Points2) -> Points2:
        return points

    def undistort(self, points: Points2):
        return points, np.ones(points.n, dtype=bool)


class BrownConrady(DistortionModel):
    """Brown-Conrady radial (k1,k2,k3) + tangential (p1,p2) distortion.

    Matches OpenCV's model and SONIC's BrownConrady.m.
    """

    def __init__(self, p1, p2, k1, k2, k3):
        self.p1, self.p2 = p1, p2
        self.k1, self.k2, self.k3 = k1, k2, k3

    def distort(self, points: Points2) -> Points2:
        r = points.r2
        x, y = r[0], r[1]
        x2, y2, xy = x * x, y * y, x * y
        r2 = x2 + y2
        kc = 1 + self.k1 * r2 + self.k2 * r2 ** 2 + self.k3 * r2 ** 3
        xd = kc * x + 2 * self.p1 * xy + self.p2 * (r2 + 2 * x2)
        yd = kc * y + self.p1 * (r2 + 2 * y2) + 2 * self.p2 * xy
        return Points2(np.vstack((xd, yd)))

    def undistort(self, points: Points2):
        """Fixed-point iteration (mirrors BrownConrady.undistort)."""
        rd = points.r2
        xd, yd = rd[0], rd[1]
        cx, cy = xd.copy(), yd.copy()
        converge = np.zeros(points.n, dtype=bool)
        for _ in range(Tolerances.MaxIters):
            out = self.distort(Points2(np.vstack((cx, cy)))).r2
            ex, ey = out[0] - xd, out[1] - yd
            converge = (np.abs(ex) < Tolerances.UndistortTolBC) & \
                       (np.abs(ey) < Tolerances.UndistortTolBC)
            cx = cx - ex
            cy = cy - ey
            if np.all(converge):
                break
        return Points2(np.vstack((cx, cy))), converge
