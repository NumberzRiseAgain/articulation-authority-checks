# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — glTF 2.0 export.

One node per part, positioned at its pivot so the joint rotates about the right point,
one box mesh per part, and one animation per procedural step driving that step's joint
through its stated travel. Single-file .gltf with the buffer embedded as a data URI, so
it opens in Unity, Unreal, Blender or a browser with nothing alongside it.
"""
import os, sys, json, base64, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aas as A, geometry as G, scenario as S
import math

BOX_I = [0,1,2, 0,2,3, 4,6,5, 4,7,6, 0,4,5, 0,5,1, 1,5,6, 1,6,2, 2,6,7, 2,7,3, 3,7,4, 3,4,0]


def box_verts(h):
    x, y, z = h
    return [(-x,-y, z),( x,-y, z),( x, y, z),(-x, y, z),
            (-x,-y,-z),( x,-y,-z),( x, y,-z),(-x, y,-z)]


def quat(axis, deg):
    a = math.radians(deg) / 2.0
    s = math.sin(a)
    v = {"X": (s,0,0), "Y": (0,s,0), "Z": (0,0,s)}[axis]
    return [v[0], v[1], v[2], math.cos(a)]


def build(aas, binding, scn):
    buf, views, accs, meshes, nodes = bytearray(), [], [], [], []
    node_of = {}

    for pid, p in sorted(aas["parts"].items()):
        # 5 Sep 2026: the binding maps a part to a LIST of segments since C1 became
        # coverage-and-identity (3 Sep). One node per part; the part's box is the first
        # segment bound to it, which is every segment in the reference binding.
        seg = G.segs_of(binding, pid)[0]
        s = G.SEGMENTS[seg]
        piv = s["pivot"] or s["c"]
        vs = [(v[0] + s["c"][0] - piv[0], v[1] + s["c"][1] - piv[1], v[2] + s["c"][2] - piv[2])
              for v in box_verts(s["h"])]
        # positions
        off = len(buf)
        for v in vs:
            buf.extend(struct.pack("<3f", *[c / 1000.0 for c in v]))
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(buf) - off})
        mins = [min(v[i] for v in vs) / 1000.0 for i in range(3)]
        maxs = [max(v[i] for v in vs) / 1000.0 for i in range(3)]
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": 8,
                     "type": "VEC3", "min": mins, "max": maxs})
        pos_acc = len(accs) - 1
        # indices
        off = len(buf)
        for i in BOX_I:
            buf.extend(struct.pack("<H", i))
        if (len(buf) - off) % 4:
            buf.extend(b"\x00" * (4 - (len(buf) - off) % 4))
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(BOX_I) * 2})
        accs.append({"bufferView": len(views) - 1, "componentType": 5123,
                     "count": len(BOX_I), "type": "SCALAR"})
        idx_acc = len(accs) - 1

        meshes.append({"name": p["name"],
                       "primitives": [{"attributes": {"POSITION": pos_acc}, "indices": idx_acc}]})
        nodes.append({"name": "%s %s" % (pid, p["name"]),
                      "mesh": len(meshes) - 1,
                      "translation": [c / 1000.0 for c in piv]})
        node_of[pid] = len(nodes) - 1

    # animations, one per step
    anims = []
    for st in sorted(scn["steps"], key=lambda s: s["order"]):
        if st["travel_end"] is None or st["part"] not in node_of:
            continue
        t0, t1 = 0.0, 1.5
        off = len(buf)
        buf.extend(struct.pack("<2f", t0, t1))
        views.append({"buffer": 0, "byteOffset": off, "byteLength": 8})
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": 2,
                     "type": "SCALAR", "min": [t0], "max": [t1]})
        time_acc = len(accs) - 1

        a0, a1 = st["travel_start"] or 0.0, st["travel_end"]
        if st["motion"] == "prismatic":
            i = G.AXIS_INDEX[st["axis"]]
            _seg = G.segs_of(binding, st["part"])[0]
            piv = G.SEGMENTS[_seg]["pivot"] or G.SEGMENTS[_seg]["c"]
            vals = []
            for d in (a0, a1):
                t = [c / 1000.0 for c in piv]; t[i] += d / 1000.0; vals.append(t)
            path = "translation"
        else:
            vals = [quat(st["axis"], a0), quat(st["axis"], a1)]
            path = "rotation"
        off = len(buf)
        for v in vals:
            buf.extend(struct.pack("<%df" % len(v), *v))
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(buf) - off})
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": 2,
                     "type": "VEC3" if path == "translation" else "VEC4"})
        val_acc = len(accs) - 1
        anims.append({
            "name": "%s %s" % (st["id"], st["text"][:48]),
            "samplers": [{"input": time_acc, "output": val_acc, "interpolation": "LINEAR"}],
            "channels": [{"sampler": 0, "target": {"node": node_of[st["part"]], "path": path}}],
        })

    gltf = {
        "asset": {"version": "2.0", "generator": "SPOKELINE (Numberz.ai) - surrogate data"},
        "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes, "accessors": accs, "bufferViews": views,
        "animations": anims,
        "buffers": [{"byteLength": len(buf),
                     "uri": "data:application/octet-stream;base64," +
                            base64.b64encode(bytes(buf)).decode("ascii")}],
    }
    return gltf


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    a = A.extract(os.path.join(here, "corpus", "s1000d"))
    scn = S.build(a, G.TRUE_BINDING)
    gltf = build(a, G.TRUE_BINDING, scn)
    out = os.path.join(here, "runs", "latest", "spokeline_front_wheel.gltf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(gltf, open(out, "w"))
    print("wrote %s  (%d nodes, %d meshes, %d animations, %.0f KB)"
          % (out, len(gltf["nodes"]), len(gltf["meshes"]), len(gltf["animations"]),
             os.path.getsize(out) / 1024.0))


if __name__ == "__main__":
    main()
