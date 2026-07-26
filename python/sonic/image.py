"""Image — digital-number image wrapper + noise estimation (port of +sonic/Image.m,
the parts used by the star-tracker pipeline)."""

import numpy as np


class Image:
    def __init__(self, DNmat):
        self.DNmat = np.asarray(DNmat, float)
        if self.DNmat.ndim == 3:
            self.DNmat = self.DNmat.mean(axis=2)
        self.rows, self.cols = self.DNmat.shape

    def estNoiseRand(self, sig_multiple=5.0, rand_num=10000, rng=None):
        """Noise threshold from random pixel-pair differences (estNoiseRand)."""
        rng = rng or np.random.default_rng()
        flat = self.DNmat.ravel()
        p = flat.size
        a = flat[rng.integers(0, p, rand_num)]
        b = flat[rng.integers(0, p, rand_num)]
        sig_nf = np.std(a - b) / np.sqrt(2)
        return sig_nf * sig_multiple

    def estNoiseSort(self, sig_multiple=5.0, cutoff=0.5):
        """Noise threshold from the std of the dimmest `cutoff` fraction (estNoiseSort)."""
        s = np.sort(self.DNmat.ravel())
        noise = s[:max(1, round(s.size * cutoff))]
        return float(np.std(noise) * sig_multiple)
