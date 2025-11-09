"""
2D Geometry Sampling Utilities
Converted from MATLAB sonic.SampleGeom2D
"""

import numpy as np
from ..geometry.points2 import Points2


class SampleGeom2D:
    """Generate points on 2D geometric objects"""

    @staticmethod
    def conic_pts(conic_obj, n_points=360, theta_range=None):
        """
        Generate points around a conic

        Args:
            conic_obj: Conic object to sample
            n_points: Number of points to generate
            theta_range: [theta_start, theta_end] in radians (default: [-π, π])

        Returns:
            Points2 object containing generated points
        """
        if theta_range is None:
            theta_range = [-np.pi, np.pi]

        if not conic_obj.proper:
            raise ValueError("Conic must be proper (non-degenerate)")

        # Extract explicit parameters
        expl = conic_obj.explicit
        x0, y0, a, b, psi = expl

        # Generate angles
        theta1, theta2 = theta_range
        if theta1 < theta2:
            t = np.linspace(theta1, theta2, n_points)
        else:
            t = np.linspace(np.mod(theta1, np.pi) - np.pi, theta2, n_points)

        if np.isinf(a):
            # Parabola (not yet fully implemented)
            raise NotImplementedError("Parabola sampling not yet implemented")
        else:
            if a > 0:
                # Ellipse
                x = a * np.cos(t)
                y = b * np.sin(t)
            else:
                # Hyperbola
                x = np.concatenate([a * np.cosh(t), -a * np.cosh(t)])
                y = np.concatenate([b * np.sinh(t), -b * np.sinh(t)])

        # Pair values
        points = np.vstack([x, y])

        # Rotation matrix
        R = np.array([
            [np.cos(psi), -np.sin(psi)],
            [np.sin(psi), np.cos(psi)]
        ])

        # Rotate and translate
        rot_points = R @ points
        transformed_points = rot_points + np.array([[x0], [y0]])

        return Points2(transformed_points)
