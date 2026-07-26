"""Tolerances — numerical tolerances used across SONIC (port of +sonic/Tolerances.m)."""


class Tolerances:
    UnitVecNorm1 = 1e-9       # max deviation of a "unit" vector's norm from 1
    HomNorm = 1e-12           # below this a homogeneous coordinate is "at infinity"
    SmallNumber = 1e-12
    SmallAngle = 1e-9         # rad; below this, small-angle paths are used
    UndistortTolBC = 1e-9     # Brown-Conrady undistort convergence tolerance
    MaxIters = 100            # max fixed-point iterations for undistort
    SlopeAdjust = 1e-14       # k-vector slope safety margin (Xsi factor)
