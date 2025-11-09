"""
Conic class for SONIC
Converted from MATLAB sonic.Conic
Handles ellipses and other conic sections in multiple representations
"""

import numpy as np
from scipy.linalg import eig
from ..utils.math_utils import Math
from ..utils.tolerances import Tolerances


class Conic:
    """
    Conic section representation

    Supports multiple representations:
    - Implicit: [A, B, C, D, E, F] for Ax² + Bxy + Cy² + Dx + Ey + F = 0
    - Explicit: [xc, yc, a, b, ψ] for center, semi-axes, and rotation angle
    - Locus: 3x3 matrix representation
    - Envelope: 3x3 dual conic representation
    """

    def __init__(self, raw_conic, representation='auto'):
        """
        Initialize conic from various representations

        Args:
            raw_conic: Can be:
                - 5-element array: explicit [xc, yc, a, b, psi]
                - 6-element array: implicit [A, B, C, D, E, F]
                - 3x3 array: locus or envelope (specify with representation)
            representation: 'auto', 'explicit', 'implicit', 'locus', or 'envelope'
        """
        raw_conic = np.atleast_1d(raw_conic).astype(float)

        # Determine input type
        if raw_conic.ndim == 1:
            if len(raw_conic) == 5:
                representation = 'explicit'
            elif len(raw_conic) == 6:
                representation = 'implicit'
            else:
                raise ValueError(f"1D input must have 5 or 6 elements, got {len(raw_conic)}")
        elif raw_conic.shape == (3, 3):
            if representation == 'auto':
                raise ValueError("Must specify 'locus' or 'envelope' for 3x3 input")
        else:
            raise ValueError(f"Invalid conic shape: {raw_conic.shape}")

        # Process based on representation
        if representation == 'explicit':
            self._init_from_explicit(raw_conic)
        elif representation == 'implicit':
            self._init_from_implicit(raw_conic)
        elif representation == 'locus':
            self._init_from_locus(raw_conic)
        elif representation == 'envelope':
            self._init_from_envelope(raw_conic)
        else:
            raise ValueError(f"Unknown representation: {representation}")

    def _init_from_explicit(self, explicit):
        """Initialize from explicit parameters [xc, yc, a, b, psi]"""
        xc, yc, a, b, psi = explicit

        if np.isinf(a):
            raise NotImplementedError("Parabola not yet fully implemented")

        # Build locus matrix
        if a > 0:
            # Ellipse
            A = a**2 * np.sin(psi)**2 + b**2 * np.cos(psi)**2
            B = 2 * (b**2 - a**2) * np.cos(psi) * np.sin(psi)
            C = a**2 * np.cos(psi)**2 + b**2 * np.sin(psi)**2
        else:
            # Hyperbola
            A = b**2 * np.cos(psi)**2 - a**2 * np.sin(psi)**2
            B = 2 * (a**2 + b**2) * np.cos(psi) * np.sin(psi)
            C = b**2 * np.sin(psi)**2 - a**2 * np.cos(psi)**2

        D = -2*A*xc - B*yc
        E = -B*xc - 2*C*yc
        F = A*xc**2 + B*xc*yc + C*yc**2 - a**2 * b**2

        self._locus = np.array([
            [A, B/2, D/2],
            [B/2, C, E/2],
            [D/2, E/2, F]
        ])

        self._locus = Math.A_to_det1(self._locus)
        self._explicit = explicit
        self._implicit = self._locus_to_implicit(self._locus)
        self._envelope = self._locus_to_envelope(self._locus)
        self._proper = self._is_proper_conic(self._locus)
        self._stable = True
        self._conic_type = self._get_type(self._locus)

    def _init_from_implicit(self, implicit):
        """Initialize from implicit coefficients [A, B, C, D, E, F]"""
        # Convert to locus
        self._locus = self._implicit_to_locus(implicit)

        # Check if proper
        self._proper = self._is_proper_conic(self._locus)
        self._stable = self._is_numerically_stable(self._locus)

        # Calculate normalized implicit to match locus sign
        self._implicit = self._locus_to_implicit(self._locus)

        # Calculate envelope
        self._envelope = self._locus_to_envelope(self._locus)

        # Convert to explicit if proper
        if self._proper:
            self._explicit = self._locus_to_explicit(self._locus)
        else:
            self._explicit = None

        self._conic_type = self._get_type(self._locus)

    def _init_from_locus(self, locus):
        """Initialize from locus matrix"""
        # Normalize to det = 1
        self._locus = Math.A_to_det1(locus)

        self._proper = self._is_proper_conic(self._locus)
        self._stable = self._is_numerically_stable(self._locus)
        self._implicit = self._locus_to_implicit(self._locus)
        self._envelope = self._locus_to_envelope(self._locus)

        if self._proper:
            self._explicit = self._locus_to_explicit(self._locus)
        else:
            self._explicit = None

        self._conic_type = self._get_type(self._locus)

    def _init_from_envelope(self, envelope):
        """Initialize from envelope matrix"""
        self._envelope = Math.A_to_det1(envelope)

        # Check if proper
        self._proper = self._is_proper_conic(self._envelope, is_envelope=True)

        if not self._proper:
            raise ValueError("Degenerate conics not accepted as envelope")

        self._stable = self._is_numerically_stable(self._envelope, is_envelope=True)

        # Get locus
        self._locus = self._envelope_to_locus(self._envelope)

        # Get implicit
        self._implicit = self._locus_to_implicit(self._locus)

        # Convert to explicit
        self._explicit = self._locus_to_explicit(self._locus)

        self._conic_type = self._get_type(self._locus)

    # Properties
    @property
    def explicit(self):
        """Get explicit parameters [xc, yc, a, b, psi]"""
        return self._explicit

    @property
    def implicit(self):
        """Get implicit coefficients [A, B, C, D, E, F]"""
        return self._implicit

    @property
    def locus(self):
        """Get locus matrix (3x3)"""
        return self._locus

    @property
    def envelope(self):
        """Get envelope matrix (3x3)"""
        return self._envelope

    @property
    def proper(self):
        """Check if conic is proper (non-degenerate)"""
        return self._proper

    @property
    def stable(self):
        """Check if conic is numerically stable"""
        return self._stable

    @property
    def type(self):
        """Get conic type (ellipse, circle, hyperbola, parabola, etc.)"""
        return self._conic_type

    def rotate(self, angle):
        """
        Rotate conic by given angle

        Args:
            angle: Rotation angle in radians

        Returns:
            New Conic object rotated by angle
        """
        rot_matrix_inv = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])

        new_locus = rot_matrix_inv.T @ self._locus @ rot_matrix_inv
        return Conic(new_locus, representation='locus')

    # Static helper methods
    @staticmethod
    def _implicit_to_locus(implicit):
        """Convert implicit to locus representation"""
        A, B, C, D, E, F = implicit
        locus = np.array([
            [A, B/2, D/2],
            [B/2, C, E/2],
            [D/2, E/2, F]
        ])
        return Math.A_to_det1(locus)

    @staticmethod
    def _locus_to_implicit(locus):
        """Convert locus to normalized implicit representation"""
        A = locus[0, 0]
        B = locus[0, 1] * 2
        C = locus[1, 1]
        D = locus[0, 2] * 2
        E = locus[1, 2] * 2
        F = locus[2, 2]

        implicit = np.array([A, B, C, D, E, F])
        return implicit / np.linalg.norm(implicit)

    @staticmethod
    def _locus_to_envelope(locus):
        """Convert locus to envelope (uses adjoint for degenerates)"""
        envelope = Math.adjoint3x3(locus)
        return Math.A_to_det1(envelope)

    @staticmethod
    def _envelope_to_locus(envelope):
        """Convert envelope to locus"""
        locus = Math.adjoint3x3(envelope)
        return Math.A_to_det1(locus)

    @staticmethod
    def _locus_to_explicit(locus):
        """
        Convert locus to explicit parameters [xc, yc, a, b, psi]
        This is the KEY method for extracting the parallactic angle!
        """
        # Check numerical stability
        stable = Conic._is_numerically_stable(locus)
        if not stable:
            # Work with translated conic
            locus, origin = Conic._translate_conic_matrix(locus)

        # Eigendecomposition of 2x2 submatrix (Conic.m line 659)
        Q = locus[:2, :2]
        eigenvalues, eigenvectors = eig(Q)

        # Sort eigenvalues
        idx = np.argsort(np.abs(eigenvalues))
        eigenvalues = eigenvalues[idx].real
        eigenvectors = eigenvectors[:, idx].real

        l1 = np.abs(eigenvalues[0])
        l2 = np.abs(eigenvalues[1])
        v2 = eigenvectors[:, 1]  # Eigenvector for larger eigenvalue

        # Extract locus elements
        A = locus[0, 0]
        B = locus[0, 1] * 2
        C = locus[1, 1]
        D = locus[0, 2] * 2
        E = locus[1, 2] * 2
        F = locus[2, 2]

        disc = B**2 - A*C
        conic_type = Conic._get_type(locus)

        if conic_type in ['ellipse', 'circle', 'hyperbola']:
            # Determinant
            deter = np.linalg.det(locus)

            # Semi-axes (make sure a is always larger)
            a = np.sqrt(deter / (l1 * l2**2))
            b = np.sqrt(deter / (l1**2 * l2))

            # Center
            xc = (C*D - B*E) / disc if abs(disc) > 1e-14 else 0
            yc = (A*E - B*D) / disc if abs(disc) > 1e-14 else 0

            # Parallactic angle (Conic.m line 691) ★ THIS IS THE KEY LINE ★
            if abs(a - b) < Tolerances.psiConicTol:
                psi = 0  # Circle
            else:
                psi = np.arctan2(v2[1], v2[0])

            if conic_type == 'hyperbola':
                a = -a
                b = -b

        elif conic_type == 'parabola':
            raise NotImplementedError("Parabola explicit parameters not yet implemented")
        else:
            raise ValueError("Explicit parameterization only for proper conics")

        explicit = np.array([xc, yc, a, b, psi])

        if not stable:
            # Add back the translation
            explicit[:2] += origin

        return explicit

    @staticmethod
    def _is_proper_conic(matrix, is_envelope=False):
        """Check if conic is proper (non-degenerate)"""
        rcond_num = np.linalg.cond(matrix)
        proper = rcond_num <= 1.0 / Tolerances.CondTol

        if not proper:
            # Check if numerical instability
            stable = Conic._is_numerically_stable(matrix, is_envelope)
            if not stable:
                proper = True

        return proper

    @staticmethod
    def _is_numerically_stable(matrix, is_envelope=False):
        """Check if conic representation is numerically stable"""
        stable = True
        rcond_num = np.linalg.cond(matrix)
        proper = rcond_num <= 1.0 / Tolerances.CondTol

        if not proper:
            # Try translating
            new_matrix, _ = Conic._translate_conic_matrix(matrix, is_envelope)
            rcond_num = np.linalg.cond(new_matrix)

            if rcond_num <= 1.0 / Tolerances.CondTol:
                stable = False

        return stable

    @staticmethod
    def _translate_conic_matrix(matrix, is_envelope=False):
        """Translate conic by its center (simplified version)"""
        # Simplified translation - just return matrix for now
        # Full implementation would find center and translate
        return matrix, np.array([0, 0])

    @staticmethod
    def _get_type(locus):
        """Determine conic type (ellipse, circle, hyperbola, parabola, etc.)"""
        locus = Math.A_to_det1(locus)

        A = locus[0, 0]
        B = locus[0, 1] * 2
        C = locus[1, 1]

        # Discriminant
        disc = B**2 - 4*A*C

        proper = Conic._is_proper_conic(locus)

        if proper:
            if disc <= -Tolerances.ConicDisc:
                if abs((A - C)**2 + B**2) < Tolerances.ConicCircle:
                    return 'circle'
                else:
                    return 'ellipse'
            elif disc >= Tolerances.ConicDisc:
                return 'hyperbola'
            else:
                return 'parabola'
        else:
            if disc <= -Tolerances.ConicDisc:
                return 'point'
            elif disc >= Tolerances.ConicDisc:
                return 'intersecting_lines'
            else:
                return 'parallel_lines'

    def __repr__(self):
        """String representation"""
        if self._explicit is not None:
            xc, yc, a, b, psi = self._explicit
            return (f"Conic(type={self._conic_type}, "
                    f"center=({xc:.3f}, {yc:.3f}), "
                    f"a={a:.3f}, b={b:.3f}, psi={np.rad2deg(psi):.2f}°)")
        else:
            return f"Conic(type={self._conic_type}, degenerate)"
