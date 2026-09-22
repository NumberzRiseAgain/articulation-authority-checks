# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — Articulation Authority Set extraction from S1000D data modules.

The AAS is the Government-owned artifact. Nothing downstream invents any of it:
every part, joint, ordering edge and constraint carries the id of the source
element it came from, and anything without one is refused by check C7.
"""
import os, glob, json
import xml.etree.ElementTree as ET

AXES = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}


def _txt(el):
    return " ".join("".join(el.itertext()).split())


def extract(corpus_dir):
    aas = {"model": None, "parts": {}, "joints": {}, "steps": [],
           "constraints": [], "markings": {}, "sources": []}

    for path in sorted(glob.glob(os.path.join(corpus_dir, "*.XML"))):
        tree = ET.parse(path)
        root = tree.getroot()
        dm = os.path.basename(path)
        aas["sources"].append(dm)

        code = root.find(".//dmCode")
        if code is not None and aas["model"] is None:
            aas["model"] = code.get("modelIdentCode")
        restr = root.find(".//dataRestrictions")
        if restr is not None:
            aas["markings"][dm] = _txt(restr)

        # --- part inventory, from the illustrated parts data
        for csn in root.findall(".//catalogSeqNumber"):
            pn = csn.get("partNumber")
            aas["parts"][pn] = {
                "id": pn,
                "name": _txt(csn.find("partName")),
                "parent": csn.get("parent") or None,
                "source": dm + "#item" + csn.get("item"),
            }

        # --- joints, from the articulation data in the descriptive module
        for j in root.findall(".//articulationData/joint"):
            pn = j.get("partRef")
            lo, hi = j.get("lowerLimit"), j.get("upperLimit")
            aas["joints"][pn] = {
                "part": pn,
                "type": j.get("type"),
                "axis": j.get("axis"),
                "lower": None if lo is None else float(lo),
                "upper": None if hi is None else float(hi),
                "unit": j.get("unit"),
                "source": dm + "#joint:" + pn,
            }

        # --- procedural steps, with their conditions
        for order, st in enumerate(root.findall(".//proceduralStep")):
            sid = st.get("id")
            conds = []
            for kind in ("warning", "caution"):
                for c in st.findall(kind):
                    cid = c.get("id")
                    conds.append({"id": cid, "kind": kind, "text": _txt(c),
                                  "source": dm + "#" + cid})
                    aas["constraints"].append({"id": cid, "kind": kind, "step": sid,
                                               "source": dm + "#" + cid})
            if st.get("toolRef"):
                aas["constraints"].append({"id": st.get("toolRef"), "kind": "tool",
                                           "step": sid, "source": dm + "#" + st.get("toolRef")})
                conds.append({"id": st.get("toolRef"), "kind": "tool",
                              "text": "tool required", "source": dm + "#" + st.get("toolRef")})
            if st.get("torque"):
                tid = sid + ":torque"
                aas["constraints"].append({"id": tid, "kind": "torque", "step": sid,
                                           "value": float(st.get("torque")),
                                           "unit": st.get("torqueUnit"),
                                           "source": dm + "#" + sid + "@torque"})
                conds.append({"id": tid, "kind": "torque",
                              "text": "%s %s" % (st.get("torque"), st.get("torqueUnit")),
                              "source": dm + "#" + sid + "@torque"})
            para = st.find("para")
            aas["steps"].append({
                "id": sid,
                "dm": dm,
                "order": order,
                "part": st.get("partRef"),
                "motion": st.get("motion"),
                "axis": st.get("axis"),
                "sense": st.get("sense"),
                "travel_start": float(st.get("travelStart")) if st.get("travelStart") else None,
                "travel_end": float(st.get("travelEnd")) if st.get("travelEnd") else None,
                "unit": st.get("travelUnit"),
                "text": _txt(para) if para is not None else "",
                "conditions": conds,
                "source": dm + "#" + sid,
            })

    # steps are ordered per data module, then by document order
    aas["steps"].sort(key=lambda s: (s["dm"], s["order"]))
    for i, s in enumerate(aas["steps"]):
        s["order"] = i
    return aas


def descendants(aas, pn):
    out = set()
    stack = [pn]
    while stack:
        cur = stack.pop()
        for p in aas["parts"].values():
            if p["parent"] == cur and p["id"] not in out:
                out.add(p["id"]); stack.append(p["id"])
    return out


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aas = extract(os.path.join(here, "corpus", "s1000d"))
    print("model            : %s" % aas["model"])
    print("data modules     : %d" % len(aas["sources"]))
    print("parts            : %d" % len(aas["parts"]))
    print("joints           : %d" % len(aas["joints"]))
    print("procedural steps : %d" % len(aas["steps"]))
    print("constraints      : %d" % len(aas["constraints"]))
    print("marking custody  : %d/%d data modules carry a distribution statement"
          % (len(aas["markings"]), len(aas["sources"])))
    out = os.path.join(here, "runs", "aas.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(aas, open(out, "w"), indent=2)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
