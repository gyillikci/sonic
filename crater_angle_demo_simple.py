#!/usr/bin/env python3
"""
Crater Parallactic Angle Determination Demo (Pure Python)
Demonstrates the concept without external dependencies
"""

import math
import random

print("=" * 70)
print("PARALLACTIC ANGLE DETERMINATION FROM CRATER IDENTIFICATION")
print("Simplified Demo (Pure Python)")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Define True Crater Parameters
# ============================================================================
print("STEP 1: True Crater Parameters (from Robbins-like database)")
print("-" * 70)

# Simulating a crater from the Robbins database
true_xc = 0.0      # center x (km)
true_yc = 0.0      # center y (km)
true_a = 5.0       # semi-major axis (km)
true_b = 4.0       # semi-minor axis (km)
true_psi_deg = 35.0  # parallactic angle (degrees)
true_psi_rad = math.radians(true_psi_deg)

print(f"  Crater Database Entry:")
print(f"    Location: Lat=10.0°, Lon=-45.0° (example)")
print(f"    Major axis diameter: {2*true_a:.1f} km")
print(f"    Minor axis diameter: {2*true_b:.1f} km")
print(f"    Eccentricity: {math.sqrt(1 - (true_b/true_a)**2):.3f}")
print(f"    ★ DATABASE PARALLACTIC ANGLE: {true_psi_deg:.2f}°")
print(f"    Database angle std dev: ~0.5-2° (typical)")
print()

# ============================================================================
# STEP 2: Simulate Crater Observation
# ============================================================================
print("STEP 2: Spacecraft Observation Scenario")
print("-" * 70)

altitude_km = 100.0
gsd_m = 10.0  # Ground Sample Distance (meters/pixel)
pixel_noise_sigma = 0.5  # pixels (sub-pixel accuracy from edge detection)

print(f"  Orbital altitude: {altitude_km:.1f} km")
print(f"  Camera GSD: {gsd_m:.1f} m/pixel")
print(f"  Edge detection noise: {pixel_noise_sigma:.2f} pixels")
print(f"  Ground noise: {pixel_noise_sigma * gsd_m:.1f} meters")
print()

# ============================================================================
# STEP 3: Generate Crater Rim Points
# ============================================================================
print("STEP 3: Generating Simulated Crater Rim Points")
print("-" * 70)

n_points = 100
noise_km = (pixel_noise_sigma * gsd_m) / 1000.0

# Generate perfect ellipse points
rim_points_perfect = []
for i in range(n_points):
    theta = 2 * math.pi * i / n_points

    # Canonical ellipse
    x_canon = true_a * math.cos(theta)
    y_canon = true_b * math.sin(theta)

    # Rotate by parallactic angle
    x_rot = x_canon * math.cos(true_psi_rad) - y_canon * math.sin(true_psi_rad)
    y_rot = x_canon * math.sin(true_psi_rad) + y_canon * math.cos(true_psi_rad)

    # Translate to center
    x_final = x_rot + true_xc
    y_final = y_rot + true_yc

    rim_points_perfect.append((x_final, y_final))

# Add noise to simulate real observations
random.seed(42)
rim_points_noisy = []
for x_p, y_p in rim_points_perfect:
    noise_x = random.gauss(0, noise_km)
    noise_y = random.gauss(0, noise_km)
    rim_points_noisy.append((x_p + noise_x, y_p + noise_y))

print(f"  Generated {n_points} crater rim points")
print(f"  Added Gaussian noise: σ = {noise_km*1000:.2f} meters")
print(f"  Example noisy points:")
for i in range(3):
    print(f"    Point {i+1}: ({rim_points_noisy[i][0]:.4f}, {rim_points_noisy[i][1]:.4f}) km")
print()

# ============================================================================
# STEP 4: Simplified Ellipse Fitting
# ============================================================================
print("STEP 4: Ellipse Fitting (Simplified Least Squares)")
print("-" * 70)

# Center the data
x_coords = [p[0] for p in rim_points_noisy]
y_coords = [p[1] for p in rim_points_noisy]

x_mean = sum(x_coords) / len(x_coords)
y_mean = sum(y_coords) / len(y_coords)

x_centered = [x - x_mean for x in x_coords]
y_centered = [y - y_mean for y in y_coords]

print(f"  Data centering:")
print(f"    Mean x: {x_mean:.4f} km")
print(f"    Mean y: {y_mean:.4f} km")

# Simplified moment-based ellipse fitting
# Calculate second moments
Mxx = sum(x**2 for x in x_centered) / n_points
Myy = sum(y**2 for y in y_centered) / n_points
Mxy = sum(x*y for x, y in zip(x_centered, y_centered)) / n_points

print(f"  Second moments:")
print(f"    Mxx = {Mxx:.4f}")
print(f"    Myy = {Myy:.4f}")
print(f"    Mxy = {Mxy:.4f}")

# Estimate parallactic angle from moment matrix
# The angle is given by: atan2(2*Mxy, Mxx - Myy) / 2
psi_fitted_rad = 0.5 * math.atan2(2*Mxy, Mxx - Myy)
psi_fitted_deg = math.degrees(psi_fitted_rad)

# Ensure angle is positive
if psi_fitted_rad < 0:
    psi_fitted_rad += math.pi
    psi_fitted_deg = math.degrees(psi_fitted_rad)

# Estimate semi-axes
lambda_max = 0.5 * (Mxx + Myy + math.sqrt((Mxx - Myy)**2 + 4*Mxy**2))
lambda_min = 0.5 * (Mxx + Myy - math.sqrt((Mxx - Myy)**2 + 4*Mxy**2))

a_fitted = math.sqrt(lambda_max) if lambda_max > 0 else 0
b_fitted = math.sqrt(lambda_min) if lambda_min > 0 else 0

print(f"  Fitted parameters:")
print(f"    Center: ({x_mean:.4f}, {y_mean:.4f}) km")
print(f"    Semi-major axis: {a_fitted:.3f} km")
print(f"    Semi-minor axis: {b_fitted:.3f} km")
print(f"    ★ FITTED PARALLACTIC ANGLE: {psi_fitted_deg:.2f}°")
print()

# ============================================================================
# STEP 5: Error Analysis
# ============================================================================
print("STEP 5: Error Analysis")
print("-" * 70)

angle_error = psi_fitted_deg - true_psi_deg
center_error_x = x_mean - true_xc
center_error_y = y_mean - true_yc
a_error = a_fitted - true_a
b_error = b_fitted - true_b

print(f"  Comparison with ground truth:")
print(f"    True angle:   {true_psi_deg:.2f}°")
print(f"    Fitted angle: {psi_fitted_deg:.2f}°")
print(f"    ★ ANGLE ERROR: {angle_error:.4f}°")
print()
print(f"  Other parameter errors:")
print(f"    Center error: ({center_error_x*1000:.1f}, {center_error_y*1000:.1f}) m")
print(f"    Semi-major axis error: {a_error*1000:.1f} m")
print(f"    Semi-minor axis error: {b_error*1000:.1f} m")
print()

# ============================================================================
# STEP 6: Uncertainty Estimation
# ============================================================================
print("STEP 6: Uncertainty Estimation")
print("-" * 70)

# Analytical approximation for angle uncertainty
# σ_ψ ≈ σ_noise / (radius * sqrt(n_points))
crater_radius = true_a
sigma_angle_rad = noise_km / (crater_radius * math.sqrt(n_points))
sigma_angle_deg = math.degrees(sigma_angle_rad)

print(f"  Analytical formula:")
print(f"    σ_ψ ≈ σ_noise / (radius × √N)")
print(f"    σ_ψ ≈ {noise_km:.6f} / ({crater_radius:.1f} × {math.sqrt(n_points):.1f})")
print(f"    σ_ψ ≈ {sigma_angle_rad:.6f} rad")
print()
print(f"  Uncertainty estimates:")
print(f"    1-sigma: ±{sigma_angle_deg:.4f}°")
print(f"    2-sigma: ±{2*sigma_angle_deg:.4f}°")
print(f"    ★ 3-SIGMA: ±{3*sigma_angle_deg:.4f}°")
print()

# Check if error is within 3-sigma
within_3sigma = abs(angle_error) <= 3 * sigma_angle_deg
print(f"  Error check:")
print(f"    |Error| = {abs(angle_error):.4f}°")
print(f"    3σ bound = ±{3*sigma_angle_deg:.4f}°")
print(f"    Within 3σ? {within_3sigma}")
print()

# ============================================================================
# STEP 7: Real-World Context
# ============================================================================
print("STEP 7: Real-World Navigation Context")
print("-" * 70)

print(f"  Crater identification scenario:")
print(f"    - Spacecraft at {altitude_km} km orbit")
print(f"    - Detects and fits ellipses to {n_points} crater rim points")
print(f"    - Parallactic angle ψ encodes viewing geometry")
print()
print(f"  Local ENU coordinate frame:")
print(f"    - East-North-Up tangent plane at crater location")
print(f"    - ψ measured from EAST direction")
print(f"    - Transforms to Moon-Centered Moon-Fixed (MCMF)")
print()
print(f"  Position estimation (using 5-10 craters):")
print(f"    - Each crater contributes angle measurement")
print(f"    - Least-squares combines all measurements")
print(f"    - Expected 3σ position accuracy: 50-150 meters")
print()

# ============================================================================
# STEP 8: Scaling Analysis
# ============================================================================
print("STEP 8: Accuracy Scaling with Crater Size")
print("-" * 70)

print(f"  3σ angle uncertainty vs crater diameter:")
print()
print(f"  {'Diameter (km)':<15} {'Radius (km)':<15} {'3σ Angle (°)':<15}")
print(f"  {'-'*15} {'-'*15} {'-'*15}")

for diam in [1, 2, 5, 10, 20, 50]:
    radius = diam / 2.0
    sigma_3 = 3 * math.degrees(noise_km / (radius * math.sqrt(n_points)))
    print(f"  {diam:<15.1f} {radius:<15.1f} {sigma_3:<15.4f}")

print()
print(f"  Note: Larger craters → Better angle accuracy")
print(f"        More rim points → Better angle accuracy")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY - PARALLACTIC ANGLE DETERMINATION")
print("=" * 70)
print()
print(f"Crater Parameters:")
print(f"  Size: {2*true_a:.1f} × {2*true_b:.1f} km")
print(f"  True parallactic angle: {true_psi_deg:.2f}°")
print()
print(f"Observation Conditions:")
print(f"  Altitude: {altitude_km} km")
print(f"  GSD: {gsd_m} m/pixel")
print(f"  Rim points: {n_points}")
print(f"  Pixel noise: {pixel_noise_sigma:.2f} pixels")
print()
print(f"Results:")
print(f"  Fitted angle: {psi_fitted_deg:.2f}°")
print(f"  Error: {angle_error:.4f}°")
print(f"  ★ 3σ UNCERTAINTY: ±{3*sigma_angle_deg:.4f}°")
print()
print(f"This corresponds to SONIC workflow:")
print(f"  1. sonic.Robbins() - Load crater database")
print(f"  2. sonic.EllipseFitter.fitEllipse() - Fit rim points")
print(f"  3. conic.explicit(5) - Extract parallactic angle ψ")
print(f"  4. getEllipseCovariance() - Compute uncertainty")
print(f"  5. PositionEstimation.withConics() - Navigation")
print()
print(f"For actual spacecraft navigation with {altitude_km} km orbit:")
print(f"  Using 5-10 craters like this one:")
print(f"  Expected 3σ position accuracy: 50-150 meters")
print()
print("=" * 70)
print("Example completed successfully!")
print("=" * 70)
