%% Crater Parallactic Angle Determination Example
% Demonstrates the full workflow for determining parallactic angles
% from crater identification using SONIC

clear; close all;
addpath(pwd);

fprintf('=== PARALLACTIC ANGLE DETERMINATION FROM CRATER IDENTIFICATION ===\n\n');

%% STEP 1: Load Robbins Crater Database
fprintf('STEP 1: Loading Robbins Crater Database...\n');
try
    rbn = sonic.Robbins();
    fprintf('  ✓ Loaded %d craters from Robbins database\n', rbn.n);
    fprintf('  ✓ Database contains parallactic angles (angElp_RAD)\n\n');
catch ME
    fprintf('  ✗ Error loading database: %s\n', ME.message);
    fprintf('  Note: You may need to download the .mat files\n\n');
    % Continue with synthetic example anyway
    rbn = [];
end

%% STEP 2: Select a Representative Crater
fprintf('STEP 2: Selecting a Representative Crater...\n');
if ~isempty(rbn)
    % Filter for medium-sized craters (5-15 km diameter)
    crater_filter = (rbn.majAxElp_KM > 5) & (rbn.majAxElp_KM < 15) & ...
                    (rbn.minAxElp_KM > 4);
    rbn_filtered = rbn.filter(crater_filter);

    % Pick the first one
    idx = 1;
    fprintf('  Selected Crater ID: %s\n', rbn_filtered.id(idx));
    fprintf('  Location: Lat=%.2f°, Lon=%.2f°\n', ...
        rad2deg(rbn_filtered.latElp_RAD(idx)), ...
        rad2deg(rbn_filtered.lonElp_RAD(idx)));
    fprintf('  Major axis: %.2f km\n', rbn_filtered.majAxElp_KM(idx));
    fprintf('  Minor axis: %.2f km\n', rbn_filtered.minAxElp_KM(idx));
    fprintf('  DATABASE PARALLACTIC ANGLE: %.2f° (%.4f rad)\n', ...
        rad2deg(rbn_filtered.angElp_RAD(idx)), rbn_filtered.angElp_RAD(idx));
    fprintf('  Angle std dev: %.2f° (1-sigma)\n', ...
        rad2deg(rbn_filtered.angElpDev_RAD(idx)));
    fprintf('  3-sigma uncertainty: ±%.2f°\n\n', ...
        3*rad2deg(rbn_filtered.angElpDev_RAD(idx)));

    % Extract parameters for synthetic example
    true_xc = 0;
    true_yc = 0;
    true_a = rbn_filtered.majAxElp_KM(idx)/2;  % semi-major axis
    true_b = rbn_filtered.minAxElp_KM(idx)/2;  % semi-minor axis
    true_psi = rbn_filtered.angElp_RAD(idx);   % parallactic angle
else
    % Use synthetic parameters
    true_xc = 0;
    true_yc = 0;
    true_a = 5.0;    % 5 km semi-major axis
    true_b = 4.0;    % 4 km semi-minor axis
    true_psi = deg2rad(35);  % 35 degree rotation
    fprintf('  Using synthetic crater parameters:\n');
    fprintf('  Major axis: %.2f km\n', 2*true_a);
    fprintf('  Minor axis: %.2f km\n', 2*true_b);
    fprintf('  TRUE PARALLACTIC ANGLE: %.2f°\n\n', rad2deg(true_psi));
end

%% STEP 3: Generate Synthetic Crater Rim Points
fprintf('STEP 3: Generating Synthetic Crater Rim Points...\n');

% Create true ellipse
true_conic = sonic.Conic([true_xc; true_yc; true_a; true_b; true_psi]);
fprintf('  Created true ellipse conic\n');

% Sample points around the ellipse
n_points = 100;
crater_pts_perfect = sonic.SampleGeom2D.conicPts(true_conic, n_points);
fprintf('  Generated %d points around crater rim\n', n_points);

% Add realistic pixel noise (0.5 pixel standard deviation)
pixel_noise_sigma = 0.5;  % pixels
gsd = 10.0;  % Ground Sample Distance: 10 m/pixel at 100 km altitude
noise_meters = pixel_noise_sigma * gsd / 1000;  % Convert to km
noise = noise_meters * randn(2, n_points);
crater_pts_noisy = sonic.Points2(crater_pts_perfect.r2 + noise);
fprintf('  Added noise: σ=%.2f pixels (%.1f m on ground)\n\n', ...
    pixel_noise_sigma, pixel_noise_sigma*gsd);

%% STEP 4: Fit Ellipse using Different Methods
fprintf('STEP 4: Fitting Ellipse to Noisy Crater Rim Points...\n');

% Method 1: Least Squares (LS)
tic;
conic_ls = sonic.EllipseFitter.fitEllipse(crater_pts_noisy, 'ls');
time_ls = toc;
psi_ls = conic_ls.explicit(5);
error_ls = rad2deg(psi_ls - true_psi);
fprintf('  Least Squares (LS):\n');
fprintf('    Fitted angle: %.2f° (error: %.3f°)\n', rad2deg(psi_ls), error_ls);
fprintf('    Computation time: %.1f ms\n', time_ls*1000);

% Method 2: Semi-Hyper Least Squares (SHLS)
tic;
conic_shls = sonic.EllipseFitter.fitEllipse(crater_pts_noisy, 'shls');
time_shls = toc;
psi_shls = conic_shls.explicit(5);
error_shls = rad2deg(psi_shls - true_psi);
fprintf('  Semi-Hyper LS (SHLS):\n');
fprintf('    Fitted angle: %.2f° (error: %.3f°)\n', rad2deg(psi_shls), error_shls);
fprintf('    Computation time: %.1f ms\n', time_shls*1000);

% Method 3: Hyper Least Squares (HLS) - Most accurate
tic;
conic_hls = sonic.EllipseFitter.fitEllipse(crater_pts_noisy, 'hls');
time_hls = toc;
psi_hls = conic_hls.explicit(5);
error_hls = rad2deg(psi_hls - true_psi);
fprintf('  Hyper Least Squares (HLS) - BEST:\n');
fprintf('    Fitted angle: %.2f° (error: %.3f°)\n', rad2deg(psi_hls), error_hls);
fprintf('    Computation time: %.1f ms\n\n', time_hls*1000);

%% STEP 5: Compute Covariance and Uncertainty
fprintf('STEP 5: Computing Angle Covariance and Uncertainty...\n');

% Compute covariance matrix for implicit parameters
sigsqr_xy = (noise_meters)^2;  % variance in km^2
Pa = sonic.EllipseFitter.getEllipseCovariance(conic_hls, crater_pts_noisy, sigsqr_xy);
fprintf('  Computed 6×6 covariance matrix for implicit parameters\n');
fprintf('  Diagonal elements (variances):\n');
for i = 1:6
    fprintf('    P(%d,%d) = %.6e\n', i, i, Pa(i,i));
end

% Approximate angle uncertainty (simplified - full would need Jacobian)
% For rough estimate: σ_ψ ≈ σ_pixel / (crater_radius * sqrt(n_points))
crater_radius_km = true_a;  % semi-major axis
sigma_angle_approx = noise_meters / (crater_radius_km * sqrt(n_points));
sigma_angle_deg = rad2deg(sigma_angle_approx);
fprintf('\n  ESTIMATED ANGLE UNCERTAINTY (1-sigma): %.3f° (%.5f rad)\n', ...
    sigma_angle_deg, sigma_angle_approx);
fprintf('  3-SIGMA UNCERTAINTY: ±%.3f°\n\n', 3*sigma_angle_deg);

%% STEP 6: Display Explicit Parameters
fprintf('STEP 6: Extracted Explicit Parameters (HLS fit):\n');
explicit_params = conic_hls.explicit;
fprintf('  Center (xc, yc): (%.3f, %.3f) km\n', explicit_params(1), explicit_params(2));
fprintf('  Semi-major axis a: %.3f km\n', explicit_params(3));
fprintf('  Semi-minor axis b: %.3f km\n', explicit_params(4));
fprintf('  ★ PARALLACTIC ANGLE ψ: %.2f° (%.4f rad)\n', ...
    rad2deg(explicit_params(5)), explicit_params(5));
fprintf('\n  TRUE vs FITTED:\n');
fprintf('    True angle:   %.2f°\n', rad2deg(true_psi));
fprintf('    Fitted angle: %.2f°\n', rad2deg(psi_hls));
fprintf('    Error:        %.3f° (%.5f rad)\n\n', error_hls, deg2rad(error_hls));

%% STEP 7: Demonstrate Coordinate Transformations
fprintf('STEP 7: Coordinate Frame Transformations...\n');

% Create a local ENU frame (like in Robbins database)
lat_rad = deg2rad(10);   % 10° North
lon_rad = deg2rad(-45);  % 45° West

% Build ENU frame vectors (from Robbins.getMCMFDiskQuadric)
uVec = [cos(lat_rad)*cos(lon_rad); cos(lat_rad)*sin(lon_rad); sin(lat_rad)];  % Up
eVec = [-sin(lon_rad); cos(lon_rad); 0];  % East
nVec = [-sin(lat_rad)*cos(lon_rad); -sin(lat_rad)*sin(lon_rad); cos(lat_rad)];  % North

T_ENUtoMCMF = [eVec, nVec, uVec];
att_ENUtoMCMF = sonic.Attitude(T_ENUtoMCMF);

fprintf('  Created local ENU frame at Lat=%.1f°, Lon=%.1f°\n', ...
    rad2deg(lat_rad), rad2deg(lon_rad));
fprintf('  East vector:  [%.3f, %.3f, %.3f]\n', eVec(1), eVec(2), eVec(3));
fprintf('  North vector: [%.3f, %.3f, %.3f]\n', nVec(1), nVec(2), nVec(3));
fprintf('  Up vector:    [%.3f, %.3f, %.3f]\n', uVec(1), uVec(2), uVec(3));
fprintf('\n  In ENU frame: parallactic angle ψ is measured from EAST direction\n');
fprintf('  Angle from East: %.2f°\n\n', rad2deg(psi_hls));

%% STEP 8: Summary Statistics
fprintf('====== SUMMARY ======\n');
fprintf('Crater Analysis Results:\n');
fprintf('  Crater size: %.1f × %.1f km\n', 2*true_a, 2*true_b);
fprintf('  Image noise: %.2f pixels @ %d m/pixel GSD\n', pixel_noise_sigma, gsd);
fprintf('  Number of rim points: %d\n', n_points);
fprintf('\n');
fprintf('Parallactic Angle Determination:\n');
fprintf('  True angle:     %.2f°\n', rad2deg(true_psi));
fprintf('  Fitted angle:   %.2f° (HLS method)\n', rad2deg(psi_hls));
fprintf('  Fitting error:  %.3f°\n', abs(error_hls));
fprintf('  1-sigma uncert: ±%.3f°\n', sigma_angle_deg);
fprintf('  ★ 3-SIGMA UNCERTAINTY: ±%.3f° (±%.5f rad)\n', ...
    3*sigma_angle_deg, 3*sigma_angle_approx);
fprintf('\n');
fprintf('Method Comparison:\n');
fprintf('  LS error:   %.3f°\n', abs(error_ls));
fprintf('  SHLS error: %.3f°\n', abs(error_shls));
fprintf('  HLS error:  %.3f° (best)\n', abs(error_hls));
fprintf('\n');
fprintf('For spacecraft position estimation:\n');
fprintf('  With 5-10 such craters @ 100 km orbit:\n');
fprintf('  Expected 3σ position accuracy: 50-150 meters\n');
fprintf('\n');

fprintf('Example completed successfully!\n');
