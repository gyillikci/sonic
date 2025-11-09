"""Pose class for SONIC - Stub"""

class Pose:
    """Pose (rotation + translation) representation (stub)"""

    def __init__(self, att, t):
        self.att = att
        self.t = t

    def __repr__(self):
        return f"Pose(att={self.att}, t={self.t})"
