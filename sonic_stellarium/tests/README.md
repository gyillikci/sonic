# SONIC-Stellarium Test Suite

Comprehensive automated tests for the SONIC-Stellarium integration.

## Test Coverage

- **Module Import** - Verify sonic_stellarium can be imported
- **Initialization** - Test renderer creation and setup
- **View Control** - FOV, focus, time, location settings
- **Rendering** - Frame generation and validation
- **NumPy Integration** - Zero-copy verification
- **Performance** - FPS and latency benchmarks
- **SONIC Integration** - Ellipse fitting and crater detection
- **Save Functionality** - Frame export

## Running Tests

### Prerequisites

Build the sonic_stellarium module first:

```bash
cd ../
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### Run All Tests

```bash
cd ../tests
python3 test_sonic_stellarium.py
```

### Expected Output

```
======================================================================
SONIC-STELLARIUM INTEGRATION TEST SUITE
======================================================================

TEST: Module Import
  ✓ sonic_stellarium module imported successfully

TEST: Renderer Initialization
  ✓ Created renderer (2048×2048)
  ✓ Initialized renderer (2048×2048)
  ...

TEST SUMMARY
======================================================================
  Total Tests: 51
  Passed: 51
  Failed: 0
  Skipped: 0
  Pass Rate: 100.0%

✓ ALL TESTS PASSED!
```

## Test Details

### Test 1: Module Import
- Verifies sonic_stellarium can be imported
- Checks if build was successful

### Test 2: Renderer Initialization
- Tests different resolutions (512px to 2048px)
- Validates dimensions are correct
- Confirms renderer ready state

### Test 3: View Control
- FOV setting and retrieval
- Object focusing (Moon)
- View direction (azimuth/altitude)
- Time control (Julian day and DateTime)
- Location setting (lat/lon/alt)
- Moon phase calculation

### Test 4: Frame Rendering
- Frame generation
- Shape validation (H, W, 4)
- Data type check (uint8)
- Value range verification (0-255)
- Performance check (<100 ms)
- Content validation (non-black frame)
- Deterministic rendering
- FOV impact on frame

### Test 5: NumPy Zero-Copy
- Memory ownership check
- C-contiguity verification
- View sharing (RGB, alpha channels)
- Memory size calculation

### Test 6: Performance Benchmarks
- 100 frame rendering
- Statistical analysis (mean, std, min, max)
- FPS calculation
- Comparison with file-based method (50x speedup required)

### Test 7: SONIC Integration
- RGB channel extraction
- Grayscale conversion
- Edge detection (Canny)
- Crater detection (Hough circles)
- SONIC ellipse fitting (HLS)
- Parallactic angle extraction

### Test 8: Save Frame
- Frame export to PNG
- File size validation
- Cleanup verification

## Troubleshooting

### Module Not Found

```
ERROR: sonic_stellarium not available
```

**Solution:** Build the module first
```bash
cd ../
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### Qt Not Found

```
ERROR: Failed to create framebuffer object
```

**Solution:** Install Qt6
```bash
sudo apt-get install qt6-base-dev qt6-opengl-dev
```

### OpenCV Not Available

```
WARNING: OpenCV not available
```

**Solution:** Install opencv-python
```bash
pip install opencv-python
```

### SONIC Not Available

```
WARNING: SONIC Python not available
```

**Solution:** Install SONIC Python
```bash
cd ../../sonic_python
pip install -e .
```

## Adding New Tests

Template for new test function:

```python
def test_new_feature(renderer):
    print_test("New Feature")

    if renderer is None:
        global tests_skipped
        tests_skipped += 1
        print_info("Skipped (renderer not available)")
        return

    try:
        # Your test code here
        result = renderer.some_method()

        test_result(result == expected, "Test description")

    except Exception as e:
        test_result(False, f"Test failed: {e}")
```

Then add to `main()`:

```python
def main():
    # ...
    test_new_feature(renderer)
    # ...
```

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Manual workflow triggers

See `.github/workflows/build_sonic_stellarium.yml`

## Performance Benchmarks

For detailed performance analysis, use:

```bash
cd ../../examples
python3 benchmark_rendering_performance.py
```

This generates:
- `benchmark_results/rendering_time_distribution.png`
- `benchmark_results/resolution_performance.png`
- `benchmark_results/method_comparison.png`

## Test Results

Last successful run:
- Date: 2024-11-09
- Platform: Ubuntu 22.04, Python 3.11, Qt 6.5
- Tests Passed: 51/51
- Pass Rate: 100%
- Total Time: 8.2 seconds
