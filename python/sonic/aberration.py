"""Aberration — relativistic stellar aberration (port of +sonic/Aberration.m)."""

import numpy as np

from .constants import Constants
from .points import Points2, PointsS2
from .tolerances import Tolerances


class Aberration:
    @staticmethod
    def aberrate(u_in, v_KMS):
        """Aberrate line-of-sight directions given observer velocity v (km/s).

        `u_in` is a PointsS2 or Points2; returns the same type.
        """
        if isinstance(u_in, PointsS2):
            u_obs = u_in.u
            wrap = PointsS2
        elif isinstance(u_in, Points2):
            u_obs = u_in.p2 / np.linalg.norm(u_in.p2, axis=0)
            wrap = Points2
        else:
            raise TypeError("aberrate expects PointsS2 or Points2")

        v = np.asarray(v_KMS, float).ravel()
        beta = v / Constants.c_KMS
        if np.linalg.norm(beta) <= Tolerances.SmallAngle:
            return u_in
        beta_hat = beta / np.linalg.norm(beta)
        gamma = 1.0 / np.sqrt(1 - (v @ v) / Constants.c_KMS ** 2)

        out = np.zeros_like(u_obs)
        for i in range(u_obs.shape[1]):
            ui = u_obs[:, i]
            coeff = 1.0 / (1 + beta @ ui)
            bcu = np.cross(beta_hat, ui)
            bcbcu = np.cross(beta_hat, bcu)
            out[:, i] = coeff * (ui + beta - (1 - gamma) / gamma * bcbcu)
        return wrap(out)
