"""
2D Points class for SONIC
Converted from MATLAB sonic.Points2
"""

import numpy as np


class Points2:
    """
    2D points in projective geometry (homogeneous coordinates)

    Stores points in both Euclidean (r2) and projective (p2) representations:
    - r2: 2xN array of (x, y) coordinates
    - p2: 3xN array of (x, y, w) homogeneous coordinates
    """

    def __init__(self, points):
        """
        Initialize 2D points

        Args:
            points: Can be:
                - 2xN array (Euclidean coordinates)
                - 3xN array (Projective/homogeneous coordinates)
                - Points2 object (copy constructor)
        """
        if isinstance(points, Points2):
            # Copy constructor
            self._p2 = points._p2.copy()
            self._r2 = points._r2.copy()
            self._n = points._n
            self._has_inf_points = points._has_inf_points
            return

        points = np.atleast_2d(points).astype(float)

        if points.shape[0] == 2:
            # Euclidean input (x, y)
            self._r2 = points
            # Convert to homogeneous (x, y, 1)
            self._p2 = np.vstack([points, np.ones(points.shape[1])])
            self._has_inf_points = False

        elif points.shape[0] == 3:
            # Homogeneous input (x, y, w)
            self._p2 = points

            # Check for points at infinity
            w = points[2, :]
            self._has_inf_points = np.any(np.abs(w) < 1e-14)

            # Convert to Euclidean
            if self._has_inf_points:
                # Handle points at infinity
                self._r2 = np.zeros((2, points.shape[1]))
                finite_mask = np.abs(w) >= 1e-14
                self._r2[:, finite_mask] = points[:2, finite_mask] / w[finite_mask]
                self._r2[:, ~finite_mask] = np.inf
            else:
                self._r2 = points[:2, :] / w

        else:
            raise ValueError(f"Points must be 2xN or 3xN, got {points.shape}")

        self._n = points.shape[1]

    @property
    def r2(self):
        """Get Euclidean coordinates (2xN array)"""
        return self._r2

    @property
    def p2(self):
        """Get projective/homogeneous coordinates (3xN array)"""
        return self._p2

    @property
    def n(self):
        """Get number of points"""
        return self._n

    @property
    def has_inf_points(self):
        """Check if any points are at infinity"""
        return self._has_inf_points

    def __getitem__(self, key):
        """
        Index into points

        Args:
            key: Integer index or slice

        Returns:
            Points2 object with selected points
        """
        if isinstance(key, int):
            key = [key]

        return Points2(self._p2[:, key])

    def __len__(self):
        """Get number of points"""
        return self._n

    def __repr__(self):
        """String representation"""
        return f"Points2(n={self._n}, has_inf={self._has_inf_points})"

    def to_array(self):
        """Get Euclidean coordinates as numpy array (2xN)"""
        return self._r2.copy()
