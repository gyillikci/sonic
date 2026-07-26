"""Camera — framing-camera model (port of +sonic/Camera.m).

Canonical camera frame: +z boresight, +x right, +y down. Pixel (u,v) origin at
the top-left. Construct from FOV+resolution (`from_fov`) or intrinsics (`from_K`).
"""

import numpy as np

from .aberration import Aberration
from .distortion import DistortionModel, Pinhole
from .points import Points2, Points3, PointsS2
from .project import Project


class Camera:
    def __init__(self, d_x, d_y, alpha, u_p, v_p, dist_model=None):
        self.d_x = d_x
        self.d_y = d_y
        self.alpha = alpha
        self.u_p = u_p
        self.v_p = v_p
        self.dist_model = dist_model if dist_model is not None else Pinhole()

    # ── constructors ────────────────────────────────────────────────────────
    @classmethod
    def from_fov(cls, fov, fov_type, direction, res, dist_model=None):
        """fov (rad), fov_type 'fov'|'ifov', direction 'h'|'v', res [rows, cols].

        Assumes square pixels, no shear (mirrors Camera.constructFromFOV).
        """
        rows, cols = res
        major = cols if direction.lower() == "h" else rows
        if fov_type.lower() == "fov":
            d_x = major / (2 * np.tan(fov / 2))
        elif fov_type.lower() == "ifov":
            d_x = 1.0 / fov
        else:
            raise ValueError("fov_type must be 'fov' or 'ifov'")
        return cls(d_x, d_x, 0.0, cols / 2.0, rows / 2.0, dist_model)

    @classmethod
    def from_K(cls, d_x, d_y, alpha, u_p, v_p, dist_model=None):
        return cls(d_x, d_y, alpha, u_p, v_p, dist_model)

    # ── intrinsics ──────────────────────────────────────────────────────────
    @property
    def K(self):
        return np.array([[self.d_x, self.alpha, self.u_p],
                         [0.0, self.d_y, self.v_p],
                         [0.0, 0.0, 1.0]])

    @property
    def Kinv(self):
        dxdy = self.d_x * self.d_y
        return np.array([
            [1 / self.d_x, -self.alpha / dxdy,
             (self.alpha * self.v_p - self.d_y * self.u_p) / dxdy],
            [0.0, 1 / self.d_y, -self.v_p / self.d_y],
            [0.0, 0.0, 1.0]])

    @property
    def hfov_rad(self):
        return 2 * np.arctan(self.u_p / self.d_x)

    @property
    def vfov_rad(self):
        return 2 * np.arctan(self.v_p / self.d_y)

    @property
    def diag_fov_rad(self):
        return 2 * np.arctan(np.hypot(self.u_p, self.v_p) / self.d_x)

    @property
    def ifov_h_rad(self):
        return 1.0 / self.d_x

    @property
    def ifov_v_rad(self):
        return 1.0 / self.d_y

    # ── forward projection (world -> pixels) ────────────────────────────────
    def synth_image(self, to_proj, attitude, velocity=None, crop_fov=None,
                    project_behind_camera=False):
        """Project 3D geometry into pixel coordinates (port of Camera.synthImage).

        Returns (Points2 pixel coords, proj_map bool over the input points).
        """
        n_in = to_proj.n
        rotated = attitude.rotate(to_proj)
        proj_raw, did_proj = Project.pinhole(rotated, project_behind_camera)

        if crop_fov is None:
            hf, vf = self.hfov_rad, self.vfov_rad
        elif len(crop_fov) == 2:
            hf, vf = crop_fov
        else:
            hf = vf = None
        if hf is not None:
            proj_crop, did_crop = Project.crop(proj_raw, hf, vf)
        else:
            proj_crop, did_crop = proj_raw, np.ones(proj_raw.n, dtype=bool)

        if velocity is not None:
            proj_crop = Aberration.aberrate(proj_crop, velocity)

        proj_dist = self.dist_model.distort(proj_crop)
        proj_px = Points2(self.K @ proj_dist.p2)

        proj_map = did_proj.copy()
        proj_map[did_proj] = did_crop
        return proj_px, proj_map

    # ── inverse (pixels -> line of sight), needed for plate solving ─────────
    def pixels_to_los(self, pix):
        """2xn pixel coords -> 3xn unit line-of-sight vectors (camera frame)."""
        pix = np.asarray(pix, float)
        if pix.ndim == 1:
            pix = pix[:, None]
        homog = np.vstack((pix, np.ones((1, pix.shape[1]))))
        norm = self.Kinv @ homog                      # distorted normalized coords
        undist, _ = self.dist_model.undistort(Points2(norm[:2]))
        rays = np.vstack((undist.r2, np.ones((1, undist.n))))
        return rays / np.linalg.norm(rays, axis=0)
