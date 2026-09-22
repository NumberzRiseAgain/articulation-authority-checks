# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — deliberate fault injection.

Six classes, each a thing a binding proposer actually gets wrong. Ground truth is
known because the fault is inserted on purpose, so a miss is a miss and is reported
with a reason rather than absorbed.

Pre-registration: the six classes, the expected check for each, and the metric
definitions below were fixed BEFORE the first scored run. See runs/PREREGISTRATION.md.
"""
import copy, random

AXES = ["X", "Y", "Z"]


def _articulation_steps(aas, scenario):
    out = []
    for st in scenario["steps"]:
        j = aas["joints"].get(st["part"])
        if j and st["travel_end"] is not None:
            if st["motion"] == "prismatic" and j["type"] != "prismatic":
                continue
            out.append(st)
    return out


def f1_wrong_part_binding(aas, binding, scenario, rng):
    """Two parts bound to each other's geometry."""
    def anc(p):
        out, cur = [], aas["parts"].get(p, {}).get("parent")
        while cur:
            out.append(cur); cur = aas["parts"].get(cur, {}).get("parent")
        return out
    ids = list(aas["parts"])
    for _ in range(200):
        a, b = rng.sample(ids, 2)
        if b in anc(a) or a in anc(b):
            continue
        nb = {k: (list(v) if isinstance(v, list) else v) for k, v in binding.items()}
        nb[a], nb[b] = nb[b], nb[a]
        return nb, scenario, "bound %s and %s to each other's geometry" % (a, b), "C1"
    return dict(binding), scenario, "no eligible pair", "C1"


def f2_inverted_joint_axis(aas, binding, scenario, rng):
    """The part is driven the opposite way along its axis."""
    cands = _articulation_steps(aas, scenario)
    st = rng.choice(cands)
    ns = copy.deepcopy(scenario)
    for s in ns["steps"]:
        if s["id"] == st["id"]:
            s["travel_start"] = -(s["travel_start"] or 0.0)
            s["travel_end"] = -(s["travel_end"] or 0.0)
            s["sense"] = "positive" if s.get("sense") == "negative" else "negative"
            tgt = s["id"]
    return dict(binding), ns, "inverted the driven direction of step %s" % tgt, "C2/C3"


def f3_out_of_range_travel(aas, binding, scenario, rng):
    """Motion driven past the limit the authority states."""
    cands = [s for s in _articulation_steps(aas, scenario)
             if aas["joints"][s["part"]]["upper"] is not None]
    st = rng.choice(cands)
    ns = copy.deepcopy(scenario)
    for s in ns["steps"]:
        if s["id"] == st["id"]:
            up = aas["joints"][s["part"]]["upper"]
            s["travel_end"] = up * (1.15 + 0.5 * rng.random())
            tgt = s["id"]
    return dict(binding), ns, "drove step %s past its stated limit" % tgt, "C3"


def f4_step_transposition(aas, binding, scenario, rng):
    """Two steps swapped where one genuinely depends on the other."""
    def anc(p):
        out, cur = [], aas["parts"].get(p, {}).get("parent")
        while cur:
            out.append(cur); cur = aas["parts"].get(cur, {}).get("parent")
        return out
    steps = sorted(scenario["steps"], key=lambda s: s["order"])
    pairs = [(i, j) for i in range(len(steps)) for j in range(i + 1, len(steps))
             if steps[j]["part"] in anc(steps[i]["part"])]
    if not pairs:
        return dict(binding), scenario, "no dependent pair", "C4"
    i, j = rng.choice(pairs)
    ns = copy.deepcopy(scenario)
    ns["steps"][i]["order"], ns["steps"][j]["order"] = \
        ns["steps"][j]["order"], ns["steps"][i]["order"]
    return dict(binding), ns, "swapped dependent steps %s and %s" % (
        steps[i]["id"], steps[j]["id"]), "C4"


def f5_dropped_safety_condition(aas, binding, scenario, rng):
    """A warning, caution, tool or torque value is not carried onto its step."""
    cands = [(si, ci) for si, s in enumerate(scenario["steps"])
             for ci, c in enumerate(s["conditions"])]
    si, ci = rng.choice(cands)
    ns = copy.deepcopy(scenario)
    dropped = ns["steps"][si]["conditions"].pop(ci)
    return dict(binding), ns, "dropped the %s from step %s" % (
        dropped["kind"], ns["steps"][si]["id"]), "C6"


def f6_phantom_step(aas, binding, scenario, rng):
    """A plausible step the authority does not contain."""
    ns = copy.deepcopy(scenario)
    base = rng.choice(ns["steps"])
    ph = copy.deepcopy(base)
    ph.update(id="stp-phantom", order=len(ns["steps"]),
              text="Verify accumulator pressure before proceeding.",
              source="INVENTED#none", conditions=[])
    ns["steps"].append(ph)
    return dict(binding), ns, "inserted a step with no source in the authority set", "C7"


CLASSES = [
    ("F1 wrong-part binding", f1_wrong_part_binding),
    ("F2 inverted joint axis", f2_inverted_joint_axis),
    ("F3 out-of-range travel", f3_out_of_range_travel),
    ("F4 step transposition", f4_step_transposition),
    ("F5 dropped safety condition", f5_dropped_safety_condition),
    ("F6 phantom step", f6_phantom_step),
]
