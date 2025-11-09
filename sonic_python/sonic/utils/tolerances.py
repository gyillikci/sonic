"""
Tolerance constants for SONIC
Converted from MATLAB sonic.Tolerances
"""

import numpy as np


class Tolerances:
    """Numerical tolerance constants used throughout SONIC"""

    # Comparison tolerance for floating point equality
    CompZero = 1e-14

    # Small number tolerance
    SmallNumber = 1e-10

    # Condition number tolerance for matrix inversion
    CondTol = 1e-10

    # Conic-specific tolerances
    ConicDisc = 1e-8          # Discriminant tolerance for conic classification
    ConicCircle = 1e-8        # Circle detection tolerance
    ConicLocusDetOne = 1e-10  # Locus determinant = 1 tolerance
    IsOnConic = 1e-8          # Point on conic tolerance
    RepeatedPointTol = 1e-8   # Repeated point detection

    # Ellipse angle tolerance (for detecting circles)
    psiConicTol = 1e-8

    @classmethod
    def is_zero(cls, value):
        """Check if value is effectively zero"""
        return np.abs(value) < cls.CompZero

    @classmethod
    def are_equal(cls, a, b, tol=None):
        """Check if two values are equal within tolerance"""
        if tol is None:
            tol = cls.CompZero
        return np.abs(a - b) < tol
