"""Attitude — rotation container + Wahba solver (port of +sonic/Attitude.m).

Passive convention (a coordinate transformation): for a DCM ``T`` and a vector
expressed in frame A, ``v_B = T @ v_A``. Quaternions are Hamilton, stored as a
vector part ``quat_v`` (3,) and scalar part ``quat_s``. The internal
quat<->DCM<->rotation-vector conversions are mutually consistent (verified by the
test suite); ``comp`` is defined so that ``comp.dcm == self.dcm @ other.dcm``,
matching SONIC.
"""

import numpy as np

from .tolerances import Tolerances


class Attitude:
    def __init__(self, raw_att, quat_flag=None):
        raw = np.asarray(raw_att, float)
        if raw.shape == (3, 3):
            self.verifyValidDCM(raw)
            self.dcm = raw
            self.quat_v, self.quat_s = self.DCMtoQuat(raw)
            self.rotation_vec = self.DCMtoRotationVec(raw)
        elif raw.size == 4:
            raw = raw.ravel()
            if quat_flag == "sv":          # scalar-first
                qv, qs = raw[1:4], raw[0]
            elif quat_flag == "vs":        # scalar-last
                qv, qs = raw[0:3], raw[3]
            else:
                raise ValueError("quaternion input needs quat_flag 'vs' or 'sv'")
            nrm = np.sqrt(qv @ qv + qs * qs)
            self.quat_v, self.quat_s = qv / nrm, qs / nrm
            self.dcm = self.quatToDCM(self.quat_v, self.quat_s)
            self.rotation_vec = self.quatToRotationVec(self.quat_v, self.quat_s)
        elif raw.size == 3:
            rv = raw.ravel()
            self.rotation_vec = rv
            self.quat_v, self.quat_s = self.rotationVecToQuat(rv)
            self.dcm = self.rotationVecToDCM(rv)
        else:
            raise ValueError("Attitude needs a 3x3 DCM, 4-vec quat, or 3-vec rotvec")

    # ── composition / inversion / action ────────────────────────────────────
    def comp(self, other: "Attitude") -> "Attitude":
        """Compose: result.dcm = self.dcm @ other.dcm (matches SONIC.comp)."""
        return Attitude(self.dcm @ other.dcm)

    def inv(self) -> "Attitude":
        return Attitude(self.dcm.T)

    def rotate(self, to_rot):
        """Rotate a PointsS2 or Points3 by this attitude (result matches input type)."""
        from .points import Points3, PointsS2
        if isinstance(to_rot, PointsS2):
            return PointsS2(self.dcm @ to_rot.u)
        if isinstance(to_rot, Points3):
            if to_rot.has_inf_points:
                rot = np.block([[self.dcm, np.zeros((3, 1))],
                                [np.zeros((1, 3)), 1.0]])
                return Points3(rot @ to_rot.p3)
            return Points3(self.dcm @ to_rot.r3)
        raise TypeError("Attitude.rotate supports PointsS2 or Points3")

    def __mul__(self, other):
        if isinstance(other, Attitude):
            return self.comp(other)
        return self.rotate(other)

    # ── Wahba / metrics ─────────────────────────────────────────────────────
    @staticmethod
    def solveWahbasProblem(pointsS2_cam, pointsS2_world) -> "Attitude":
        """world->camera attitude from matched directions (SONIC's SVD method).

        Inputs are PointsS2 (or 3xn arrays). Returns T with u_cam ≈ T @ u_world.
        """
        from .points import PointsS2
        uc = pointsS2_cam.u if isinstance(pointsS2_cam, PointsS2) else np.asarray(pointsS2_cam, float)
        uw = pointsS2_world.u if isinstance(pointsS2_world, PointsS2) else np.asarray(pointsS2_world, float)
        if uc.shape[1] < 2 or uc.shape != uw.shape:
            raise ValueError("need >=2 matching direction pairs of equal count")
        U, _, Vt = np.linalg.svd(uc @ uw.T)
        M = np.diag([1.0, 1.0, np.linalg.det(U) * np.linalg.det(Vt)])
        return Attitude(U @ M @ Vt)

    @staticmethod
    def angleBetween(att1: "Attitude", att2: "Attitude") -> float:
        R = att1.dcm @ att2.dcm.T
        return float(np.arccos(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)))

    @staticmethod
    def interpolate(att1: "Attitude", att2: "Attitude", t: float) -> "Attitude":
        """SLERP between two attitudes at fraction t in [0,1]."""
        qv1, qs1 = att1.quat_v, att1.quat_s
        qv2, qs2 = att2.quat_v, att2.quat_s
        q1 = np.append(qv1, qs1)
        q2 = np.append(qv2, qs2)
        if q1 @ q2 < 0:
            q2 = -q2
        dot = float(np.clip(q1 @ q2, -1.0, 1.0))
        if dot > 1 - 1e-10:
            q = q1 + t * (q2 - q1)
        else:
            th = np.arccos(dot)
            q = (np.sin((1 - t) * th) * q1 + np.sin(t * th) * q2) / np.sin(th)
        q /= np.linalg.norm(q)
        return Attitude(q, "vs")

    # ── conversions (mutually consistent, passive convention) ───────────────
    @staticmethod
    def quatToDCM(qv, qs):
        q1, q2, q3 = qv
        q4 = qs
        return np.array([
            [1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 + q3 * q4), 2 * (q1 * q3 - q2 * q4)],
            [2 * (q1 * q2 - q3 * q4), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 + q1 * q4)],
            [2 * (q1 * q3 + q2 * q4), 2 * (q2 * q3 - q1 * q4), 1 - 2 * (q1 * q1 + q2 * q2)]])

    @staticmethod
    def DCMtoQuat(T):
        """Shepperd's method (numerically stable)."""
        tr = np.trace(T)
        cand = np.array([tr, T[0, 0], T[1, 1], T[2, 2]])
        i = int(np.argmax(cand))
        if i == 0:
            r = np.sqrt(1 + tr)
            qs = 0.5 * r
            qv = np.array([T[1, 2] - T[2, 1], T[2, 0] - T[0, 2], T[0, 1] - T[1, 0]]) / (2 * r)
        elif i == 1:
            r = np.sqrt(1 + 2 * T[0, 0] - tr)
            qv = np.array([0.5 * r,
                           (T[0, 1] + T[1, 0]) / (2 * r),
                           (T[0, 2] + T[2, 0]) / (2 * r)])
            qs = (T[1, 2] - T[2, 1]) / (2 * r)
        elif i == 2:
            r = np.sqrt(1 + 2 * T[1, 1] - tr)
            qv = np.array([(T[0, 1] + T[1, 0]) / (2 * r),
                           0.5 * r,
                           (T[1, 2] + T[2, 1]) / (2 * r)])
            qs = (T[2, 0] - T[0, 2]) / (2 * r)
        else:
            r = np.sqrt(1 + 2 * T[2, 2] - tr)
            qv = np.array([(T[0, 2] + T[2, 0]) / (2 * r),
                           (T[1, 2] + T[2, 1]) / (2 * r),
                           0.5 * r])
            qs = (T[0, 1] - T[1, 0]) / (2 * r)
        if qs < 0:
            qv, qs = -qv, -qs
        n = np.sqrt(qv @ qv + qs * qs)
        return qv / n, qs / n

    @staticmethod
    def rotationVecToQuat(rv):
        ang = np.linalg.norm(rv)
        if ang < Tolerances.SmallAngle:
            return 0.5 * rv, np.sqrt(max(1 - ang * ang / 4, 0.0))
        ax = rv / ang
        return ax * np.sin(ang / 2), np.cos(ang / 2)

    @staticmethod
    def quatToRotationVec(qv, qs):
        qs = np.clip(qs, -1.0, 1.0)
        ang = 2 * np.arccos(qs)
        s = np.sqrt(max(1 - qs * qs, 0.0))
        if s < Tolerances.SmallAngle:
            return 2 * qv
        return (qv / s) * ang

    @staticmethod
    def rotationVecToDCM(rv):
        qv, qs = Attitude.rotationVecToQuat(rv)
        return Attitude.quatToDCM(qv, qs)

    @staticmethod
    def DCMtoRotationVec(T):
        qv, qs = Attitude.DCMtoQuat(T)
        return Attitude.quatToRotationVec(qv, qs)

    # ── validation ──────────────────────────────────────────────────────────
    @staticmethod
    def verifyValidDCM(T, tol=1e-6):
        if T.shape != (3, 3):
            raise ValueError("DCM must be 3x3")
        if np.max(np.abs(T @ T.T - np.eye(3))) > tol:
            raise ValueError("DCM is not orthogonal")
        if abs(np.linalg.det(T) - 1.0) > tol:
            raise ValueError("DCM determinant is not +1")
