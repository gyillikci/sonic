"""Points — projective/Euclidean point containers (port of +sonic Points2/Points3/PointsS2).

Points are stored as columns (3xn / 4xn homogeneous, 3xn unit vectors), matching
SONIC's column-major convention.
"""

import numpy as np

from .spherecoords import SphereCoords
from .tolerances import Tolerances


class Points2:
    """Points in P2/R2, including points at infinity (port of Points2.m).

    Construct from a 2xn (R2) or 3xn (P2, homogeneous) array.
    """

    def __init__(self, pts):
        pts = np.asarray(pts, float)
        if pts.ndim == 1:
            pts = pts[:, None]
        dim, n = pts.shape
        self.n = n
        if dim == 2:
            inf_pts = np.any(np.isinf(pts), axis=0)
            p2 = np.vstack((pts, np.ones((1, n))))
            p2[2, inf_pts] = 0.0
            self.p2 = p2
            self.inf_points = inf_pts
        elif dim == 3:
            small = np.abs(pts) < Tolerances.HomNorm
            if np.any(np.sum(small, axis=0) == 3):
                raise ValueError("[0;0;0] is not a member of P2")
            inf_pts = np.abs(pts[2]) < Tolerances.HomNorm
            pts = pts.copy()
            pts[:, ~inf_pts] = pts[:, ~inf_pts] / pts[2, ~inf_pts]
            pts[2, inf_pts] = 0.0
            self.p2 = pts
            self.inf_points = inf_pts
        else:
            raise ValueError("Must input a 2xn or 3xn matrix of 2D points")
        self.has_inf_points = bool(np.any(self.inf_points))

    @property
    def r2(self):
        val = self.p2[:2, :].copy()
        val[:, self.inf_points] = np.inf
        return val

    @property
    def r2_finite(self):
        return self.p2[:2, ~self.inf_points]

    @property
    def p2_finite(self):
        return self.p2[:, ~self.inf_points]

    @property
    def p2_infinite(self):
        return self.p2[:, self.inf_points]


class Points3:
    """Points in P3/R3, including points at infinity (port of Points3.m).

    Construct from a 3xn (R3) or 4xn (P3, homogeneous) array.
    """

    def __init__(self, pts):
        pts = np.asarray(pts, float)
        if pts.ndim == 1:
            pts = pts[:, None]
        dim, n = pts.shape
        self.n = n
        if dim == 3:
            inf_pts = np.any(np.isinf(pts), axis=0)
            p3 = np.vstack((pts, np.ones((1, n))))
            p3[3, inf_pts] = 0.0
            self.p3 = p3
            self.inf_points = inf_pts
        elif dim == 4:
            small = np.abs(pts) < Tolerances.SmallNumber
            if np.any(np.all(small, axis=0)):
                raise ValueError("[0;0;0;0] is not a member of P3")
            inf_pts = np.abs(pts[3]) < Tolerances.HomNorm
            pts = pts.copy()
            pts[:, ~inf_pts] = pts[:, ~inf_pts] / pts[3, ~inf_pts]
            pts[3, inf_pts] = 0.0
            self.p3 = pts
            self.inf_points = inf_pts
        else:
            raise ValueError("Must input a 3xn or 4xn matrix of 3D points")
        self.has_inf_points = bool(np.any(self.inf_points))

    @property
    def r3(self):
        val = self.p3[:3, :].copy()
        val[:, self.inf_points] = np.inf
        return val

    @property
    def r3_finite(self):
        return self.p3[:3, ~self.inf_points]

    @property
    def p3_finite(self):
        return self.p3[:, ~self.inf_points]

    @property
    def p3_infinite(self):
        return self.p3[:, self.inf_points]


class PointsS2:
    """Points on the unit 2-sphere (port of PointsS2.m).

    Construct from a 2xn array of (RA, Dec) radians, or a 3xn array of unit vectors.
    """

    def __init__(self, pts):
        pts = np.asarray(pts, float)
        if pts.ndim == 1:
            pts = pts[:, None]
        dim, n = pts.shape
        self.n = n
        if dim == 2:
            self.ra_dec = pts
            self.u = SphereCoords.raDecToCart(pts[0], pts[1])
        elif dim == 3:
            norms = np.linalg.norm(pts, axis=0)
            if np.any(np.abs(norms - 1.0) > Tolerances.UnitVecNorm1):
                raise ValueError("Vectors must be unit vectors (norm != 1)")
            self.u = pts
            ra, dec, _ = SphereCoords.cartToRaDec(pts)
            self.ra_dec = np.vstack((ra, dec))
        else:
            raise ValueError("Must input a 2xn (RA/Dec) or 3xn (unit vec) matrix")
