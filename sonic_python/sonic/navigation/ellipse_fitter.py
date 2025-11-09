"""
Ellipse Fitter for SONIC
Converted from MATLAB sonic.EllipseFitter
Implements LS, SHLS, and HLS ellipse fitting methods
"""

import numpy as np
from scipy.linalg import svd, eig
from ..geometry.conic import Conic
from ..geometry.points2 import Points2
from ..utils.math_utils import Math


class EllipseFitter:
    """
    Ellipse fitting using various least-squares methods

    Methods:
    - 'ls': Least Squares (Total Least Squares)
    - 'shls': Semi-Hyper Least Squares
    - 'hls': Hyper Least Squares (most accurate, statistically optimal)

    References:
    1. Kanatani, K., & Rangarajan, P. (2011). Hyper least squares
       fitting of circles and ellipses. Computational Statistics & Data
       Analysis, 55(6), 2197-2208.
    2. Krause, M., Price, J., & Christian, J. A. (2023). Analytical
       Methods in Crater Rim Fitting and Pattern Recognition.
       AAS/AIAA Astrodynamics Specialist Conference.
    """

    @staticmethod
    def fit_ellipse(ellipse_pts, method='hls'):
        """
        Fit ellipse to 2D points using specified method

        Args:
            ellipse_pts: Points2 object containing rim points
            method: 'ls', 'shls', or 'hls'

        Returns:
            Conic object representing fitted ellipse

        Raises:
            ValueError: If method is not recognized or points are invalid
        """
        if not isinstance(ellipse_pts, Points2):
            raise TypeError("ellipse_pts must be a Points2 object")

        # Extract x and y points
        xy_vals = ellipse_pts.r2
        x_vals = xy_vals[0, :]
        y_vals = xy_vals[1, :]

        # Center points for numerical precision
        x_com = np.mean(x_vals)
        y_com = np.mean(y_vals)
        x_cent = x_vals - x_com
        y_cent = y_vals - y_com

        # Get xi vectors (6D representation)
        xi_vects = EllipseFitter._get_xi_vects(x_cent, y_cent)

        # Fit based on method
        method = method.lower()
        if method == 'ls':
            impl_soln = EllipseFitter._solve_tls(xi_vects)
        elif method == 'shls':
            impl_soln = EllipseFitter._solve_shls(xi_vects)
        elif method == 'hls':
            impl_soln = EllipseFitter._solve_hls(xi_vects)
        else:
            raise ValueError(
                f"Unknown method '{method}'. Use 'ls', 'shls', or 'hls'")

        # Convert to explicit form via Conic
        impl_conic = Conic(impl_soln, representation='implicit')
        expl_soln = impl_conic.explicit

        # Add back center of mass
        expl_soln[0] += x_com
        expl_soln[1] += y_com

        # Return Conic object
        conic_obj = Conic(expl_soln, representation='explicit')

        # Warn if not proper or not ellipse
        if not conic_obj.proper:
            print("Warning: Fitted conic is not proper")
        elif conic_obj.type != 'ellipse':
            print(f"Warning: Fitted conic is type '{conic_obj.type}', not ellipse")

        return conic_obj

    @staticmethod
    def get_ellipse_covariance(conic_obj, ellipse_pts, sigsqr_xy):
        """
        Compute analytical covariance of implicit solution

        Args:
            conic_obj: Fitted Conic object
            ellipse_pts: Points2 object with rim points
            sigsqr_xy: Variance of x,y coordinates (assumes isotropic)

        Returns:
            6x6 covariance matrix for implicit parameters

        Reference:
            Krause et al. (2023) Eq. 45h (with corrections)
        """
        # Get implicit solution
        impl_soln = conic_obj.implicit

        # Get xi vectors
        xy_vals = ellipse_pts.r2
        x_vals = xy_vals[0, :]
        y_vals = xy_vals[1, :]
        xi_vects = EllipseFitter._get_xi_vects(x_vals, y_vals)

        # Compute LS matrix
        M, xi_outer_all = EllipseFitter._compute_ls_matrix(xi_vects)
        M_pinv = np.linalg.pinv(M)

        # Number of samples
        n_samp = len(x_vals)

        # Get R0xi for covariance computation
        _, R0xi_all = EllipseFitter._compute_taubin_norm_factor(x_vals, y_vals)
        Rxi_all = sigsqr_xy * R0xi_all

        # Loop through observations
        n_coeff = 6
        sum_inner_mat = np.zeros((n_coeff, n_coeff))

        for i in range(len(x_vals)):
            interm_term = impl_soln.T @ Rxi_all[:, :, i] @ impl_soln
            inner_mat = (1/n_samp)**2 * interm_term * xi_outer_all[:, :, i]
            sum_inner_mat += inner_mat

        # Final covariance matrix
        Pa = M_pinv @ sum_inner_mat @ M_pinv.T

        return Pa

    # Private helper methods

    @staticmethod
    def _get_xi_vects(x_vals, y_vals):
        """
        Get 6D vector representation of 2D points

        For point (x, y), xi = [x², xy, y², x, y, 1]ᵀ

        Args:
            x_vals: X coordinates (N,)
            y_vals: Y coordinates (N,)

        Returns:
            Nx6 array of xi vectors
        """
        n_samples = len(x_vals)
        return np.column_stack([
            x_vals * x_vals,
            x_vals * y_vals,
            y_vals * y_vals,
            x_vals,
            y_vals,
            np.ones(n_samples)
        ])

    @staticmethod
    def _compute_ls_matrix(xi_vects):
        """
        Compute least-squares matrix M

        M = (1/n) Σ(xi * xi^T)

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            tuple: (M matrix 6x6, xi_outer_all 6x6xN)
        """
        n_coeff = 6
        n_samples = xi_vects.shape[0]

        # Reshape for vectorized outer product
        xi_deep_cols = xi_vects.T.reshape(n_coeff, 1, n_samples)
        xi_deep_rows = xi_vects.T.reshape(1, n_coeff, n_samples)

        # All outer products
        xi_outer_all = xi_deep_cols * xi_deep_rows

        # Sum and normalize
        M = np.sum(xi_outer_all, axis=2) / n_samples

        return M, xi_outer_all

    @staticmethod
    def _solve_tls(xi_vects):
        """
        Total Least Squares solution

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            6x1 implicit solution
        """
        # Get smallest right singular vector
        _, impl_soln = Math.get_smallest_r_sing_vector(xi_vects)
        return impl_soln

    @staticmethod
    def _compute_taubin_norm_factor(x_vals, y_vals):
        """
        Compute Taubin's normalization factor

        Args:
            x_vals: X coordinates
            y_vals: Y coordinates

        Returns:
            tuple: (N_taub 6x6, R0xi_all 6x6xN)
        """
        n_coeff = 6
        n_samples = len(x_vals)
        N_taub = np.zeros((n_coeff, n_coeff))
        R0xi_all = np.zeros((n_coeff, n_coeff, n_samples))

        for i in range(n_samples):
            # Jacobian of xi with respect to (x, y)
            dxidx = np.zeros((6, 2))
            dxidx[0, 0] = 2 * x_vals[i]
            dxidx[1, 0] = y_vals[i]
            dxidx[1, 1] = x_vals[i]
            dxidx[2, 1] = 2 * y_vals[i]
            dxidx[3, 0] = 1
            dxidx[4, 1] = 1

            R0xi = dxidx @ dxidx.T
            R0xi_all[:, :, i] = R0xi
            N_taub += R0xi

        N_taub /= n_samples

        return N_taub, R0xi_all

    @staticmethod
    def _compute_s_fcn(B):
        """
        Matrix symmetrization function S(B) = 0.5 * (B + B^T)

        Args:
            B: Square matrix

        Returns:
            Symmetrized matrix
        """
        return 0.5 * (B + B.T)

    @staticmethod
    def _compute_shls_norm_factor(xi_vects):
        """
        Compute Semi-Hyper Least Squares normalization factor

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            tuple: (N_shls 6x6, R0xi_all 6x6xN)
        """
        # Extract x, y
        x_vals = xi_vects[:, 3]
        y_vals = xi_vects[:, 4]

        # Get Taubin normalization
        N_taub, R0xi_all = EllipseFitter._compute_taubin_norm_factor(
            x_vals, y_vals)

        # Compute SHLS normalization
        xi_cent = np.mean(xi_vects, axis=0)
        e_vec = np.array([1, 0, 1, 0, 0, 0])
        B = np.outer(xi_cent, e_vec)
        SB = EllipseFitter._compute_s_fcn(B)
        N_shls = N_taub + 2 * SB

        return N_shls, R0xi_all

    @staticmethod
    def _solve_shls(xi_vects):
        """
        Semi-Hyper Least Squares solution

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            6x1 implicit solution
        """
        # Get LS matrix
        M, _ = EllipseFitter._compute_ls_matrix(xi_vects)

        # Get SHLS normalization factor
        N_shls, _ = EllipseFitter._compute_shls_norm_factor(xi_vects)

        # Solve generalized eigenvalue problem
        impl_soln = Math.solve_gen_eigval_smallest_lambda(M, N_shls)

        return impl_soln

    @staticmethod
    def _compute_hls_norm_factor(xi_vects):
        """
        Compute Hyper Least Squares normalization factor

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            tuple: (N_hls 6x6, M 6x6)
        """
        n_samples = xi_vects.shape[0]

        # Get required matrices
        M, xi_outer_all = EllipseFitter._compute_ls_matrix(xi_vects)
        N_shls, R0xi_all = EllipseFitter._compute_shls_norm_factor(xi_vects)

        # Pseudoinverse of M
        M_pinv = np.linalg.pinv(M)

        # Number of coefficients
        n_coeff = 6

        # Compute summation terms
        sum_term = np.zeros((n_coeff, n_coeff))

        for i in range(n_samples):
            R0xi = R0xi_all[:, :, i]
            xi = xi_vects[i, :]
            xi_outer_i = xi_outer_all[:, :, i]

            # Individual terms
            term1 = np.trace(M_pinv @ R0xi) * xi_outer_i
            term2 = (xi.T @ M_pinv @ xi) * R0xi
            term3 = 2 * EllipseFitter._compute_s_fcn(
                R0xi @ M_pinv @ xi_outer_i)

            sum_term += term1 + term2 + term3

        # Final normalization
        N_hls = N_shls - (1 / (n_samples**2)) * sum_term

        return N_hls, M

    @staticmethod
    def _solve_hls(xi_vects):
        """
        Hyper Least Squares solution (most accurate)

        Args:
            xi_vects: Nx6 array of xi vectors

        Returns:
            6x1 implicit solution
        """
        # Get HLS normalization factor
        N_hls, M = EllipseFitter._compute_hls_norm_factor(xi_vects)

        # Solve generalized eigenvalue problem
        impl_soln = Math.solve_gen_eigval_smallest_lambda(M, N_hls)

        return impl_soln
