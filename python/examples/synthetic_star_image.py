"""Synthetic star image + lost-in-space solve — the Python analogue of SONIC's
SyntheticStarImgTutorial.mlx, followed by a StarId round-trip.

Builds a camera, an attitude, a (synthetic) star catalog, projects the stars into
a synthetic image, then recovers the attitude from the projected line-of-sight
vectors. Needs only numpy. Run: python3 python/examples/synthetic_star_image.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sonic  # noqa: E402


def main():
    rng = np.random.default_rng(2024)

    # 1. Camera — a wide framing camera (60° HFOV, 1920x1080), Brown-Conrady lens.
    lens = sonic.BrownConrady(p1=0.0, p2=0.0, k1=-0.02, k2=0.0, k3=0.0)
    cam = sonic.Camera.from_fov(np.radians(60), "fov", "h", (1080, 1920), lens)
    print(f"Camera: HFOV={np.degrees(cam.hfov_rad):.1f}°  "
          f"diag={np.degrees(cam.diag_fov_rad):.1f}°  "
          f"IFOV={np.degrees(cam.ifov_h_rad)*3600:.1f}\"/px")

    # 2. Star catalog — synthetic all-sky field (stand-in for Hipparcos; use
    #    sonic.Hipparcos.from_sonic_mat / from_vizier for the real catalog).
    n = 4000
    v = rng.standard_normal((3, n))
    v /= np.linalg.norm(v, axis=0)
    ra, dec, _ = sonic.SphereCoords.cartToRaDec(v)
    cat = sonic.StarCatalog(ra, dec, vmag=rng.uniform(1, 6, n))

    # 3. Attitude (ICRF -> camera) + imaging epoch/observer.
    att = sonic.Attitude(np.array([0.1, -0.2, 0.05]))          # a rotation vector
    stars_icrf = cat.eval(et=0.0, r_obs_AU=(1.0, 0.0, 0.0))    # 5-param model

    # 4. Project into a synthetic image (pinhole + crop + distort + intrinsics).
    px, mask = cam.synth_image(stars_icrf, att, velocity=[0.0, 29.78, 0.0])
    print(f"Projected {px.n} of {n} catalog stars onto the sensor.")

    # 5. Recover the attitude from the projected stars (lost-in-space StarId).
    los = cam.pixels_to_los(px.r2 + 0.3 * rng.standard_normal(px.r2.shape))
    kvec = sonic.Kvector(cat, np.radians(0.05), cam.diag_fov_rad)
    matches, att_est = sonic.StarId.interstar_angle(
        kvec, cat, sonic.PointsS2(los), tol=2 * cam.ifov_h_rad,
        max_angle=cam.diag_fov_rad, min_matches=5, confirm_frac=0.4)

    if matches is None:
        print("Identification FAILED")
        return 1
    err = np.degrees(sonic.Attitude.angleBetween(att_est, att)) * 3600
    b = att_est.dcm[2]                                          # boresight in ICRF
    ra_b, dec_b, _ = sonic.SphereCoords.cartToRaDec(b[:, None])
    print(f"Identified {matches.shape[1]} stars.")
    print(f"Recovered boresight: RA={np.degrees(ra_b[0])%360:.3f}°  "
          f"Dec={np.degrees(dec_b[0]):+.3f}°")
    print(f"Attitude error vs truth: {err:.1f}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
