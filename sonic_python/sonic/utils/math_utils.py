"""
Mathematical utilities for SONIC
Converted from MATLAB sonic.Math
"""

import numpy as np
from scipy.linalg import svd, eig


class Math:
    """Mathematical utility functions"""

    @staticmethod
    def crossmat(v):
        """
        Create skew-symmetric cross product matrix

        Args:
            v: 3D vector or 3xN array of vectors

        Returns:
            3x3 or 3x3xN array of cross-product matrices
        """
        v = np.atleast_2d(v)
        if v.shape[0] != 3:
            v = v.T

        if v.shape[1] == 1:
            # Single vector
            return np.array([
                [0, -v[2, 0], v[1, 0]],
                [v[2, 0], 0, -v[0, 0]],
                [-v[1, 0], v[0, 0], 0]
            ])
        else:
            # Multiple vectors
            n = v.shape[1]
            result = np.zeros((3, 3, n))
            for i in range(n):
                result[:, :, i] = np.array([
                    [0, -v[2, i], v[1, i]],
                    [v[2, i], 0, -v[0, i]],
                    [-v[1, i], v[0, i], 0]
                ])
            return result

    @staticmethod
    def get_smallest_r_sing_vector(matrix):
        """
        Get right singular vector corresponding to smallest singular value

        Args:
            matrix: Input matrix

        Returns:
            tuple: (smallest_singular_value, corresponding_right_vector)
        """
        U, s, Vt = svd(matrix)
        # In Python/NumPy, Vt is already transposed
        return s[-1], Vt[-1, :]

    @staticmethod
    def solve_gen_eigval_smallest_lambda(M, N):
        """
        Solve generalized eigenvalue problem for smallest eigenvalue
        Solves: M*v = lambda*N*v

        Args:
            M: Matrix M
            N: Matrix N

        Returns:
            Eigenvector corresponding to smallest eigenvalue
        """
        # Solve generalized eigenvalue problem
        eigenvalues, eigenvectors = eig(M, N)

        # Find smallest eigenvalue (by magnitude)
        idx = np.argmin(np.abs(eigenvalues))

        return eigenvectors[:, idx]

    @staticmethod
    def A_to_det1(A):
        """
        Normalize matrix to have determinant ±1

        Args:
            A: Input matrix

        Returns:
            Normalized matrix with det(A) = ±1
        """
        det_A = np.linalg.det(A)
        if abs(det_A) < 1e-14:
            return A  # Degenerate matrix
        return A / np.cbrt(det_A)

    @staticmethod
    def adjoint3x3(A):
        """
        Compute adjoint (adjugate) of 3x3 matrix
        adj(A) = det(A) * inv(A)

        Args:
            A: 3x3 matrix

        Returns:
            3x3 adjoint matrix
        """
        # For 3x3 matrix, adjoint is transpose of cofactor matrix
        a11, a12, a13 = A[0, :]
        a21, a22, a23 = A[1, :]
        a31, a32, a33 = A[2, :]

        # Cofactors
        c11 = a22*a33 - a23*a32
        c12 = -(a21*a33 - a23*a31)
        c13 = a21*a32 - a22*a31

        c21 = -(a12*a33 - a13*a32)
        c22 = a11*a33 - a13*a31
        c23 = -(a11*a32 - a12*a31)

        c31 = a12*a23 - a13*a22
        c32 = -(a11*a23 - a13*a21)
        c33 = a11*a22 - a12*a21

        # Transpose of cofactor matrix
        return np.array([
            [c11, c21, c31],
            [c12, c22, c32],
            [c13, c23, c33]
        ])

    @staticmethod
    def normalize_vector(v):
        """
        Normalize vector to unit length

        Args:
            v: Vector (1D or 2D array)

        Returns:
            Unit vector
        """
        return v / np.linalg.norm(v)

    @staticmethod
    def rotation_matrix(axis, angle):
        """
        Create rotation matrix from axis-angle representation

        Args:
            axis: 3D rotation axis (will be normalized)
            angle: Rotation angle in radians

        Returns:
            3x3 rotation matrix
        """
        axis = Math.normalize_vector(axis)
        K = Math.crossmat(axis.reshape(3, 1))
        I = np.eye(3)

        # Rodrigues' rotation formula
        return I + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
