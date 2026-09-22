# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — part geometry.

Each part is an axis-aligned box with a pivot and a local axis. This is a STAND-IN.
The Phase I substrate is photogrammetry or 3-D Gaussian splatting of a real bicycle,
segmented into these same parts; the geometry stage is commodity work RIGLINE drives
and is not a contribution of this firm.

None of the measured results depend on it. The seven checks operate on the binding
between the Articulation Authority Set and whatever segments the capture produces,
so the detection rates are a property of the checks, not of the mesh quality.
"""
import math

MM = 1.0

# id: centre (x,y,z), half-extents, pivot, axis
SEGMENTS = {
    "seg-frame":     dict(c=(0, 620, -250), h=(30, 260, 420),  pivot=None,               axis=None),
    "seg-fork":      dict(c=(0, 700, 355),  h=(28, 300, 60),   pivot=(0, 1000, 300),     axis="Y"),
    "seg-bar":       dict(c=(0, 1010, 320), h=(300, 14, 14),   pivot=None,               axis=None),
    "seg-wheel":     dict(c=(0, 350, 400),  h=(22, 350, 350),  pivot=(0, 350, 400),      axis="X"),
    "seg-skewer":    dict(c=(0, 350, 400),  h=(85, 7, 7),      pivot=(0, 350, 400),      axis="X"),
    "seg-qrlever":   dict(c=(-95, 350, 400), h=(12, 35, 7),    pivot=(-85, 350, 400),    axis="Z"),
    "seg-qrnut":     dict(c=(85, 350, 400), h=(10, 16, 16),    pivot=(85, 350, 400),     axis="X"),
    "seg-armL":      dict(c=(-45, 690, 400), h=(10, 90, 12),   pivot=(-45, 760, 400),    axis="Z"),
    "seg-armR":      dict(c=(45, 690, 400), h=(10, 90, 12),    pivot=(45, 760, 400),     axis="Z"),
    "seg-padL":      dict(c=(-30, 620, 400), h=(6, 18, 25),    pivot=None,               axis=None),
    "seg-padR":      dict(c=(30, 620, 400), h=(6, 18, 25),     pivot=None,               axis=None),
    "seg-lever":     dict(c=(-230, 1000, 345), h=(10, 12, 70), pivot=(-230, 1010, 320),  axis="X"),
    "seg-fbolt":     dict(c=(0, 860, 380),  h=(8, 8, 14),      pivot=(0, 860, 380),      axis="Z"),
    # Segments a real capture produces that are not part of the equipment. They must be
    # classified, not silently ignored: unclassified geometry is what C1 refuses.
    "seg-standclamp": dict(c=(0, 300, -600), h=(60, 40, 60),    pivot=None,               axis=None),
    "seg-backdrop":   dict(c=(0, 900, -1200), h=(900, 900, 10), pivot=None,               axis=None),
}

# Geometry that carries no AAS part. Declaring it is mandatory; leaving it undeclared fails C1.
NON_ACTIONABLE = {"seg-standclamp", "seg-backdrop"}

# The correct binding: AAS part -> one OR MORE geometry segments. Photogrammetry routinely
# splits one physical part across several segments, so a one-to-one rule would be a property
# of the segmenter rather than of the equipment.
TRUE_BINDING = {
    "SPK-1000": ["seg-frame"],  "SPK-1100": ["seg-fork"],   "SPK-1110": ["seg-bar"],
    "SPK-1200": ["seg-wheel"],  "SPK-1210": ["seg-skewer"], "SPK-1211": ["seg-qrlever"],
    "SPK-1212": ["seg-qrnut"],  "SPK-1300": ["seg-armL"],   "SPK-1301": ["seg-armR"],
    "SPK-1310": ["seg-padL"],   "SPK-1311": ["seg-padR"],   "SPK-1400": ["seg-lever"],
    "SPK-1500": ["seg-fbolt"],
}


def segs_of(binding, pid):
    """Segments bound to a part, tolerating either a single id or a list."""
    v = binding.get(pid)
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple, set)) else [v]


def union_aabb(segs):
    boxes = [aabb(s) for s in segs]
    return [(min(b[i][0] for b in boxes), max(b[i][1] for b in boxes)) for i in range(3)]

AXIS_INDEX = {"X": 0, "Y": 1, "Z": 2}


def aabb(seg):
    c, h = SEGMENTS[seg]["c"], SEGMENTS[seg]["h"]
    return [(c[i] - h[i], c[i] + h[i]) for i in range(3)]


def volume(seg):
    h = SEGMENTS[seg]["h"]
    return 8.0 * h[0] * h[1] * h[2]


def overlap(a, b, tol=0.0):
    return all(a[i][0] < b[i][1] - tol and b[i][0] < a[i][1] - tol for i in range(3))


def contains(outer, inner, slack=60.0):
    """Is inner inside outer, allowing slack in mm? Used by C1 containment."""
    return all(inner[i][0] >= outer[i][0] - slack and inner[i][1] <= outer[i][1] + slack
               for i in range(3))


def _rot(p, pivot, axis, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    x, y, z = p[0] - pivot[0], p[1] - pivot[1], p[2] - pivot[2]
    if axis == "X":
        y, z = y * ca - z * sa, y * sa + z * ca
    elif axis == "Y":
        x, z = x * ca + z * sa, -x * sa + z * ca
    else:
        x, y = x * ca - y * sa, x * sa + y * ca
    return (x + pivot[0], y + pivot[1], z + pivot[2])


def swept_aabb(seg, motion, axis, start, end, samples=13):
    """AABB of the segment swept through its stated travel."""
    s = SEGMENTS[seg]
    c, h = s["c"], s["h"]
    corners = [(c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2])
               for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    pts = []
    for k in range(samples):
        t = start + (end - start) * k / float(samples - 1)
        if motion == "prismatic":
            i = AXIS_INDEX[axis]
            for p in corners:
                q = list(p); q[i] += t; pts.append(tuple(q))
        else:
            piv = s["pivot"] or c
            for p in corners:
                pts.append(_rot(p, piv, axis, t))
    return [(min(p[i] for p in pts), max(p[i] for p in pts)) for i in range(3)]
