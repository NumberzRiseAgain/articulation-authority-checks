# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — build the scenario from the Authority Set and a binding."""
import copy


def build(aas, binding):
    steps = []
    for st in sorted(aas["steps"], key=lambda s: s["order"]):
        s = copy.deepcopy(st)
        s["segment"] = binding.get(st["part"])
        steps.append(s)
    return {"model": aas["model"], "steps": steps}
