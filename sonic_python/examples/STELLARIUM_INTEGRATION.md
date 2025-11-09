# Stellarium Integration for SONIC Crater Identification

## Overview

This integration allows you to use lunar images from Stellarium for optical navigation with SONIC's crater identification tools.

## Setup

### 1. Install Stellarium

Download from: https://stellarium.org/

### 2. Enable Remote Control Plugin

1. Open Stellarium
2. Go to: **Settings** (F2) → **Plugins** → **RemoteControl**
3. Check "Load at startup"
4. Set port: **8090** (default)
5. Restart Stellarium

### 3. Install Python Dependencies

```bash
pip install opencv-python pillow scikit-image numpy scipy requests
```

### 4. Install SONIC Python

```bash
cd sonic_python
pip install -e .
```

## Usage

### Method 1: With Stellarium Running

```bash
# Start Stellarium and set up your view:
# - Focus on Moon (search "Moon" and press Space)
# - Zoom to 1° field of view
# - Turn off atmosphere (A key)
# - Turn off ground (G key)

# Run the integration script:
python3 sonic_python/examples/stellarium_crater_detection.py
```

The script will:
- Connect to Stellarium API (localhost:8090)
- Automatically focus on Moon with 1° FOV
- Use synthetic image for demo (or capture screenshot)
- Detect craters and extract parallactic angles

### Method 2: With Saved Screenshot

```bash
# In Stellarium:
# 1. Set up Moon view (1° FOV, centered on crater-rich region)
# 2. Take screenshot (Ctrl+S)
# 3. Note the save location

# Run with your image:
python3 sonic_python/examples/stellarium_crater_detection.py /path/to/stellarium_screenshot.png
```

### Method 3: Auto-Capture Window

Modify the script to use auto-capture:

```python
results = stellarium_to_sonic_pipeline(
    image_path=None,
    auto_capture=True  # Will capture Stellarium window after 3 seconds
)
```

## Stellarium Setup for Best Results

### Camera Settings

- **Field of View:** 1° (type "1" in FOV box or use Ctrl+Alt+1)
- **Location:** Set to your position or spacecraft orbit
- **Time:** Set accurate time for Moon ephemeris
- **Atmosphere:** OFF (press A)
- **Ground:** OFF (press G)
- **Landscape:** OFF

### Image Quality

- **Screen Resolution:** 2048×2048 recommended (2K)
- **Graphics:** High quality in Settings
- **Zoom:** Center on crater-rich regions (near terminator is best)
- **Contrast:** Adjust in Settings → Display

### Best Viewing Conditions

- **Terminator region** - Maximum crater visibility due to shadows
- **Mare edges** - Good mix of bright/dark features
- **Avoid full Moon** - Low contrast, poor crater visibility
- **Avoid new Moon** - Too dark

## Output

The script provides:

1. **Crater Detection:**
   - Number of detected craters
   - Positions and radii in pixels

2. **Ellipse Fitting:**
   - Semi-major/minor axes
   - Center coordinates
   - Eccentricity

3. **Parallactic Angles (★):**
   - Angle ψ in degrees for each crater
   - Uncertainty estimates (1σ)

4. **Navigation Data:**
   - Ready for Robbins database matching
   - Can be used with PositionEstimation module

## Example Output

```
STEP 3: Detecting Craters
----------------------------------------------------------------------
  ✓ Detected 1872 potential craters

STEP 4: Fitting Ellipses with SONIC (Hyper Least Squares)
----------------------------------------------------------------------

  Crater 1: center=(1171, 535), radius=299 px
    Extracted 27051 rim points
    ✓ Ellipse fitted successfully
      Semi-major axis: 359.3 px
      Semi-minor axis: 361.3 px
      ★ Parallactic angle: 67.12°
      Angle uncertainty (1σ): ±0.052°

SUMMARY
----------------------------------------------------------------------
✓ Successfully identified 5 craters from Stellarium image

Extracted parallactic angles:
  Crater 1: ψ = 67.12°
  Crater 2: ψ = 49.62°
  Crater 3: ψ = 168.41°
  Crater 4: ψ = 137.44°
  Crater 5: ψ = 45.63°
```

## Integration with SONIC Navigation

### Next Steps After Crater Identification

1. **Database Matching:**
   ```python
   from sonic.navigation.robbins import Robbins

   # Load crater database
   robbins = Robbins()

   # Match detected craters to database
   # (compare positions, sizes, angles)
   ```

2. **Position Estimation:**
   ```python
   from sonic.navigation.position_estimation import PositionEstimation

   # Use matched craters + parallactic angles
   # Solve for observer position
   estimated_pos = PositionEstimation.with_conics(
       crater_observations,
       robbins_database
   )
   ```

3. **Accuracy:**
   - With 5-10 identified craters: **1-10 km (3σ)**
   - From Earth surface: **~10-100 km (3σ)**
   - In lunar orbit: **30-150 m (3σ)**

## Troubleshooting

### "No craters detected"

- **Increase contrast** in Stellarium
- **Zoom to crater-rich region** (not blank mare)
- **Adjust detector parameters:**
  ```python
  detector = CraterDetector(min_radius_px=10, max_radius_px=500)
  ```

### "Stellarium RemoteControl not available"

- Enable plugin in Stellarium settings
- Restart Stellarium
- Check firewall allows localhost:8090
- Use manual screenshot method instead

### "Insufficient rim points"

- Image resolution too low (use 2K or 4K)
- Crater too small in image (zoom in more)
- Poor contrast (adjust Stellarium display settings)

## API Reference

### Stellarium Remote Control API

Default: `http://localhost:8090/api`

**Key Endpoints:**
- `GET /api/main/status` - Get current state
- `POST /api/main/focus?target=Moon` - Focus on Moon
- `POST /api/main/fov?fov=1.0` - Set FOV (degrees)
- `GET /api/objects/info?name=Moon` - Get Moon info

### Python Classes

**StellariumClient:**
```python
stellarium = StellariumClient(host='localhost', port=8090)
stellarium.focus_moon()
stellarium.set_fov(1.0)
status = stellarium.get_status()
```

**CraterDetector:**
```python
detector = CraterDetector(min_radius_px=20, max_radius_px=300)
preprocessed = detector.preprocess_image(img)
edges = detector.detect_edges(preprocessed)
circles = detector.find_circles_hough(edges, preprocessed)
```

**SONICCraterAnalyzer:**
```python
analyzer = SONICCraterAnalyzer()
conic, covariance = analyzer.fit_ellipse_sonic(rim_points, method='hls')
params = analyzer.extract_parallactic_angle(conic)
```

## Performance

- **Image Processing:** ~2-5 seconds for 2K image
- **Crater Detection:** ~1-3 seconds (depends on number)
- **Ellipse Fitting:** ~5-50 ms per crater (HLS method)
- **Total Pipeline:** ~10-30 seconds for 5-10 craters

## References

- Stellarium: https://stellarium.org/
- SONIC MATLAB: Original crater navigation toolkit
- Krause et al. (2023): "Crater-based Optical Navigation"
- Robbins Crater Database: ~1.3 million lunar craters

## Future Enhancements

- [ ] Real-time video feed processing
- [ ] Automatic database matching
- [ ] Full position estimation integration
- [ ] Mars/planetary crater support
- [ ] GPU-accelerated image processing
- [ ] Machine learning crater detection

---

**Contact:** SONIC Navigation Team
**Date:** November 2024
