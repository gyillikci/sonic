"""Project — projective camera operations (port of the pinhole/crop parts of
+sonic/Project.m). Points3 / PointsS2 -> image-plane Points2 by pinhole division.
"""

import numpy as np

from .points import Points2, Points3, PointsS2


class Project:
    @staticmethod
    def pinhole(to_proj, project_behind_camera=False):
        """Pinhole projection: divide by the z (boresight) coordinate.

        Returns (Points2 image-plane points, did_proj mask). Points with z<=0
        are dropped unless `project_behind_camera` is True.
        """
        if isinstance(to_proj, PointsS2):
            r3 = to_proj.u
        elif isinstance(to_proj, Points3):
            r3 = to_proj.r3
        else:
            r3 = np.asarray(to_proj, float)

        z = r3[2]
        if project_behind_camera:
            did = np.abs(z) > 0
        else:
            did = z > 0
        r3 = r3[:, did]
        proj = np.vstack((r3[0] / r3[2], r3[1] / r3[2]))
        return Points2(proj), did

    @staticmethod
    def crop(points2: Points2, hfov_rad, vfov_rad):
        """Keep image-plane points within the half-angle FOV bounds (ideal/pinhole).

        Returns (cropped Points2, did_crop mask).
        """
        r = points2.r2
        xb = np.tan(hfov_rad / 2)
        yb = np.tan(vfov_rad / 2)
        did = (np.abs(r[0]) <= xb) & (np.abs(r[1]) <= yb)
        return Points2(r[:, did]), did
