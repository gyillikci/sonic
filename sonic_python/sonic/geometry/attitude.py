"""
Attitude class for SONIC
Stub for future implementation
"""

import numpy as np


class Attitude:
    """Attitude/rotation representation (stub)"""

    def __init__(self, dcm):
        """Initialize from DCM (Direction Cosine Matrix)"""
        self.dcm = np.array(dcm)

    def __repr__(self):
        return f"Attitude(dcm shape={self.dcm.shape})"
