#!/usr/bin/env python3
"""
Parallactic Angle Determination Example
Demonstrates the complete SONIC Python workflow for crater-based navigation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from sonic import (
    Points2, Conic, EllipseFitter, SampleGeom2D, Units
)

print("=" * 70)
print("SONIC PYTHON - Parallactic Angle Determination")
print("Crater-Based Optical Navigation Demonstration")
print("=" * 70)
print()

# =============================================================================
# STEP 1: Create a True Crater Ellipse
# =============================================================================
print("STEP 1: Creating True Crater Parameters")
print("-" * 70)

# Crater parameters (simulating Robbins database entry)
true_xc = 0.0      # Center x (km)
true_yc = 0.0      # Center y (km)
true_a = 5.0       # Semi-major axis (km)
true_b = 4.0       # Semi-minor axis (km)
true_psi_rad = np.deg2rad(35.0)  # Parallactic angle (radians)

# Create true conic
true_explicit = np.array([true_xc, true_yc, true_a, true_b, true_psi_rad])
true_conic = Conic(true_explicit, representation='explicit')

print(f"  Crater ellipse parameters:")
print(f"    Center: ({true_xc:.2f}, {true_yc:.2f}) km")
print(f"    Semi-axes: a={true_a:.2f} km, b={true_b:.2f} km")
print(f"    ★ TRUE PARALLACTIC ANGLE: {np.rad2deg(true_psi_rad):.2f}°")
print(f"    Conic type: {true_conic.type}")
print()

# =============================================================================
# STEP 2: Generate Synthetic Crater Rim Points
# =============================================================================
print("STEP 2: Generating Synthetic Crater Rim Points")
print("-" * 70)

# Generate perfect points
n_points = 100
crater_pts_perfect = SampleGeom2D.conic_pts(true_conic, n_points=n_points)

# Add realistic noise
pixel_noise_sigma = 0.5  # pixels
gsd = 10.0  # Ground Sample Distance (m/pixel) at 100 km altitude
noise_km = (pixel_noise_sigma * gsd) / 1000.0  # Convert to km

np.random.seed(42)
noise = noise_km * np.random.randn(2, n_points)
crater_pts_noisy = Points2(crater_pts_perfect.r2 + noise)

print(f"  Generated {n_points} crater rim points")
print(f"  Added noise: σ={pixel_noise_sigma:.2f} pixels ({pixel_noise_sigma*gsd:.1f} m)")
print(f"  Noise in km: σ={noise_km:.6f} km")
print()

# =============================================================================
# STEP 3: Fit Ellipse Using Different Methods
# =============================================================================
print("STEP 3: Fitting Ellipse to Noisy Rim Points")
print("-" * 70)

# Method 1: Least Squares
import time
t_start = time.time()
conic_ls = EllipseFitter.fit_ellipse(crater_pts_noisy, method='ls')
t_ls = (time.time() - t_start) * 1000

psi_ls = conic_ls.explicit[4]
error_ls = np.rad2deg(psi_ls - true_psi_rad)

print(f"  Least Squares (LS):")
print(f"    Fitted angle: {np.rad2deg(psi_ls):.2f}°")
print(f"    Error: {error_ls:.4f}°")
print(f"    Time: {t_ls:.2f} ms")

# Method 2: Semi-Hyper LS
t_start = time.time()
conic_shls = EllipseFitter.fit_ellipse(crater_pts_noisy, method='shls')
t_shls = (time.time() - t_start) * 1000

psi_shls = conic_shls.explicit[4]
error_shls = np.rad2deg(psi_shls - true_psi_rad)

print(f"  Semi-Hyper Least Squares (SHLS):")
print(f"    Fitted angle: {np.rad2deg(psi_shls):.2f}°")
print(f"    Error: {error_shls:.4f}°")
print(f"    Time: {t_shls:.2f} ms")

# Method 3: Hyper LS (BEST)
t_start = time.time()
conic_hls = EllipseFitter.fit_ellipse(crater_pts_noisy, method='hls')
t_hls = (time.time() - t_start) * 1000

psi_hls = conic_hls.explicit[4]
error_hls = np.rad2deg(psi_hls - true_psi_rad)

print(f"  Hyper Least Squares (HLS) - MOST ACCURATE:")
print(f"    Fitted angle: {np.rad2deg(psi_hls):.2f}°")
print(f"    Error: {error_hls:.4f}°")
print(f"    Time: {t_hls:.2f} ms")
print()

# =============================================================================
# STEP 4: Compute Covariance and Uncertainty
# =============================================================================
print("STEP 4: Computing Angle Covariance and Uncertainty")
print("-" * 70)

# Compute covariance
sigsqr_xy = noise_km**2
Pa = EllipseFitter.get_ellipse_covariance(conic_hls, crater_pts_noisy, sigsqr_xy)

print(f"  Computed 6×6 covariance matrix for implicit parameters")
print(f"  Diagonal elements (variances):")
for i in range(6):
    print(f"    P[{i},{i}] = {Pa[i,i]:.6e}")

# Approximate angle uncertainty
crater_radius = true_a
sigma_angle_approx = noise_km / (crater_radius * np.sqrt(n_points))
sigma_angle_deg = np.rad2deg(sigma_angle_approx)

print(f"\n  ESTIMATED ANGLE UNCERTAINTY:")
print(f"    1-sigma: ±{sigma_angle_deg:.4f}°")
print(f"    ★ 3-SIGMA: ±{3*sigma_angle_deg:.4f}°")
print()

# =============================================================================
# STEP 5: Display All Conic Representations
# =============================================================================
print("STEP 5: Multiple Conic Representations")
print("-" * 70)

print(f"  Explicit form [xc, yc, a, b, ψ]:")
expl = conic_hls.explicit
print(f"    xc = {expl[0]:.4f} km")
print(f"    yc = {expl[1]:.4f} km")
print(f"    a  = {expl[2]:.4f} km")
print(f"    b  = {expl[3]:.4f} km")
print(f"    ★ ψ  = {np.rad2deg(expl[4]):.2f}° ({expl[4]:.4f} rad)")

print(f"\n  Implicit form [A, B, C, D, E, F]:")
impl = conic_hls.implicit
for i, coeff in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
    print(f"    {coeff} = {impl[i]:.6f}")

print(f"\n  Locus matrix (3×3):")
for row in conic_hls.locus:
    print(f"    [{row[0]:8.4f}, {row[1]:8.4f}, {row[2]:8.4f}]")
print()

# =============================================================================
# STEP 6: Monte Carlo Validation
# =============================================================================
print("STEP 6: Monte Carlo Validation")
print("-" * 70)

n_trials = 500
fitted_angles = np.zeros(n_trials)

print(f"  Running {n_trials} trials...")

for trial in range(n_trials):
    # Generate noisy points
    noise_trial = noise_km * np.random.randn(2, n_points)
    pts_trial = Points2(crater_pts_perfect.r2 + noise_trial)

    # Fit
    conic_trial = EllipseFitter.fit_ellipse(pts_trial, method='hls')
    fitted_angles[trial] = conic_trial.explicit[4]

# Compute statistics
errors = fitted_angles - true_psi_rad
# Handle angle wrapping
errors = np.arctan2(np.sin(errors), np.cos(errors))

mean_error_deg = np.rad2deg(np.mean(errors))
std_error_deg = np.rad2deg(np.std(errors))
rmse_deg = np.rad2deg(np.sqrt(np.mean(errors**2)))

print(f"  Monte Carlo results:")
print(f"    Mean error: {mean_error_deg:.4f}°")
print(f"    Std deviation: {std_error_deg:.4f}° (empirical 1σ)")
print(f"    RMSE: {rmse_deg:.4f}°")
print(f"    ★ EMPIRICAL 3-SIGMA: ±{3*std_error_deg:.4f}°")
print()

# =============================================================================
# STEP 7: Scaling Analysis
# =============================================================================
print("STEP 7: Accuracy Scaling with Crater Size")
print("-" * 70)

print(f"  3σ angle uncertainty vs crater diameter:")
print(f"  (at 100 km altitude, {pixel_noise_sigma} px noise, {n_points} points)")
print()
print(f"  {'Diameter (km)':<15} {'Radius (km)':<15} {'3σ Angle (°)':<15}")
print(f"  {'-'*15} {'-'*15} {'-'*15}")

for diam in [1, 2, 5, 10, 20, 50]:
    radius = diam / 2.0
    sigma_3 = 3 * np.rad2deg(noise_km / (radius * np.sqrt(n_points)))
    print(f"  {diam:<15.1f} {radius:<15.1f} {sigma_3:<15.4f}")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print(f"Crater Parameters:")
print(f"  Size: {2*true_a:.1f} × {2*true_b:.1f} km")
print(f"  True parallactic angle: {np.rad2deg(true_psi_rad):.2f}°")
print()
print(f"Observation Conditions:")
print(f"  Altitude: 100 km")
print(f"  GSD: {gsd} m/pixel")
print(f"  Rim points: {n_points}")
print(f"  Pixel noise: {pixel_noise_sigma:.2f} pixels")
print()
print(f"Single Fit Results (HLS method):")
print(f"  Fitted angle: {np.rad2deg(psi_hls):.2f}°")
print(f"  Error: {error_hls:.4f}°")
print(f"  Analytical 3σ: ±{3*sigma_angle_deg:.4f}°")
print()
print(f"Monte Carlo Results ({n_trials} trials):")
print(f"  Empirical 1σ: ±{std_error_deg:.4f}°")
print(f"  ★ Empirical 3σ: ±{3*std_error_deg:.4f}°")
print()
print(f"Navigation Context:")
print(f"  Using 5-10 such craters at 100 km orbit:")
print(f"  Expected 3σ position accuracy: 50-150 meters")
print()
print(f"SONIC Python Components Used:")
print(f"  ✓ Points2 - 2D point handling")
print(f"  ✓ Conic - Ellipse representation (explicit/implicit/locus)")
print(f"  ✓ EllipseFitter - LS/SHLS/HLS fitting methods")
print(f"  ✓ SampleGeom2D - Point generation on conics")
print()
print("=" * 70)
print("Example completed successfully!")
print("=" * 70)
