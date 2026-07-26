"""Parity + self-consistency tests for the SONIC Python port.

Run: python3 -m pytest python/tests/  (or `python3 python/tests/test_sonic.py`).
Only numpy is required; the star-ID test builds a synthetic catalog so no external
data is needed.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sonic  # noqa: E402


def _rand_dcm(rng):
    Q, R = np.linalg.qr(rng.standard_normal((3, 3)))
    Q = Q @ np.diag(np.sign(np.diag(R)))
    if np.linalg.det(Q) < 0:
        Q[:, 0] = -Q[:, 0]
    return Q


def test_units_roundtrip():
    assert np.isclose(sonic.Units.RADtoDEG(np.pi), 180.0)
    assert np.isclose(sonic.Units.DEGtoRAD(180.0), np.pi)
    assert np.isclose(sonic.Units.MAStoDEG(3600_000), 1.0)


def test_spherecoords_roundtrip():
    rng = np.random.default_rng(1)
    v = rng.standard_normal((3, 50))
    v /= np.linalg.norm(v, axis=0)
    ra, dec, r = sonic.SphereCoords.cartToRaDec(v)
    back = sonic.SphereCoords.raDecToCart(ra, dec)
    assert np.allclose(back, v, atol=1e-12)


def test_pointss2_radec():
    u = np.array([[1.0], [0.0], [0.0]])
    p = sonic.PointsS2(u)
    assert np.allclose(p.ra_dec[:, 0], [0.0, 0.0])


def test_attitude_dcm_quat_roundtrip():
    rng = np.random.default_rng(2)
    for _ in range(200):
        T = _rand_dcm(rng)
        att = sonic.Attitude(T)
        # DCM -> quat -> DCM is identity
        assert np.allclose(sonic.Attitude.quatToDCM(att.quat_v, att.quat_s), T, atol=1e-10)
        # rotation vector round trip
        assert np.allclose(sonic.Attitude.rotationVecToDCM(att.rotation_vec), T, atol=1e-9)


def test_attitude_comp_matches_dcm_product():
    rng = np.random.default_rng(3)
    A = sonic.Attitude(_rand_dcm(rng))
    B = sonic.Attitude(_rand_dcm(rng))
    assert np.allclose(A.comp(B).dcm, A.dcm @ B.dcm, atol=1e-12)
    assert np.allclose((A * B).dcm, A.dcm @ B.dcm, atol=1e-12)
    assert np.allclose(A.inv().dcm, A.dcm.T, atol=1e-12)


def test_wahba_recovers_attitude():
    rng = np.random.default_rng(4)
    T = _rand_dcm(rng)
    uw = rng.standard_normal((3, 20))
    uw /= np.linalg.norm(uw, axis=0)
    uc = T @ uw
    est = sonic.Attitude.solveWahbasProblem(sonic.PointsS2(uc), sonic.PointsS2(uw))
    # arccos amplifies near-zero angles; compare the DCMs directly (exact to ~1e-15).
    assert np.allclose(est.dcm, T, atol=1e-12)


def test_slerp_endpoints():
    rng = np.random.default_rng(5)
    A = sonic.Attitude(_rand_dcm(rng))
    B = sonic.Attitude(_rand_dcm(rng))
    assert sonic.Attitude.angleBetween(sonic.Attitude.interpolate(A, B, 0.0), A) < 1e-9
    assert sonic.Attitude.angleBetween(sonic.Attitude.interpolate(A, B, 1.0), B) < 1e-9


def test_brownconrady_undistort_inverts_distort():
    bc = sonic.BrownConrady(1e-3, -5e-4, -0.08, 0.02, 0.001)
    pts = sonic.Points2(np.array([[0.1, -0.2, 0.05], [0.0, 0.15, -0.1]]))
    d = bc.distort(pts)
    u, conv = bc.undistort(d)
    assert np.all(conv)
    assert np.allclose(u.r2, pts.r2, atol=1e-9)


def test_camera_synth_image_inverts_to_los():
    cam = sonic.Camera.from_fov(np.radians(20), "fov", "h", (1024, 1024))
    rng = np.random.default_rng(6)
    # points near boresight
    u = np.array([0.02, -0.03, 1.0])[:, None] + 0.01 * rng.standard_normal((3, 8))
    u = u / np.linalg.norm(u, axis=0)
    px, m = cam.synth_image(sonic.PointsS2(u), sonic.Attitude(np.eye(3)))
    los = cam.pixels_to_los(px.r2)
    assert np.allclose(los, u[:, m], atol=1e-6)


def test_starid_lost_in_space():
    """Full lost-in-space solve on a synthetic catalog (Kvector + StarId)."""
    rng = np.random.default_rng(7)
    n = 4000
    v = rng.standard_normal((3, n))
    v /= np.linalg.norm(v, axis=0)
    ra, dec, _ = sonic.SphereCoords.cartToRaDec(v)
    cat = sonic.StarCatalog(ra, dec, vmag=rng.uniform(1, 6, n))

    cam = sonic.Camera.from_fov(np.radians(60), "fov", "h", (1080, 1920))
    max_ang = cam.diag_fov_rad
    kvec = sonic.Kvector(cat, np.radians(0.05), max_ang, max_mag=np.inf)
    tol = 2 * cam.ifov_h_rad

    ok = 0
    trials = 12
    for _ in range(trials):
        T = _rand_dcm(rng)
        px, mask = cam.synth_image(cat.eval(), sonic.Attitude(T))
        if px.n < 6:
            continue
        los = cam.pixels_to_los(px.r2 + 0.3 * rng.standard_normal(px.r2.shape))
        matches, att = sonic.StarId.interstar_angle(
            kvec, cat, sonic.PointsS2(los), tol, max_ang,
            min_matches=5, confirm_frac=0.4)
        assert matches is not None, "identification failed"
        err = sonic.Attitude.angleBetween(att, sonic.Attitude(T))
        ok += err < np.radians(1 / 60)  # < 1 arcmin
    assert ok >= trials - 1, f"only {ok}/{trials} solves within 1'"


if __name__ == "__main__":
    fns = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for f in fns:
        try:
            f()
            print(f"PASS  {f.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {f.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
