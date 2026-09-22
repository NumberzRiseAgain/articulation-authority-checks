# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — the scored run. Writes runs/latest/metrics.json and ledger.json.

Every figure quoted in Volume 2 is written by this file and can be regenerated.
"""
import os, sys, json, random, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aas as A, geometry as G, scenario as S, checks as C, inject as I

TRIALS = 50
SEED = 20260902


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    t0 = time.time()
    a = A.extract(os.path.join(here, "corpus", "s1000d"))
    base_scn = S.build(a, G.TRUE_BINDING)

    # ---------- clean twins: the false-positive control
    clean_fp, clean_adv = 0, 0
    for _ in range(TRIALS):
        f = C.run_all(a, G.TRUE_BINDING, base_scn)
        if C.failures(f):
            clean_fp += 1
        clean_adv = len(f) - len(C.failures(f))

    # ---------- fault injection
    rng = random.Random(SEED)
    per_class, misses = {}, []
    for name, fn in I.CLASSES:
        hit = 0
        fired = {}
        for _ in range(TRIALS):
            b2, s2, desc, expect = fn(a, G.TRUE_BINDING, base_scn, rng)
            f = C.failures(C.run_all(a, b2, s2))
            if f:
                hit += 1
                for x in f:
                    fired[x[0]] = fired.get(x[0], 0) + 1
            else:
                misses.append({"class": name, "injected": desc, "expected": expect})
        per_class[name] = {"trials": TRIALS, "detected": hit,
                           "rate": round(hit / float(TRIALS), 4),
                           "checks_that_fired": fired}

    total = sum(v["trials"] for v in per_class.values())
    det = sum(v["detected"] for v in per_class.values())

    # ---------- residual, with a named reason per distinct miss
    reasons = {}
    for m in misses:
        reasons.setdefault((m["class"], m["injected"]), 0)
        reasons[(m["class"], m["injected"])] += 1
    residual = [{"class": k[0], "injected": k[1], "occurrences": v}
                for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])]

    metrics = {
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "seed": SEED, "trials_per_class": TRIALS,
        "corpus": {
            "data_modules": len(a["sources"]),
            "parts": len(a["parts"]),
            "joints": len(a["joints"]),
            "procedural_steps": len(a["steps"]),
            "constraints": len(a["constraints"]),
            "marking_custody": "%d/%d" % (len(a["markings"]), len(a["sources"])),
        },
        "clean_control": {
            "runs": TRIALS,
            "false_positive_runs": clean_fp,
            "false_positive_rate": round(clean_fp / float(TRIALS), 4),
            "advisories_per_run": clean_adv,
        },
        "detection": per_class,
        "overall": {"faults": total, "detected": det,
                    "rate": round(det / float(total), 4)},
        "residual": residual,
        "wall_clock_seconds": round(time.time() - t0, 2),
    }

    out = os.path.join(here, "runs", "latest")
    os.makedirs(out, exist_ok=True)
    json.dump(metrics, open(os.path.join(out, "metrics.json"), "w"), indent=2)
    json.dump({"aas": a, "scenario": base_scn, "binding": G.TRUE_BINDING,
               "findings": C.run_all(a, G.TRUE_BINDING, base_scn)},
              open(os.path.join(out, "ledger.json"), "w"), indent=2)

    print("=" * 74)
    print("SPOKELINE — scored run   seed %d, %d trials per class" % (SEED, TRIALS))
    print("=" * 74)
    c = metrics["corpus"]
    print("corpus     : %d data modules, %d parts, %d joints, %d steps, %d constraints"
          % (c["data_modules"], c["parts"], c["joints"], c["procedural_steps"], c["constraints"]))
    print("markings   : %s data modules carry their distribution statement through" % c["marking_custody"])
    print()
    print("clean control (%d runs): %d false positives, %.1f%%   [%d advisories per run]"
          % (TRIALS, clean_fp, 100 * clean_fp / float(TRIALS), clean_adv))
    print()
    print("%-30s %8s %10s   %s" % ("fault class", "detected", "rate", "checks that fired"))
    print("-" * 74)
    for k, v in per_class.items():
        fired = ", ".join("%s x%d" % (a_, b_) for a_, b_ in sorted(v["checks_that_fired"].items()))
        print("%-30s %5d/%-3d %9.1f%%   %s" % (k, v["detected"], v["trials"], 100 * v["rate"], fired))
    print("-" * 74)
    print("%-30s %5d/%-3d %9.1f%%" % ("OVERALL", det, total, 100 * det / float(total)))
    print()
    if residual:
        print("RESIDUAL — every miss, with the reason it was missed:")
        for r in residual:
            print("  %-28s %3d x  %s" % (r["class"], r["occurrences"], r["injected"]))
    else:
        print("RESIDUAL — none.")
    print()
    print("wall clock %.2f s   ->  runs/latest/metrics.json" % metrics["wall_clock_seconds"])


if __name__ == "__main__":
    main()
