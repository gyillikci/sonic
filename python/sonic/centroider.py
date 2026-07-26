"""Centroider — center-of-brightness star detection (port of +sonic/Centroider.m).

Needs opencv (cv2) or scipy for connected-components labeling; both are optional.
Returns a Points2 of centroids (and, optionally, the per-centroid pixel index lists).
"""

import numpy as np

from .image import Image
from .points import Points2

try:
    import cv2
    _HAVE_CV2 = True
except Exception:
    _HAVE_CV2 = False

try:
    from scipy import ndimage as _ndi
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False


def _label(bw):
    if _HAVE_CV2:
        num, labels = cv2.connectedComponents(bw.astype(np.uint8), connectivity=8)
        return labels, num - 1
    if _HAVE_SCIPY:
        labels, num = _ndi.label(bw, structure=np.ones((3, 3)))
        return labels, num
    raise RuntimeError("Centroider.COB needs opencv or scipy for labeling")


class Centroider:
    @staticmethod
    def COB(imgObj, thresh, min_star_size=9, max_star_size=50,
            nonmax_sup_dist=5.0, buffer=0):
        """Center-of-brightness centroiding (port of Centroider.COB).

        Returns (Points2 centroids [x;y], list of pixel-index arrays). Sorted by
        detection; brightest-wins within `nonmax_sup_dist`.
        """
        img = imgObj.DNmat if isinstance(imgObj, Image) else np.asarray(imgObj, float)
        n, m = img.shape
        bw = img > thresh
        labels, num = _label(bw)

        centers = np.full((2, num), np.nan)
        comps = [None] * num
        for i in range(1, num + 1):
            idx = np.nonzero(labels.ravel() == i)[0]
            if idx.size < min_star_size or idx.size > max_star_size:
                continue
            row, col = np.divmod(idx, m)
            if (row.min() < buffer or row.max() > n - buffer or
                    col.min() < buffer or col.max() > m - buffer):
                continue
            dn = img.ravel()[idx]
            s = dn.sum()
            xc = (col * dn).sum() / s
            yc = (row * dn).sum() / s

            dists = np.sqrt((xc - centers[0]) ** 2 + (yc - centers[1]) ** 2)
            close = dists < nonmax_sup_dist
            if np.any(close):
                cdn = img[int(round(yc)), int(round(xc))]
                cclose = img[np.round(centers[1, close]).astype(int),
                             np.round(centers[0, close]).astype(int)]
                if np.all(cclose >= cdn):
                    continue
                centers[:, close] = np.nan
            centers[:, i - 1] = [xc, yc]
            comps[i - 1] = idx

        keep = ~np.isnan(centers[0])
        centers = centers[:, keep]
        comps = [c for c, k in zip(comps, keep) if k]
        if centers.shape[1] == 0:
            return Points2(np.empty((2, 0))), []
        return Points2(centers), comps
