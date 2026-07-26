# SONIC — Python port

A Python port of the OPNAV / star-tracker core of the SONIC MATLAB toolkit. Class
names and semantics mirror the MATLAB `+sonic` package so workflows translate
directly; methods use `snake_case` with the MATLAB name noted in each docstring.

The goal of this port is the **image → RA/Dec plate-solving pipeline** and the
projective-geometry foundations it rests on — the part of SONIC that is directly
useful outside MATLAB (e.g. the `dwarf3tostellarium` telescope bridge). It is
**not** a line-for-line port of the entire toolkit; see *Status* below.

## Install / use

```bash
pip install numpy                     # only hard dependency
pip install scipy                     # optional: Centroider labeling, .mat catalogs
pip install opencv-python             # optional: faster Centroider labeling
pip install astroquery                # optional: real Hipparcos via Vizier

python3 python/tests/test_sonic.py            # 10/10, numpy only
python3 python/examples/synthetic_star_image.py
```

Or import it:

```python
import sys; sys.path.insert(0, "python")
import sonic
```

## The pipeline (mirrors the MATLAB tutorial)

```python
import numpy as np, sonic

# Camera: 60° HFOV, 1920x1080, Brown-Conrady lens
lens = sonic.BrownConrady(p1=0, p2=0, k1=-0.02, k2=0, k3=0)
cam  = sonic.Camera.from_fov(np.radians(60), "fov", "h", (1080, 1920), lens)

# Catalog -> ICRF unit vectors at the imaging epoch (5-parameter standard model)
cat   = sonic.Hipparcos.from_sonic_mat("hipparcos.mat")   # or .from_vizier()
stars = cat.eval(et=0.0, r_obs_AU=(1.0, 0.0, 0.0))

# Forward: project stars into a synthetic image
px, mask = cam.synth_image(stars, sonic.Attitude(np.array([0.1, -0.2, 0.05])))

# Inverse (plate solve): centroids -> line of sight -> identify -> attitude
los = cam.pixels_to_los(px.r2)
kvec = sonic.Kvector(cat, np.radians(0.05), cam.diag_fov_rad)
matches, att = sonic.StarId.interstar_angle(
    kvec, cat, sonic.PointsS2(los), tol=2*cam.ifov_h_rad,
    max_angle=cam.diag_fov_rad, min_matches=5, confirm_frac=0.4)

boresight_icrf = att.dcm[2]           # camera +z in ICRF -> RA/Dec
```

## Status — what is ported

| Area | Classes | Ported |
|---|---|---|
| Geometry | `Points2`, `Points3`, `PointsS2`, `SphereCoords` | ✅ |
| Attitude | `Attitude` (DCM/quat/rotvec, Wahba/SVD, SLERP) | ✅ |
| Camera | `Camera`, `DistortionModel`/`Pinhole`/`BrownConrady`, `Project`, `Aberration` | ✅ |
| Detection | `Image`, `Centroider` (center-of-brightness) | ✅ |
| Star ID | `StarCatalog`/`Hipparcos`, `Kvector`, `StarId` | ✅ |
| Support | `Units`, `Constants`, `Tolerances` | ✅ (OPNAV subset) |
| Horizon OPNAV | `Conic`, `Quadric`, `Ellipsoid`, `EllipseFitter`, `EdgeFinder`, `ScanLines`, `Robbins`, `Lines2/3`, `Planes3` | ❌ |
| Pose / position | `PnP`, `Pose`, `PositionEstimation`, `Lambert` | ❌ |
| Rendering / reflectance | `OrthoRender`, `OrthoSphere`, `Reflectance`, `Hapke`, … | ❌ |

### Faithfulness notes

- **Passive attitude convention**, matching SONIC. `comp` is defined so
  `comp.dcm == self.dcm @ other.dcm`; quaternion/rotation-vector conversions are
  mutually consistent (verified by the test suite). Rotation-vector *sign* may
  differ from a particular MATLAB code path — the rotation is identical and the
  pipeline never depends on the sign.
- **`Kvector`** ports the linear-fit bracket, then tightens it with an exact
  `searchsorted` so range queries are correct regardless of the fit margin.
- **`StarId.interstar_angle`** follows `StarId.interstarAngle`/`checkTriad`, and
  adds `confirm_frac` (default `0.0` = exact SONIC). Setting it (e.g. `0.4`)
  rejects false triads that a bare `min_matches` floor accepts in dense fields —
  see the commit history for the synthetic-test evidence.
- **Catalog data:** SONIC's `.mat` files ship separately, so `Hipparcos` offers
  `from_sonic_mat` (scipy.io), `from_vizier` (astroquery), and `StarCatalog`
  offers `from_degrees`/`from_csv`. The tests/examples build a synthetic catalog
  so nothing external is required to verify the port.

## Validation

`python3 python/tests/test_sonic.py` runs 10 parity/self-consistency checks
(unit round-trips, DCM↔quat↔rotvec, Wahba recovery to ~1e-15, Brown-Conrady
undistort inverts distort, `synth_image` ↔ `pixels_to_los` round-trip, and a full
lost-in-space `Kvector`+`StarId` solve). All pass with numpy alone.
