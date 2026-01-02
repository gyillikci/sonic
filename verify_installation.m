% verify_installation.m
% 
% This script verifies that SONIC is properly installed with all required
% data files. Run this script after downloading the data files to ensure
% everything is set up correctly.
%
% Usage:
%   Run this script from the SONIC root directory in MATLAB:
%   >> verify_installation

function verify_installation()
    fprintf('\n');
    fprintf('========================================\n');
    fprintf('SONIC Installation Verification\n');
    fprintf('========================================\n');
    fprintf('\n');
    
    % Test 1: Check if we're in the right directory
    fprintf('Test 1: Checking directory structure...\n');
    if exist('+sonic', 'dir') && exist('+examples', 'dir')
        fprintf('  ✓ SONIC directory structure found\n');
    else
        fprintf('  ✗ ERROR: Not in SONIC root directory\n');
        fprintf('    Please run this script from the SONIC root directory\n');
        return;
    end
    fprintf('\n');
    
    % Test 2: Check for data files
    fprintf('Test 2: Checking for required data files...\n');
    dataFiles = {'hipparcos.mat', 'usnognc.mat', 'robbins.mat', 'constellations.mat'};
    allFilesPresent = true;
    
    for i = 1:length(dataFiles)
        filePath = fullfile('+sonic', '+data', dataFiles{i});
        if exist(filePath, 'file')
            fprintf('  ✓ %s found\n', dataFiles{i});
        else
            fprintf('  ✗ %s NOT FOUND\n', dataFiles{i});
            allFilesPresent = false;
        end
    end
    fprintf('\n');
    
    if ~allFilesPresent
        fprintf('ERROR: Some data files are missing!\n');
        fprintf('\n');
        fprintf('Please download the data files by running:\n');
        fprintf('  python3 download_data.py\n');
        fprintf('OR\n');
        fprintf('  ./download_data.sh\n');
        fprintf('\n');
        fprintf('For more information, see DOWNLOAD_DATA.md\n');
        return;
    end
    
    % Test 3: Try to load each catalog
    fprintf('Test 3: Testing catalog loading...\n');
    
    try
        fprintf('  Loading Hipparcos catalog...\n');
        hip = sonic.Hipparcos();
        fprintf('    ✓ Hipparcos loaded: %d stars\n', hip.n);
    catch ME
        fprintf('    ✗ ERROR loading Hipparcos: %s\n', ME.message);
        return;
    end
    
    try
        fprintf('  Loading USNO GNC catalog...\n');
        gnc = sonic.USNOGNC();
        fprintf('    ✓ USNO GNC loaded: %d stars\n', gnc.n);
    catch ME
        fprintf('    ✗ ERROR loading USNO GNC: %s\n', ME.message);
        return;
    end
    
    try
        fprintf('  Loading Robbins crater catalog...\n');
        rbn = sonic.Robbins();
        fprintf('    ✓ Robbins loaded: %d craters\n', rbn.n);
    catch ME
        fprintf('    ✗ ERROR loading Robbins: %s\n', ME.message);
        return;
    end
    
    fprintf('\n');
    
    % Test 4: Check MATLAB toolboxes
    fprintf('Test 4: Checking required MATLAB toolboxes...\n');
    
    v = ver;
    hasImageProcessing = any(strcmp({v.Name}, 'Image Processing Toolbox'));
    hasComputerVision = any(strcmp({v.Name}, 'Computer Vision Toolbox'));
    
    if hasImageProcessing
        fprintf('  ✓ Image Processing Toolbox installed\n');
    else
        fprintf('  ⚠ WARNING: Image Processing Toolbox not detected\n');
        fprintf('    (Required: version 24.1 or later)\n');
    end
    
    if hasComputerVision
        fprintf('  ✓ Computer Vision Toolbox installed\n');
    else
        fprintf('  ⚠ WARNING: Computer Vision Toolbox not detected\n');
        fprintf('    (Required: version 24.1 or later)\n');
    end
    fprintf('\n');
    
    % Summary
    fprintf('========================================\n');
    if allFilesPresent && hasImageProcessing && hasComputerVision
        fprintf('✓ SONIC is properly installed!\n');
        fprintf('\n');
        fprintf('Next steps:\n');
        fprintf('  1. Add SONIC to your MATLAB path: addpath(pwd)\n');
        fprintf('  2. Explore the examples in +examples/\n');
        fprintf('  3. Visit the documentation: https://opnavlab.github.io/sonic/\n');
    else
        fprintf('⚠ Installation incomplete\n');
        fprintf('\n');
        fprintf('Please address the issues above before using SONIC.\n');
    end
    fprintf('========================================\n');
    fprintf('\n');
end
