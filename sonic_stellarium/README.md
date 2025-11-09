# SONIC-Stellarium Bridge

**Proof-of-Concept: Embedded Stellarium with Direct Framebuffer Access**

This directory contains the C++ bridge library that integrates Stellarium directly into SONIC for seamless, real-time lunar rendering without file I/O.

## Status

⚠️ **PROOF-OF-CONCEPT** - Architecture and API design complete, full implementation pending.

The code in this directory demonstrates:
- How Stellarium would be embedded
- API interface design
- Python bindings structure
- Performance expectations

## What This Enables

### Before (Current Method)
```
Stellarium (separate process)
    ↓ HTTP API
Screenshot saved to disk
    ↓ File I/O (~2000 ms)
Python reads file
    ↓ OpenCV processing
SONIC crater detection
```
**Performance:** 0.5-1 FPS, ~2 seconds latency

### After (Unified Integration)
```
Embedded Stellarium
    ↓ Direct memory access (<1 ms)
NumPy array (zero-copy)
    ↓ Immediate processing
SONIC crater detection
```
**Performance:** 30-60 FPS, ~20 ms latency

**Improvement: 100x faster!**

## Architecture

```
sonic_stellarium/
├── CMakeLists.txt              # Build configuration
├── include/
│   └── sonic_stel_bridge.h    # C++ API interface
├── src/
│   ├── sonic_stel_bridge.cpp  # Main implementation
│   ├── offscreen_renderer.cpp # Qt OpenGL helpers
│   └── python_bindings.cpp    # pybind11 Python wrapper
└── README.md                   # This file
```

## Build Instructions (When Implemented)

### Prerequisites
```bash
# Install Qt6
sudo apt-get install qt6-base-dev qt6-opengl-dev

# Install Python development headers
sudo apt-get install python3-dev

# Install pybind11
pip install pybind11
```

### Build
```bash
cd sonic_stellarium
cmake -B build -S .
cmake --build build -j8
```

### Install Python Module
```bash
pip install build/sonic_stellarium*.so
```

## Usage (Proposed API)

```python
import sonic_stellarium
import numpy as np

# Create embedded Stellarium renderer
renderer = sonic_stellarium.StellariumRenderer(2048, 2048)
renderer.initialize()

# Configure view
renderer.set_location(35.0, -106.0, 0.0, "Earth")
renderer.focus_object("Moon")
renderer.set_fov(1.0)  # 1 degree FOV

# Render to NumPy array (ZERO file I/O!)
frame = renderer.render_frame()  # (2048, 2048, 4) RGBA array

# Use with SONIC immediately
from sonic.navigation import detect_craters
craters = detect_craters(frame[:,:,:3])  # RGB channels
```

## Key Features

- **Direct Memory Access:** Framebuffer → NumPy array without file I/O
- **Zero-Copy:** Data stays in GPU memory until accessed
- **Real-Time:** 30-60 FPS rendering capability
- **Seamless Integration:** Single unified system
- **Qt Offscreen Rendering:** No GUI window required
- **Python Native:** NumPy arrays, familiar API

## Implementation Roadmap

See `../STELLARIUM_SONIC_INTEGRATION.md` for complete roadmap.

**Estimated effort:** 5-6 weeks

### Phase 1: Proof of Concept (1-2 weeks)
- [x] Design API interface
- [x] Create CMake structure
- [x] Write stub implementation
- [ ] Add Stellarium as git submodule
- [ ] Link against Stellarium libraries
- [ ] Verify offscreen rendering works

### Phase 2: Python Integration (1 week)
- [x] Design Python bindings
- [ ] Implement pybind11 wrapper
- [ ] Test NumPy zero-copy access
- [ ] Integration tests with SONIC

### Phase 3: Full Implementation (2 weeks)
- [ ] Implement all Stellarium controls
- [ ] Add crater database access
- [ ] Performance optimization
- [ ] Documentation

### Phase 4: Production Ready (1 week)
- [ ] Multi-platform support
- [ ] CI/CD pipeline
- [ ] pip-installable package
- [ ] Example applications

## Performance Benchmarks (Expected)

| Operation | Current | Unified | Improvement |
|-----------|---------|---------|-------------|
| Frame Acquisition | 1-2 sec | 16-33 ms | 100x faster |
| Memory Copies | 2-3 | 0-1 | 3x reduction |
| FPS Capability | 0.5-1 | 30-60 | 60x faster |
| CPU Usage | Medium | Low | 40% reduction |

## Dependencies

- **Qt6** - GUI framework and OpenGL
- **OpenGL** - GPU rendering
- **pybind11** - Python/C++ bindings
- **NumPy** - Python arrays
- **Stellarium** - Planetarium software (to be integrated)

## License

GPL v2 (same as Stellarium)

## References

- See `../STELLARIUM_SONIC_INTEGRATION.md` for full integration analysis
- See `../examples/unified_stellarium_sonic.py` for usage example
- Stellarium source: https://github.com/Stellarium/stellarium
- Qt Offscreen Rendering: https://doc.qt.io/qt-6/qoffscreensurface.html

## Contact

SONIC Navigation Team

---

**Note:** This is a proof-of-concept demonstrating architecture and performance potential. Full implementation requires linking against actual Stellarium libraries and completing the stub functions with real Stellarium API calls.
