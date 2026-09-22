# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""Write results/manifest.json: run identifier, seed, python, platform, source digests.

The run identifier is derived from the source digests and the seed, so the same sources and
seed always produce the same identifier (EVIDENCE_PACK.md, "Identified").
"""
import os, sys, json, hashlib, platform, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.dirname(HERE)
SRC = os.path.join(HERE, "spokeline", "src")
CORPUS = os.path.join(HERE, "spokeline", "corpus", "s1000d")
SEED = 20260902


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    sources = {}
    for d in (SRC, CORPUS):
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.isfile(p) and (f.endswith(".py") or f.endswith(".XML")):
                sources[os.path.relpath(p, HERE)] = sha(p)
    h = hashlib.sha256()
    for k in sorted(sources):
        h.update(("%s %s %d\n" % (k, sources[k], SEED)).encode())
    metrics = json.load(open(os.path.join(A, "results", "spokeline_metrics.json")))
    man = {
        "study": "SPOKELINE — articulation binding validator, fault injection",
        "topic": "DON26BZ05-NV071",
        "run_identifier": h.hexdigest()[:16],
        "seed": SEED,
        "trials_per_class": metrics["trials_per_class"],
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "libraries": "stdlib only",
        "network": "none", "gpu": "none",
        "source_digests": sources,
        "results": {
            "spokeline_metrics.json": sha(os.path.join(A, "results", "spokeline_metrics.json")),
            "spokeline_ledger.json": sha(os.path.join(A, "results", "spokeline_ledger.json")),
            "spokeline_front_wheel.gltf": sha(os.path.join(A, "results", "spokeline_front_wheel.gltf")),
            "spokeline_viewer.html": sha(os.path.join(HERE, "spokeline", "viewer", "spokeline_viewer.html")),
        },
        "headline": {
            "detected": metrics["overall"]["detected"], "faults": metrics["overall"]["faults"],
            "rate": metrics["overall"]["rate"],
            "false_positive_runs": metrics["clean_control"]["false_positive_runs"],
            "clean_runs": metrics["clean_control"]["runs"],
            "wall_clock_seconds": metrics["wall_clock_seconds"],
        },
    }
    out = os.path.join(A, "results", "manifest.json")
    json.dump(man, open(out, "w"), indent=2)
    print("manifest -> results/manifest.json  run_identifier %s" % man["run_identifier"])


if __name__ == "__main__":
    main()
