# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — the seven deterministic checks.

Each check is arithmetic or graph logic against the Articulation Authority Set.
No model confidence is consulted anywhere in this file. A binding proposal is a
proposal until these have run.

A finding with severity "fail" stops the export. Severity "advisory" is shown to the
subject-matter expert and does not stop anything: C3 raises one where the source
states no travel limit, because assuming a joint is free is exactly the error that
would otherwise pass silently.
"""
import geometry as G

CW_WORDS = ("clockwise",)
CCW_WORDS = ("counter-clockwise", "counterclockwise", "anti-clockwise")


def _ancestors(aas, pid):
    out, cur = [], aas["parts"].get(pid, {}).get("parent")
    while cur:
        out.append(cur)
        cur = aas["parts"].get(cur, {}).get("parent")
    return out


def _expanded(box, frac=0.25):
    out = []
    for lo, hi in box:
        pad = (hi - lo) * frac
        out.append((lo - pad, hi + pad))
    return out


def c1_coverage_and_identity(aas, binding, scenario):
    """C1. Coverage and identity consistency.

    Not a one-to-one bijection. A capture routinely splits one physical part across several
    mesh segments, and it also produces geometry that is not part of the equipment at all.
    Demanding 1:1 would make the check a property of the segmenter rather than of the
    equipment, and would fail on exactly the real captures Phase I is for.

    What the check does require, which is the safety property:
      (a) every actionable AAS part maps to at least one geometry segment;
      (b) every actionable geometry segment traces back to exactly one AAS part;
      (c) geometry that carries no part is permitted, but only when it has been explicitly
          classified as non-actionable. Unclassified geometry fails.
      (d) the segments bound to a part sit within the part's parent, so a part cannot be
          bound to geometry belonging somewhere else on the assembly.
    """
    f = []
    claimed = {}
    for pid in aas["parts"]:
        segs = G.segs_of(binding, pid)
        if not segs:
            f.append(("C1", "fail", pid, "no geometry segment maps to this actionable part"))
            continue
        for sg in segs:
            if sg in claimed and claimed[sg] != pid:
                f.append(("C1", "fail", pid,
                          "segment %s is claimed by both %s and %s" % (sg, claimed[sg], pid)))
            claimed[sg] = pid
    for sg in G.SEGMENTS:
        if sg in claimed:
            if sg in G.NON_ACTIONABLE:
                f.append(("C1", "fail", sg,
                          "segment is classified non-actionable but is bound to %s" % claimed[sg]))
            continue
        if sg not in G.NON_ACTIONABLE:
            f.append(("C1", "fail", sg,
                      "geometry segment carries no part and is not classified non-actionable"))
    for pid, p in aas["parts"].items():
        par = p.get("parent")
        if not par:
            continue
        cs, ps = G.segs_of(binding, pid), G.segs_of(binding, par)
        if not cs or not ps:
            continue
        if not G.overlap(_expanded(G.union_aabb(ps)), G.union_aabb(cs)):
            f.append(("C1", "fail", pid,
                      "geometry bound to %s does not sit within its parent %s"
                      % (pid, par)))
    return f


def _step_class(aas, st):
    """A step is articulation if the part declares a joint of that motion type."""
    j = aas["joints"].get(st["part"])
    if j is None:
        return "extraction", None
    if st["motion"] == "prismatic" and j["type"] != "prismatic":
        return "extraction", j
    if st["motion"] == "revolute" and j["type"] not in ("revolute", "continuous"):
        return "extraction", j
    return "articulation", j


def c2_axis_consistency(aas, binding, scenario):
    f = []
    for st in scenario["steps"]:
        kind, j = _step_class(aas, st)
        if kind != "articulation":
            continue
        if st["axis"] != j["axis"]:
            f.append(("C2", "fail", st["id"],
                      "step turns %s about %s; the authority declares axis %s"
                      % (st["part"], st["axis"], j["axis"])))
        t = (st.get("text") or "").lower()
        want = None
        if any(w in t for w in CCW_WORDS):
            want = "negative"
        elif any(w in t for w in CW_WORDS):
            want = "positive"
        if want and st.get("sense") and st["sense"] != want:
            f.append(("C2", "fail", st["id"],
                      "step text says %s but the motion is %s"
                      % ("counter-clockwise" if want == "negative" else "clockwise", st["sense"])))
    return f


def c3_travel_bounds(aas, binding, scenario):
    f = []
    for st in scenario["steps"]:
        kind, j = _step_class(aas, st)
        if kind != "articulation" or st["travel_end"] is None:
            continue
        if j["lower"] is None or j["upper"] is None:
            f.append(("C3", "advisory", st["id"],
                      "no travel limit stated for %s; not assumed free" % st["part"]))
            continue
        lo, hi = min(j["lower"], j["upper"]), max(j["lower"], j["upper"])
        for v in (st["travel_start"], st["travel_end"]):
            if v is not None and (v < lo - 1e-6 or v > hi + 1e-6):
                f.append(("C3", "fail", st["id"],
                          "travel %.0f %s is outside the declared limit %.0f to %.0f"
                          % (v, st["unit"], lo, hi)))
    return f


def c4_ordering(aas, binding, scenario):
    f = []
    steps = sorted(scenario["steps"], key=lambda s: s["order"])
    for i, a in enumerate(steps):
        for b in steps[i + 1:]:
            if a["part"] == b["part"]:
                continue
            if b["part"] in _ancestors(aas, a["part"]):
                continue                      # child before parent: correct
            if a["part"] in _ancestors(aas, b["part"]):
                f.append(("C4", "fail", b["id"],
                          "%s is removed at step %s before its own sub-component %s at step %s"
                          % (a["part"], a["id"], b["part"], b["id"])))
    return f


def c5_collision(aas, binding, scenario):
    f = []
    for st in scenario["steps"]:
        segs = G.segs_of(binding, st["part"])
        if not segs or st["travel_end"] is None:
            continue
        boxes = [G.swept_aabb(sg, st["motion"], st["axis"],
                              st["travel_start"] or 0.0, st["travel_end"]) for sg in segs]
        swept = [(min(b[i][0] for b in boxes), max(b[i][1] for b in boxes)) for i in range(3)]
        rel = set(_ancestors(aas, st["part"]))
        for pid, p in aas["parts"].items():
            if pid == st["part"] or pid in rel:
                continue
            if st["part"] in _ancestors(aas, pid):
                continue
            others = [o for o in G.segs_of(binding, pid) if o not in segs]
            if not others:
                continue
            if G.overlap(swept, G.union_aabb(others), tol=1.0):
                f.append(("C5", "fail", st["id"],
                          "%s cannot travel its stated path without striking %s"
                          % (st["part"], pid)))
                break
    return f


def c6_constraint_attachment(aas, binding, scenario):
    f = []
    attached = set()
    for st in scenario["steps"]:
        for c in st["conditions"]:
            attached.add((c["id"], st["id"]))
    for con in aas["constraints"]:
        if (con["id"], con["step"]) not in attached:
            f.append(("C6", "fail", con["id"],
                      "%s from the authority is not attached to step %s in the scenario"
                      % (con["kind"], con["step"])))
    return f


def c7_provenance(aas, binding, scenario):
    f = []
    known_steps = {s["source"] for s in aas["steps"]}
    known_cons = {c["source"] for c in aas["constraints"]}
    for st in scenario["steps"]:
        if st.get("source") not in known_steps:
            f.append(("C7", "fail", st["id"],
                      "step has no source element in the authority set"))
        for c in st["conditions"]:
            if c.get("source") not in known_cons:
                f.append(("C7", "fail", c["id"],
                          "annotation has no source element in the authority set"))
    return f


CHECKS = [c1_coverage_and_identity, c2_axis_consistency, c3_travel_bounds,
          c4_ordering, c5_collision, c6_constraint_attachment, c7_provenance]


def run_all(aas, binding, scenario):
    out = []
    for fn in CHECKS:
        out.extend(fn(aas, binding, scenario))
    return out


def failures(findings):
    return [f for f in findings if f[1] == "fail"]
