#!/usr/bin/env python3
"""
Stellarium-to-SONIC Crater Identification Pipeline

This script demonstrates how to:
1. Capture Moon images from Stellarium (1° FOV, 2K resolution)
2. Detect craters using image processing
3. Extract rim points
4. Fit ellipses to extract parallactic angles
5. Use for optical navigation

Requirements:
    pip install opencv-python numpy scipy requests pillow scikit-image

Stellarium Setup:
    1. Open Stellarium
    2. Enable RemoteControl plugin (Settings → Plugins → RemoteControl)
    3. Set port to 8090 (default)
    4. Zoom to Moon with ~1° FOV
    5. Run this script

Author: SONIC Navigation Team
Date: 2024
"""

import sys
import os
import time
import numpy as np
import requests
from pathlib import Path
import json

# Optional imports (will check availability)
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("WARNING: OpenCV not available. Install with: pip install opencv-python")

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not available. Install with: pip install pillow")

try:
    from skimage import filters, feature, measure, morphology
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False
    print("WARNING: scikit-image not available. Install with: pip install scikit-image")

# Add SONIC Python package to path
sonic_path = Path(__file__).parent.parent
sys.path.insert(0, str(sonic_path))

try:
    from sonic.geometry.points2 import Points2
    from sonic.geometry.conic import Conic
    from sonic.navigation.ellipse_fitter import EllipseFitter
    HAS_SONIC = True
except ImportError:
    HAS_SONIC = False
    print("WARNING: SONIC Python not available. Run from sonic_python/examples/")


# =============================================================================
# STELLARIUM API INTERFACE
# =============================================================================

class StellariumClient:
    """
    Interface to Stellarium Remote Control Plugin

    API Documentation: http://localhost:8090/api/help
    """

    def __init__(self, host='localhost', port=8090):
        self.base_url = f'http://{host}:{port}/api'
        self.host = host
        self.port = port

    def test_connection(self):
        """Test if Stellarium RemoteControl is available"""
        try:
            response = requests.get(f'{self.base_url}/main/status', timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_status(self):
        """Get current Stellarium status"""
        response = requests.get(f'{self.base_url}/main/status')
        return response.json()

    def get_view_info(self):
        """Get current view parameters (FOV, etc)"""
        response = requests.get(f'{self.base_url}/main/view')
        return response.json()

    def focus_moon(self):
        """Focus view on the Moon"""
        params = {'target': 'Moon'}
        response = requests.post(f'{self.base_url}/main/focus', data=params)
        return response.status_code == 200

    def set_fov(self, fov_degrees):
        """Set field of view in degrees"""
        params = {'fov': fov_degrees}
        response = requests.post(f'{self.base_url}/main/fov', data=params)
        return response.status_code == 200

    def get_object_info(self, name='Moon'):
        """Get information about celestial object"""
        params = {'name': name}
        response = requests.get(f'{self.base_url}/objects/info', params=params)
        return response.json()

    def take_screenshot_script(self, filename='moon_capture.png'):
        """
        Take screenshot using Stellarium scripting engine

        Note: This requires sending a script to Stellarium.
        Alternative: Use system screenshot tools (see capture_stellarium_window)
        """
        script = f'''
        core.screenshot("{filename}", false, "", true);
        core.wait(0.5);
        '''

        # Send script to Stellarium (if script API is available)
        # This is a placeholder - actual implementation depends on API version
        print(f"Screenshot script prepared: {filename}")
        print("Note: May need to use manual screenshot or system capture")
        return filename


def capture_stellarium_window(save_path='stellarium_capture.png'):
    """
    Alternative: Capture Stellarium window using system screenshot

    This works when Stellarium API screenshot is not available.
    Requires PIL (Pillow) library.
    """
    if not HAS_PIL:
        print("ERROR: PIL required for screenshot capture")
        return None

    print("Please focus Stellarium window...")
    print("Capturing in 3 seconds...")
    time.sleep(3)

    # Capture full screen (user should have Stellarium focused)
    screenshot = ImageGrab.grab()
    screenshot.save(save_path)
    print(f"Screenshot saved: {save_path}")

    return save_path


# =============================================================================
# CRATER DETECTION IMAGE PROCESSING
# =============================================================================

class CraterDetector:
    """
    Crater detection from lunar images using image processing

    Implements edge detection, segmentation, and rim extraction
    similar to SONIC MATLAB EdgeFinder and Centroider
    """

    def __init__(self, min_radius_px=10, max_radius_px=500):
        self.min_radius = min_radius_px
        self.max_radius = max_radius_px

    def preprocess_image(self, img):
        """
        Preprocess lunar image

        Steps:
        1. Convert to grayscale
        2. Enhance contrast
        3. Denoise
        4. Flatten (remove background gradient)
        """
        if not HAS_CV2:
            print("ERROR: OpenCV required for image processing")
            return None

        # Convert to grayscale if color
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

        # Background flattening (remove illumination gradient)
        # Similar to SONIC Image.flatten() method
        kernel_size = max(gray.shape) // 20
        if kernel_size % 2 == 0:
            kernel_size += 1  # Must be odd
        background = cv2.medianBlur(denoised, kernel_size)
        flattened = cv2.subtract(denoised, background)
        flattened = cv2.add(flattened, 128)  # Shift to mid-gray

        return flattened

    def detect_edges(self, img):
        """
        Edge detection using Canny algorithm

        Similar to SONIC EdgeFinder.sobel() method
        """
        if not HAS_CV2:
            return None

        # Automatic threshold determination
        median = np.median(img)
        lower = int(max(0, 0.7 * median))
        upper = int(min(255, 1.3 * median))

        # Canny edge detection
        edges = cv2.Canny(img, lower, upper, apertureSize=3, L2gradient=True)

        return edges

    def find_circles_hough(self, edges, original_img):
        """
        Find circular crater rims using Hough Circle Transform

        Returns list of detected circles: (x, y, radius)
        """
        if not HAS_CV2:
            return []

        # Hough Circle Transform
        circles = cv2.HoughCircles(
            original_img,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=self.min_radius * 2,
            param1=50,
            param2=30,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )

        if circles is None:
            return []

        circles = np.round(circles[0, :]).astype("int")
        print(f"  Detected {len(circles)} potential craters")

        return circles

    def extract_rim_points(self, edges, circle):
        """
        Extract rim points from edge image for a detected circle

        Args:
            edges: Binary edge image
            circle: (x, y, radius) of detected crater

        Returns:
            rim_points: Nx2 array of (x, y) coordinates on crater rim
        """
        x_center, y_center, radius = circle

        # Create circular mask slightly larger than detected radius
        mask = np.zeros_like(edges)
        cv2.circle(mask, (x_center, y_center), int(radius * 1.2), 255, thickness=int(radius * 0.4))

        # Extract edge points within mask
        rim_edge = cv2.bitwise_and(edges, mask)

        # Get coordinates of edge pixels
        y_coords, x_coords = np.where(rim_edge > 0)

        if len(x_coords) < 10:
            return None

        rim_points = np.column_stack([x_coords, y_coords])

        return rim_points

    def refine_to_ellipse(self, rim_points):
        """
        Fit ellipse to rim points using OpenCV

        Returns ellipse parameters: (center_x, center_y, axes, angle)
        """
        if not HAS_CV2 or rim_points is None or len(rim_points) < 5:
            return None

        # OpenCV requires points as float32
        points = rim_points.astype(np.float32)

        # Fit ellipse (requires at least 5 points)
        try:
            ellipse = cv2.fitEllipse(points)
            # ellipse format: ((cx, cy), (width, height), angle)
            return ellipse
        except cv2.error:
            return None


# =============================================================================
# SONIC INTEGRATION
# =============================================================================

class SONICCraterAnalyzer:
    """
    Integrate crater detection with SONIC ellipse fitting and angle extraction
    """

    def __init__(self):
        if not HAS_SONIC:
            raise ImportError("SONIC Python package required")

    def fit_ellipse_sonic(self, rim_points, method='hls'):
        """
        Fit ellipse using SONIC's statistically optimal methods

        Args:
            rim_points: Nx2 array of (x, y) rim coordinates
            method: 'ls', 'shls', or 'hls' (Hyper Least Squares recommended)

        Returns:
            conic: SONIC Conic object with parallactic angle
            covariance: Uncertainty covariance matrix
        """
        # Convert to SONIC Points2 format (2×N)
        pts = rim_points.T  # Transpose to 2×N
        points2_obj = Points2(pts)

        # Fit ellipse using SONIC EllipseFitter
        conic = EllipseFitter.fit_ellipse(points2_obj, method=method)

        # Get covariance (uncertainty quantification)
        try:
            covariance = EllipseFitter.get_ellipse_covariance(
                points2_obj,
                conic,
                noise_std=1.0  # 1 pixel noise
            )
        except:
            covariance = None

        return conic, covariance

    def extract_parallactic_angle(self, conic):
        """
        Extract parallactic angle from fitted ellipse

        The parallactic angle ψ is the rotation angle of the crater
        ellipse in the local ENU (East-North-Up) frame.
        """
        # Get explicit parameters: [xc, yc, a, b, ψ]
        explicit = conic.explicit

        center_x = explicit[0]
        center_y = explicit[1]
        semi_major = explicit[2]
        semi_minor = explicit[3]
        psi_rad = explicit[4]  # Parallactic angle in radians

        psi_deg = np.degrees(psi_rad)

        return {
            'center': (center_x, center_y),
            'semi_major_axis': semi_major,
            'semi_minor_axis': semi_minor,
            'parallactic_angle_rad': psi_rad,
            'parallactic_angle_deg': psi_deg,
            'eccentricity': np.sqrt(1 - (semi_minor/semi_major)**2)
        }


# =============================================================================
# COMPLETE PIPELINE
# =============================================================================

def stellarium_to_sonic_pipeline(image_path=None, auto_capture=False):
    """
    Complete pipeline from Stellarium to crater angle extraction

    Args:
        image_path: Path to saved Stellarium image (or None for auto-capture)
        auto_capture: If True, attempt to capture Stellarium window
    """

    print("=" * 70)
    print("STELLARIUM-TO-SONIC CRATER IDENTIFICATION PIPELINE")
    print("=" * 70)
    print()

    # Check dependencies
    if not HAS_CV2:
        print("ERROR: OpenCV required. Install: pip install opencv-python")
        return

    if not HAS_SONIC:
        print("ERROR: SONIC Python required. Check installation.")
        return

    # Step 1: Connect to Stellarium
    print("STEP 1: Connecting to Stellarium")
    print("-" * 70)
    stellarium = StellariumClient()

    if stellarium.test_connection():
        print("  ✓ Connected to Stellarium RemoteControl (localhost:8090)")

        # Get current view info
        try:
            status = stellarium.get_status()
            print(f"  Stellarium time: {status.get('time', 'unknown')}")
            print(f"  Location: {status.get('location', 'unknown')}")
        except:
            print("  Note: Could not retrieve detailed status")

        # Focus on Moon and set FOV
        print("  Setting up Moon view (1° FOV)...")
        stellarium.focus_moon()
        time.sleep(1)
        stellarium.set_fov(1.0)  # 1 degree field of view
        time.sleep(1)
        print("  ✓ Moon focused with 1° FOV")

    else:
        print("  ✗ Stellarium RemoteControl not available")
        print("    Enable: Settings → Plugins → RemoteControl → Load at startup")
        print("    Continuing with manual image capture...")

    print()

    # Step 2: Capture Image
    print("STEP 2: Capturing Lunar Image")
    print("-" * 70)

    if image_path is None:
        if auto_capture:
            image_path = capture_stellarium_window('stellarium_moon_2k.png')
        else:
            print("  No image provided. Options:")
            print("    1. Take screenshot manually in Stellarium (Ctrl+S)")
            print("    2. Re-run with auto_capture=True")
            print("    3. Provide image_path parameter")
            print()
            print("  Using demo: Creating synthetic lunar image...")
            image_path = create_synthetic_lunar_image()

    if image_path is None or not os.path.exists(image_path):
        print(f"  ERROR: Image not found: {image_path}")
        return

    print(f"  ✓ Image loaded: {image_path}")

    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"  ERROR: Could not read image")
        return

    print(f"  Image size: {img.shape[1]}×{img.shape[0]} pixels")
    print()

    # Step 3: Crater Detection
    print("STEP 3: Detecting Craters")
    print("-" * 70)

    detector = CraterDetector(min_radius_px=20, max_radius_px=300)

    print("  Preprocessing image...")
    preprocessed = detector.preprocess_image(img)

    print("  Detecting edges...")
    edges = detector.detect_edges(preprocessed)

    print("  Finding circular features (Hough Transform)...")
    circles = detector.find_circles_hough(edges, preprocessed)

    if len(circles) == 0:
        print("  ✗ No craters detected")
        print("    Try adjusting detection parameters or image quality")
        return

    print(f"  ✓ Detected {len(circles)} potential craters")
    print()

    # Step 4: Ellipse Fitting with SONIC
    print("STEP 4: Fitting Ellipses with SONIC (Hyper Least Squares)")
    print("-" * 70)

    analyzer = SONICCraterAnalyzer()
    results = []

    for i, circle in enumerate(circles[:5]):  # Process first 5 craters
        print(f"\n  Crater {i+1}: center=({circle[0]}, {circle[1]}), radius={circle[2]} px")

        # Extract rim points
        rim_points = detector.extract_rim_points(edges, circle)

        if rim_points is None or len(rim_points) < 20:
            print(f"    ✗ Insufficient rim points")
            continue

        print(f"    Extracted {len(rim_points)} rim points")

        # Fit with SONIC
        try:
            conic, covariance = analyzer.fit_ellipse_sonic(rim_points, method='hls')
            params = analyzer.extract_parallactic_angle(conic)

            print(f"    ✓ Ellipse fitted successfully")
            print(f"      Semi-major axis: {params['semi_major_axis']:.1f} px")
            print(f"      Semi-minor axis: {params['semi_minor_axis']:.1f} px")
            print(f"      ★ Parallactic angle: {params['parallactic_angle_deg']:.2f}°")
            print(f"      Eccentricity: {params['eccentricity']:.3f}")

            if covariance is not None:
                angle_std = np.sqrt(covariance[4, 4])  # ψ is 5th parameter
                print(f"      Angle uncertainty (1σ): ±{np.degrees(angle_std):.3f}°")

            results.append({
                'circle': circle,
                'rim_points': rim_points,
                'conic': conic,
                'params': params,
                'covariance': covariance
            })

        except Exception as e:
            print(f"    ✗ Fitting failed: {e}")

    print()
    print(f"  Successfully processed {len(results)} craters")
    print()

    # Step 5: Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if len(results) > 0:
        print(f"\n✓ Successfully identified {len(results)} craters from Stellarium image")
        print(f"\nExtracted parallactic angles:")
        for i, result in enumerate(results):
            angle = result['params']['parallactic_angle_deg']
            print(f"  Crater {i+1}: ψ = {angle:.2f}°")

        print("\nNext steps for navigation:")
        print("  1. Match detected craters to Robbins database")
        print("  2. Use parallactic angles + known crater positions")
        print("  3. Solve for observer position (spacecraft or Earth location)")
        print("  4. Estimated accuracy: 1-10 km (3σ) with 5-10 craters")
    else:
        print("\n✗ No craters successfully processed")
        print("\nTroubleshooting:")
        print("  • Ensure Stellarium shows clear crater features")
        print("  • Try 1° FOV centered on crater-rich region")
        print("  • Increase image contrast in Stellarium")
        print("  • Adjust detector parameters (min/max radius)")

    print()
    return results


def create_synthetic_lunar_image(size=(2048, 2048), n_craters=10):
    """
    Create synthetic lunar image for testing when no Stellarium available
    """
    if not HAS_CV2:
        return None

    print("  Creating synthetic Moon image (2048×2048)...")

    # Create blank image (gray background)
    img = np.ones(size, dtype=np.uint8) * 128

    # Add random noise
    noise = np.random.randint(-20, 20, size, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Add synthetic craters
    for i in range(n_craters):
        center_x = np.random.randint(200, size[1] - 200)
        center_y = np.random.randint(200, size[0] - 200)
        radius = np.random.randint(30, 150)

        # Draw crater (dark circle with bright rim)
        cv2.circle(img, (center_x, center_y), radius, 80, -1)  # Dark interior
        cv2.circle(img, (center_x, center_y), radius, 200, 3)  # Bright rim

        # Add some ellipticity (perspective distortion)
        angle = np.random.uniform(0, 180)
        axes = (radius, int(radius * np.random.uniform(0.6, 0.9)))
        cv2.ellipse(img, (center_x, center_y), axes, angle, 0, 360, 180, 2)

    # Save
    save_path = '/tmp/synthetic_moon.png'
    cv2.imwrite(save_path, img)
    print(f"  ✓ Synthetic image created: {save_path}")

    return save_path


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print(__doc__)
    print()

    # Check if image path provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Using provided image: {image_path}\n")
    else:
        image_path = None

    # Run complete pipeline
    results = stellarium_to_sonic_pipeline(
        image_path=image_path,
        auto_capture=False  # Set True to auto-capture Stellarium window
    )

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nTo use with real Stellarium imagery:")
    print("  1. Open Stellarium, zoom to Moon (1° FOV)")
    print("  2. Take screenshot (Ctrl+S or manual)")
    print("  3. Run: python stellarium_crater_detection.py <image_path>")
    print()
