"""
3D Points class for SONIC
Converted from MATLAB sonic.Points3
"""

import numpy as np


class Points3:
    """
    3D points in projective geometry (homogeneous coordinates)

    Stores points in both Euclidean (r3) and projective (p3) representations:
    - r3: 3xN array of (x, y, z) coordinates
    - p3: 4xN array of (x, y, z, w) homogeneous coordinates
    """

    def __init__(self, points):
        """
        Initialize 3D points

        Args:
            points: Can be:
                - 3xN array (Euclidean coordinates)
                - 4xN array (Projective/homogeneous coordinates)
                - Points3 object (copy constructor)
        """
        if isinstance(points, Points3):
            # Copy constructor
            self._p3 = points._p3.copy()
            self._r3 = points._r3.copy()
            self._n = points._n
            self._has_inf_points = points._has_inf_points
            return

        points = np.atleast_2d(points).astype(float)

        if points.shape[0] == 3:
            # Euclidean input (x, y, z)
            self._r3 = points
            # Convert to homogeneous (x, y, z, 1)
            self._p3 = np.vstack([points, np.ones(points.shape[1])])
            self._has_inf_points = False

        elif points.shape[0] == 4:
            # Homogeneous input (x, y, z, w)
            self._p3 = points

            # Check for points at infinity
            w = points[3, :]
            self._has_inf_points = np.any(np.abs(w) < 1e-14)

            # Convert to Euclidean
            if self._has_inf_points:
                # Handle points at infinity
                self._r3 = np.zeros((3, points.shape[1]))
                finite_mask = np.abs(w) >= 1e-14
                self._r3[:, finite_mask] = points[:3, finite_mask] / w[finite_mask]
                self._r3[:, ~finite_mask] = np.inf
            else:
                self._r3 = points[:3, :] / w

        else:
            raise ValueError(f"Points must be 3xN or 4xN, got {points.shape}")

        self._n = points.shape[1]

    @property
    def r3(self):
        """Get Euclidean coordinates (3xN array)"""
        return self._r3

    @property
    def p3(self):
        """Get projective/homogeneous coordinates (4xN array)"""
        return self._p3

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
            Points3 object with selected points
        """
        if isinstance(key, int):
            key = [key]

        return Points3(self._p3[:, key])

    def __len__(self):
        """Get number of points"""
        return self._n

    def __repr__(self):
        """String representation"""
        return f"Points3(n={self._n}, has_inf={self._has_inf_points})"

    def to_array(self):
        """Get Euclidean coordinates as numpy array (3xN)"""
        return self._r3.copy()
