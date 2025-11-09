#!/usr/bin/env python3
"""
Crater Parallactic Angle Determination Demo
Demonstrates ellipse fitting to crater rims and angle extraction
Simulates the SONIC workflow in Python
"""

import numpy as np
from scipy.linalg import svd, eig
import sys

print("=" * 70)
print("PARALLACTIC ANGLE DETERMINATION FROM CRATER IDENTIFICATION")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Define True Crater Parameters
# ============================================================================
print("STEP 1: Defining True Crater Parameters...")

# Crater ellipse parameters (in km, simulating 100 km orbital altitude)
true_xc = 0.0      # center x
true_yc = 0.0      # center y
true_a = 5.0       # semi-major axis (5 km)
true_b = 4.0       # semi-minor axis (4 km)
true_psi = np.deg2rad(35.0)  # parallactic angle (35 degrees)

print(f"  Crater center: ({true_xc:.2f}, {true_yc:.2f}) km")
print(f"  Semi-major axis a: {true_a:.2f} km")
print(f"  Semi-minor axis b: {true_b:.2f} km")
print(f"  TRUE PARALLACTIC ANGLE ψ: {np.rad2deg(true_psi):.2f}° ({true_psi:.4f} rad)")
print()

# ============================================================================
# STEP 2: Generate Synthetic Crater Rim Points
# ============================================================================
print("STEP 2: Generating Synthetic Crater Rim Points...")

n_points = 100
theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)

# Generate points on canonical ellipse
x_canonical = true_a * np.cos(theta)
y_canonical = true_b * np.sin(theta)

# Rotation matrix
R = np.array([[np.cos(true_psi), -np.sin(true_psi)],
              [np.sin(true_psi),  np.cos(true_psi)]])

# Rotate and translate
points_perfect = R @ np.vstack([x_canonical, y_canonical]) + np.array([[true_xc], [true_yc]])

# Add noise (simulating 0.5 pixel noise at 10 m/pixel GSD)
pixel_noise_sigma = 0.5  # pixels
gsd = 10.0  # meters/pixel
noise_km = (pixel_noise_sigma * gsd) / 1000.0  # convert to km

np.random.seed(42)  # For reproducibility
noise = noise_km * np.random.randn(2, n_points)
points_noisy = points_perfect + noise

print(f"  Generated {n_points} rim points")
print(f"  Added noise: σ={pixel_noise_sigma:.2f} pixels ({pixel_noise_sigma*gsd:.1f} m on ground)")
print(f"  Noise in km: σ={noise_km:.6f} km")
print()

# ============================================================================
# STEP 3: Ellipse Fitting (Least Squares Method)
# ============================================================================
print("STEP 3: Fitting Ellipse using Least Squares...")

# Extract noisy points
x = points_noisy[0, :]
y = points_noisy[1, :]

# Center points for numerical stability (like SONIC does)
x_mean = np.mean(x)
y_mean = np.mean(y)
x_centered = x - x_mean
y_centered = y - y_mean

# Build design matrix (xi vectors from EllipseFitter.m line 638)
# xi = [x^2, xy, y^2, x, y, 1]
D = np.column_stack([
    x_centered**2,
    x_centered * y_centered,
    y_centered**2,
    x_centered,
    y_centered,
    np.ones(n_points)
])

# Solve using SVD (Total Least Squares - like EllipseFitter.m line 282)
# Find the eigenvector corresponding to smallest eigenvalue
U, S, Vt = svd(D)
implicit_centered = Vt[-1, :]  # Last row of V (smallest singular value)

print(f"  Computed implicit parameters (centered): {implicit_centered}")

# Extract implicit coefficients
A, B, C, D_coef, E_coef, F = implicit_centered

# ============================================================================
# STEP 4: Convert Implicit to Explicit (Extract Parallactic Angle!)
# ============================================================================
print("\nSTEP 4: Extracting Parallactic Angle from Implicit Form...")

# Build locus matrix (like Conic.m line 578)
locus_centered = np.array([
    [A,      B/2,    D_coef/2],
    [B/2,    C,      E_coef/2],
    [D_coef/2, E_coef/2, F]
])

# Extract ellipse parameters via eigendecomposition (Conic.m line 659-692)
# The 2x2 submatrix determines the ellipse orientation
Q = locus_centered[:2, :2]
eigenvalues, eigenvectors = eig(Q)

# Sort by eigenvalue magnitude
idx = np.argsort(np.abs(eigenvalues))
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# The eigenvector for the larger eigenvalue points along major axis
v2 = eigenvectors[:, 1]  # Eigenvector for larger eigenvalue

# Extract parallactic angle using atan2 (Conic.m line 691)
psi_fitted = np.arctan2(v2[1], v2[0])

# Normalize angle to [0, 2π)
if psi_fitted < 0:
    psi_fitted += 2*np.pi

# Extract semi-axes from eigenvalues
discriminant = B**2 - A*C
determinant = np.linalg.det(locus_centered)

if determinant != 0:
    lambda1 = np.abs(eigenvalues[0])
    lambda2 = np.abs(eigenvalues[1])
    a_fitted = np.sqrt(np.abs(determinant / (lambda1 * lambda2**2)))
    b_fitted = np.sqrt(np.abs(determinant / (lambda1**2 * lambda2)))
else:
    a_fitted = np.nan
    b_fitted = np.nan

# Extract center (add back the mean we subtracted)
xc_fitted = x_mean + (C*D_coef - B*E_coef) / (discriminant) if discriminant != 0 else x_mean
yc_fitted = y_mean + (A*E_coef - B*D_coef) / (discriminant) if discriminant != 0 else y_mean

print(f"  Eigenvalues: {eigenvalues}")
print(f"  Major axis eigenvector: {v2}")
print(f"  ★ FITTED PARALLACTIC ANGLE: {np.rad2deg(psi_fitted):.2f}° ({psi_fitted:.4f} rad)")
print()

# ============================================================================
# STEP 5: Compute Uncertainty Estimate
# ============================================================================
print("STEP 5: Estimating Angle Uncertainty...")

# Approximate formula: σ_ψ ≈ σ_noise / (radius * sqrt(n_points))
crater_radius = true_a
sigma_angle = noise_km / (crater_radius * np.sqrt(n_points))
sigma_angle_deg = np.rad2deg(sigma_angle)

print(f"  Approximate 1-sigma uncertainty: {sigma_angle_deg:.4f}° ({sigma_angle:.6f} rad)")
print(f"  ★ 3-SIGMA UNCERTAINTY: ±{3*sigma_angle_deg:.4f}°")
print()

# ============================================================================
# STEP 6: Error Analysis
# ============================================================================
print("STEP 6: Error Analysis...")

angle_error = psi_fitted - true_psi
# Handle angle wrapping
if angle_error > np.pi:
    angle_error -= 2*np.pi
elif angle_error < -np.pi:
    angle_error += 2*np.pi

angle_error_deg = np.rad2deg(angle_error)

print(f"  True angle:       {np.rad2deg(true_psi):.2f}°")
print(f"  Fitted angle:     {np.rad2deg(psi_fitted):.2f}°")
print(f"  Angle error:      {angle_error_deg:.4f}°")
print(f"  Error magnitude:  {np.abs(angle_error_deg):.4f}°")
print()

# ============================================================================
# STEP 7: Monte Carlo Simulation for Realistic Uncertainty
# ============================================================================
print("STEP 7: Running Monte Carlo Simulation...")

n_trials = 1000
fitted_angles = np.zeros(n_trials)

for trial in range(n_trials):
    # Generate noisy points
    noise_trial = noise_km * np.random.randn(2, n_points)
    points_trial = points_perfect + noise_trial

    x_trial = points_trial[0, :] - np.mean(points_trial[0, :])
    y_trial = points_trial[1, :] - np.mean(points_trial[1, :])

    # Build design matrix
    D_trial = np.column_stack([
        x_trial**2, x_trial*y_trial, y_trial**2,
        x_trial, y_trial, np.ones(n_points)
    ])

    # SVD
    _, _, Vt_trial = svd(D_trial)
    impl = Vt_trial[-1, :]

    # Extract angle
    locus_trial = np.array([
        [impl[0], impl[1]/2, impl[3]/2],
        [impl[1]/2, impl[2], impl[4]/2],
        [impl[3]/2, impl[4]/2, impl[5]]
    ])

    Q_trial = locus_trial[:2, :2]
    evals, evecs = eig(Q_trial)
    idx = np.argsort(np.abs(evals))
    v2_trial = evecs[:, idx[1]]

    psi_trial = np.arctan2(v2_trial[1], v2_trial[0])
    if psi_trial < 0:
        psi_trial += 2*np.pi

    fitted_angles[trial] = psi_trial

# Compute statistics
errors = fitted_angles - true_psi
# Handle wrapping
errors = np.arctan2(np.sin(errors), np.cos(errors))

mean_error = np.mean(errors)
std_error = np.std(errors)
rmse = np.sqrt(np.mean(errors**2))

print(f"  Monte Carlo trials: {n_trials}")
print(f"  Mean error:     {np.rad2deg(mean_error):.4f}°")
print(f"  Std deviation:  {np.rad2deg(std_error):.4f}° (empirical 1-sigma)")
print(f"  RMSE:           {np.rad2deg(rmse):.4f}°")
print(f"  ★ EMPIRICAL 3-SIGMA: ±{3*np.rad2deg(std_error):.4f}°")
print()

# ============================================================================
# STEP 8: Coordinate Frame Information
# ============================================================================
print("STEP 8: Coordinate Frame Context...")

lat_deg = 10.0
lon_deg = -45.0
lat_rad = np.deg2rad(lat_deg)
lon_rad = np.deg2rad(lon_deg)

# ENU frame vectors (from Robbins.m lines 274-278)
east = np.array([-np.sin(lon_rad), np.cos(lon_rad), 0])
north = np.array([-np.sin(lat_rad)*np.cos(lon_rad),
                  -np.sin(lat_rad)*np.sin(lon_rad),
                  np.cos(lat_rad)])
up = np.array([np.cos(lat_rad)*np.cos(lon_rad),
               np.cos(lat_rad)*np.sin(lon_rad),
               np.sin(lat_rad)])

print(f"  Local ENU frame at Lat={lat_deg}°, Lon={lon_deg}°")
print(f"  East vector:  [{east[0]:.4f}, {east[1]:.4f}, {east[2]:.4f}]")
print(f"  North vector: [{north[0]:.4f}, {north[1]:.4f}, {north[2]:.4f}]")
print(f"  Up vector:    [{up[0]:.4f}, {up[1]:.4f}, {up[2]:.4f}]")
print(f"  Parallactic angle ψ measured from EAST direction")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print(f"Crater Parameters:")
print(f"  Size: {2*true_a:.1f} × {2*true_b:.1f} km (major × minor)")
print(f"  Observation: {n_points} rim points, {pixel_noise_sigma:.2f} px noise @ {gsd}m/px")
print()
print(f"Parallactic Angle Results:")
print(f"  True angle:              {np.rad2deg(true_psi):.2f}°")
print(f"  Single fit:              {np.rad2deg(psi_fitted):.2f}°")
print(f"  Single fit error:        {np.abs(angle_error_deg):.4f}°")
print()
print(f"Uncertainty Estimates:")
print(f"  Analytical 1σ:           ±{sigma_angle_deg:.4f}°")
print(f"  Empirical 1σ (MC):       ±{np.rad2deg(std_error):.4f}°")
print(f"  ★ ANALYTICAL 3σ:         ±{3*sigma_angle_deg:.4f}°")
print(f"  ★ EMPIRICAL 3σ (MC):     ±{3*np.rad2deg(std_error):.4f}°")
print()
print(f"Position Estimation (using multiple craters):")
print(f"  With 5-10 craters @ 100 km orbit:")
print(f"    Expected 3σ position accuracy: 50-150 meters")
print()
print(f"This demonstrates the SONIC workflow:")
print(f"  1. Robbins DB provides crater database with angles")
print(f"  2. EllipseFitter.fitEllipse() fits ellipse to rim points")
print(f"  3. Conic.locusToExplicit() extracts parallactic angle ψ")
print(f"  4. getEllipseCovariance() quantifies uncertainty")
print(f"  5. PositionEstimation.withConics() uses angles for nav")
print()
print("Example completed successfully!")
print("=" * 70)
