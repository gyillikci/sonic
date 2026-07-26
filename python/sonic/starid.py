"""StarId — lost-in-space star identification (port of +sonic/StarId.m).

`interstar_angle` matches measured camera-frame line-of-sight vectors to a star
catalog using inter-star angles and the k-vector, returning the matches and the
recovered ICRF->camera Attitude (Wahba/SVD). Faithful to SONIC's triad search
and checkTriad; adds an optional `confirm_frac` gate (default 0 == exact SONIC)
that rejects false triads a bare `min_matches` floor would accept in dense fields.
"""

from collections import defaultdict

import numpy as np

from .attitude import Attitude
from .kvector import Kvector
from .points import PointsS2


class StarId:
    @staticmethod
    def interstar_angle(kvec: Kvector, cat, pointsS2_meas, tol, max_angle,
                        min_matches=5, confirm_frac=0.0, max_triad_seeds=15):
        """Identify measured directions against `cat` using `kvec`.

        Inputs mirror StarId.interstarAngle: a Kvector over the FULL catalog, the
        unfiltered StarCatalog, measured directions (PointsS2 or 3xn), an angular
        tolerance `tol` (rad), and `max_angle` (~camera FOV, rad).

        Returns (matches 2xK [meas_idx; catalog_idx], Attitude) or (None, None).
        """
        if min_matches < 4:
            raise ValueError("min_matches must be >= 4")
        if cat.filter_map is not None:
            raise ValueError("A full, unfiltered StarCatalog must be provided")

        meas_u = pointsS2_meas.u if isinstance(pointsS2_meas, PointsS2) \
            else np.asarray(pointsS2_meas, float)
        meas_u = meas_u / np.linalg.norm(meas_u, axis=0)
        n = meas_u.shape[1]
        if n < min_matches:
            return None, None

        cat_u = cat.eval(kvec.et, kvec.r_obs_AU).u
        min_confirm = max(min_matches, int(np.ceil(confirm_frac * n)))
        seeds = min(n, max_triad_seeds)

        for dj in range(1, seeds - 1):
            for dk in range(1, seeds - dj):
                for i in range(0, seeds - dj - dk):
                    j, k = i + dj, i + dj + dk
                    if k >= n:
                        continue
                    res = StarId._check_triad(kvec, cat_u, meas_u, (i, j, k),
                                              tol, max_angle, min_confirm)
                    if res is not None:
                        return res
        return None, None

    @staticmethod
    def _dir_pairs(kvec, ang, tol):
        """Directed catalog index pairs whose inter-star angle is within tol of `ang`."""
        lo, hi = kvec.query(max(ang - tol, 0.0), ang + tol)
        if lo is None:
            return np.empty(0, np.int64), np.empty(0, np.int64)
        I, J = kvec.Is[lo:hi], kvec.Js[lo:hi]
        return np.concatenate((I, J)), np.concatenate((J, I))

    @staticmethod
    def _check_triad(kvec, cat_u, meas_u, ijk, tol, max_angle, min_matches):
        i, j, k = ijk
        ang = lambda a, b: float(np.arccos(np.clip(meas_u[:, a] @ meas_u[:, b], -1, 1)))
        Iij, Jij = StarId._dir_pairs(kvec, ang(i, j), tol)
        Iik, Kik = StarId._dir_pairs(kvec, ang(i, k), tol)
        Ijk, Kjk = StarId._dir_pairs(kvec, ang(j, k), tol)
        if Iij.size == 0 or Iik.size == 0 or Ijk.size == 0:
            return None

        ik_by_I = defaultdict(list)
        for I2, K in zip(Iik, Kik):
            ik_by_I[I2].append(K)
        jk_set = set(zip(Ijk.tolist(), Kjk.tolist()))

        triangles = []
        for I, J in zip(Iij, Jij):
            for K in ik_by_I.get(I, ()):
                if (J, K) in jk_set:
                    triangles.append((I, J, K))
        if not triangles:
            return None

        u_cam = meas_u[:, [i, j, k]]
        center = u_cam.mean(axis=1)
        center /= np.linalg.norm(center)
        cos_max = np.cos(max_angle)
        cos_tol = np.cos(tol)

        for (I, J, K) in triangles:
            u_world = cat_u[:, [I, J, K]]
            T = Attitude.solveWahbasProblem(PointsS2(u_cam), PointsS2(u_world)).dcm

            center_world = T.T @ center
            near = (center_world @ cat_u) >= cos_max
            near_idx = np.nonzero(near)[0]
            if near_idx.size == 0:
                continue
            meas_world = T.T @ meas_u
            cosang = meas_world.T @ cat_u[:, near]
            mi, cj = np.nonzero(cosang >= cos_tol)
            if mi.size == 0:
                continue
            _, keep = np.unique(mi, return_index=True)
            mi, cj = mi[keep], cj[keep]
            _, keep2 = np.unique(cj, return_index=True)
            mi, cj = mi[keep2], cj[keep2]

            if mi.size >= min_matches:
                matches = np.vstack((mi, near_idx[cj]))
                att = Attitude.solveWahbasProblem(
                    PointsS2(meas_u[:, matches[0]]), PointsS2(cat_u[:, matches[1]]))
                return matches, att
        return None
