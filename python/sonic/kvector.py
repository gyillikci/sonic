"""Kvector — k-vector range-search index over catalog inter-star angles
(port of +sonic/Kvector.m).

Stores, for every catalog star pair within [min_angle, max_angle], the cosine of
the inter-star angle plus the two catalog indices (I<J), sorted by cosine. A
linear "k" fit over the sorted values turns an angular range query into an O(1)
bracket + a slice — the mechanism behind fast lost-in-space identification.

References: Mortari et al., "The Pyramid Star Identification Technique" (2004);
Christian & Arulraj, "Review of the k-Vector..." (JGCD 2022).
"""

import numpy as np

from .tolerances import Tolerances


class Kvector:
    def __init__(self, cat, min_angle, max_angle, max_mag=np.inf,
                 bin_width_cos_angle=0.0, et=0.0, r_obs_AU=(0.0, 0.0, 0.0)):
        if cat.filter_map is not None:
            raise ValueError("A full, unfiltered StarCatalog must be provided")
        if np.isfinite(max_mag):
            cat = cat.filter(cat.vmag < max_mag)

        self.et = et
        self.r_obs_AU = np.asarray(r_obs_AU, float)
        u = cat.eval(et, r_obs_AU).u
        fmap = cat.filter_map if cat.filter_map is not None else np.arange(u.shape[1])

        cos_min, cos_max = np.cos(max_angle), np.cos(min_angle)
        cos_list, Is, Js = [], [], []
        for i in range(u.shape[1] - 1):
            cij = u[:, i] @ u[:, i + 1:]
            locs = np.nonzero((cij >= cos_min) & (cij <= cos_max))[0]
            if locs.size:
                cos_list.append(cij[locs])
                Is.append(np.full(locs.size, fmap[i]))
                Js.append(fmap[i + 1 + locs])
        if cos_list:
            cos_ang = np.concatenate(cos_list)
            self.Is = np.concatenate(Is).astype(np.int64)
            self.Js = np.concatenate(Js).astype(np.int64)
        else:
            cos_ang = np.empty(0)
            self.Is = np.empty(0, np.int64)
            self.Js = np.empty(0, np.int64)

        order = np.argsort(cos_ang, kind="stable")
        self.cos_interstar_angle = cos_ang[order]
        self.Is = self.Is[order]
        self.Js = self.Js[order]
        self.n = self.cos_interstar_angle.size
        if self.n == 0:
            return

        self.ymin = self.cos_interstar_angle[0]
        self.ymax = self.cos_interstar_angle[-1]
        span = self.ymax - self.ymin
        if bin_width_cos_angle > 0:
            self.n_bins = min(int(np.ceil(span / bin_width_cos_angle)), self.n)
        else:
            self.n_bins = self.n
        self.bin_width = span / self.n_bins

        xsi = Tolerances.SlopeAdjust * max(abs(self.ymin), abs(self.ymax))
        self.m = (span + 2 * xsi) / self.n_bins
        self.q = self.ymin - self.m - xsi

        edges = np.linspace(self.ymin, self.ymax, self.n_bins + 1)
        N, _ = np.histogram(self.cos_interstar_angle, edges)
        self.k = np.concatenate(([0], np.cumsum(N)))

    def query(self, min_angle, max_angle):
        """Return (min_idx, max_idx) bracketing pairs with angle in [min,max].

        Indices are into the sorted Is/Js arrays; slice ``[min_idx:max_idx]``.
        Returns (None, None) if the range lies outside the table.
        """
        if min_angle > max_angle:
            raise ValueError("min_angle must be <= max_angle")
        if self.n == 0:
            return None, None
        cmin, cmax = np.cos(min_angle), np.cos(max_angle)
        if cmin < self.cos_interstar_angle[0] or cmax > self.cos_interstar_angle[-1]:
            return None, None
        j_bottom = max(int(np.floor((cmax - self.q) / self.m)), 1)
        min_idx = self.k[min(j_bottom, len(self.k) - 1)]
        if min_idx == 0:
            min_idx = 1
        j_top = min(int(np.ceil((cmin - self.q) / self.m)), len(self.k) - 1)
        max_idx = self.k[j_top]
        # k-vector brackets are approximate; expand by an exact search to be safe.
        lo = int(np.searchsorted(self.cos_interstar_angle, cmax, "left"))
        hi = int(np.searchsorted(self.cos_interstar_angle, cmin, "right"))
        return min(min_idx - 1, lo), max(max_idx, hi)
