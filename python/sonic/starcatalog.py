"""StarCatalog — catalog base + concrete catalogs (port of +sonic StarCatalog / Hipparcos).

`eval(et, r_obs_AU)` applies the 5-parameter standard model (proper motion +
parallax) to produce ICRF unit vectors (a PointsS2), exactly like SONIC. Proper
motion / parallax are optional per-star; when omitted the catalog degenerates to
fixed ICRF directions, which is fine for a single night's imaging.

Because SONIC's binary `.mat` catalog files are distributed separately, this port
provides several loaders: from plain arrays, from CSV, from the SONIC `.mat`
(via scipy.io), and from Vizier/Hipparcos (via astroquery, optional).
"""

import numpy as np

from .points import PointsS2
from .spherecoords import SphereCoords
from .units import Units

# Hipparcos catalog epoch J1991.25, expressed in SPICE TDB seconds past J2000.
HIP_EPOCH_TDB = -2.761289418143435e8


class StarCatalog:
    """Base catalog. Angles stored in radians; proper motion in rad/s; parallax in rad."""

    def __init__(self, ra_rad, dec_rad, vmag=None, ids=None, t_epoch=0.0,
                 pm_ra_rps=None, pm_dec_rps=None, plx_rad=None):
        self.ra_rad = np.asarray(ra_rad, float).ravel()
        self.dec_rad = np.asarray(dec_rad, float).ravel()
        self.n = self.ra_rad.size
        self.t_epoch = t_epoch
        z = np.zeros(self.n)
        self.vmag = np.asarray(vmag, float).ravel() if vmag is not None else np.full(self.n, np.nan)
        self.ids = np.asarray(ids) if ids is not None else np.arange(self.n)
        self.pm_ra_rps = np.asarray(pm_ra_rps, float).ravel() if pm_ra_rps is not None else z
        self.pm_dec_rps = np.asarray(pm_dec_rps, float).ravel() if pm_dec_rps is not None else z
        self.plx_rad = np.asarray(plx_rad, float).ravel() if plx_rad is not None else z
        self.filter_map = None      # None == full, unfiltered catalog

    def eval(self, et=0.0, r_obs_AU=(0.0, 0.0, 0.0)):
        """5-parameter standard model -> PointsS2 of ICRF unit vectors."""
        r_obs = np.asarray(r_obs_AU, float).reshape(3, 1)
        dt = et - self.t_epoch
        ra, dec = self.ra_rad, self.dec_rad
        p = np.vstack((-np.sin(ra), np.cos(ra), np.zeros(self.n)))
        q = np.vstack((-np.sin(dec) * np.cos(ra),
                       -np.sin(dec) * np.sin(ra),
                       np.cos(dec)))
        e0 = SphereCoords.raDecToCart(ra, dec)
        u = e0 + dt * (self.pm_ra_rps * p + self.pm_dec_rps * q) - self.plx_rad * r_obs
        u = u / np.linalg.norm(u, axis=0)
        return PointsS2(u)

    def filter(self, mask_or_idx):
        """Return a filtered copy. Accepts a boolean mask or an index array."""
        m = np.asarray(mask_or_idx)
        idx = np.nonzero(m)[0] if m.dtype == bool else m
        out = StarCatalog(self.ra_rad[idx], self.dec_rad[idx], self.vmag[idx],
                          self.ids[idx], self.t_epoch,
                          self.pm_ra_rps[idx], self.pm_dec_rps[idx], self.plx_rad[idx])
        out.filter_map = idx.astype(np.int64)
        return out

    def filter_mag(self, vmag_limit):
        return self.filter(self.vmag <= vmag_limit)

    # ── loaders ─────────────────────────────────────────────────────────────
    @classmethod
    def from_degrees(cls, ra_deg, dec_deg, vmag=None, ids=None, **kw):
        return cls(np.radians(np.asarray(ra_deg, float)),
                   np.radians(np.asarray(dec_deg, float)), vmag, ids, **kw)

    @classmethod
    def from_csv(cls, path, ra_col="ra_deg", dec_col="dec_deg", mag_col="vmag",
                 id_col=None):
        import csv
        ra, dec, mag, ids = [], [], [], []
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                ra.append(float(row[ra_col]))
                dec.append(float(row[dec_col]))
                mag.append(float(row[mag_col]))
                if id_col:
                    ids.append(row[id_col])
        return cls.from_degrees(ra, dec, mag, ids or None)


class Hipparcos(StarCatalog):
    """Hipparcos catalog loader (port of +sonic/Hipparcos.m constructor semantics)."""

    @classmethod
    def from_sonic_mat(cls, path):
        """Load SONIC's hipparcos.mat (needs scipy.io).

        Reads the same fields SONIC's constructor uses (HIP, Vmag, RA/DEC in deg,
        proper motions in mas/yr, parallax in mas) and converts to SI/radians.
        """
        from scipy.io import loadmat
        raw = loadmat(path, squeeze_me=True, struct_as_record=False)
        tab = raw["hip_db"]
        def col(name):
            return np.asarray(getattr(tab, name), float).ravel()
        obj = cls(Units.DEGtoRAD(col("RA_DEG")), Units.DEGtoRAD(col("DEC_DEG")),
                  vmag=col("Vmag"), ids=col("HIP"), t_epoch=HIP_EPOCH_TDB,
                  pm_ra_rps=Units.MASPYtoRPS(col("pmRA_MASPY")),
                  pm_dec_rps=Units.MASPYtoRPS(col("pmDEC_MASPY")),
                  plx_rad=Units.MAStoRAD(col("Plx_MAS")))
        return obj

    @classmethod
    def from_vizier(cls, vmag_limit=6.5):
        """Best-effort real Hipparcos-2 via astroquery/Vizier (optional, needs network)."""
        try:
            from astroquery.vizier import Vizier
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Hipparcos.from_vizier needs astroquery") from e
        v = Vizier(columns=["HIP", "RAICRS", "DEICRS", "Vmag", "pmRA", "pmDE", "Plx"],
                   column_filters={"Vmag": f"<{vmag_limit}"}, row_limit=-1)
        t = v.get_catalogs("I/311/hip2")[0]
        return cls(Units.DEGtoRAD(np.asarray(t["RAICRS"], float)),
                   Units.DEGtoRAD(np.asarray(t["DEICRS"], float)),
                   vmag=np.asarray(t["Vmag"], float),
                   ids=np.asarray(t["HIP"]), t_epoch=HIP_EPOCH_TDB,
                   pm_ra_rps=Units.MASPYtoRPS(np.asarray(t["pmRA"], float)),
                   pm_dec_rps=Units.MASPYtoRPS(np.asarray(t["pmDE"], float)),
                   plx_rad=Units.MAStoRAD(np.asarray(t["Plx"], float)))
