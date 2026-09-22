# SPOKELINE — measured results

**Run 2 September 2026, seed 20260902, 50 trials per fault class. Company-funded.**
Regenerate with `08_Analysis/code/spokeline/src/run.py`. Every figure below is written
by that script into `runs/latest/metrics.json`; nothing here is asserted by hand.

## What was measured

Not "the pipeline works." The question is narrower and testable: **given an Articulation
Authority Set extracted from a technical manual, and a proposed binding of that authority
to geometry, how often do seven deterministic checks catch a wrong motion?**

Ground truth is known because every fault is injected deliberately.

## Headline

| | |
|---|---|
| Overall detection | **290 / 300 = 96.7%** |
| False positives, 50 clean twins | **0 / 50 = 0%** |
| Advisories on a clean run | 2, both legitimate: the source states no travel limit for those joints |
| Corpus | 4 data modules, 13 parts, 9 joints, 6 procedural steps, 7 constraints |
| Marking custody | 4/4 data modules carry their distribution statement through to the export |
| Wall clock, full scored run | under a second (0.20 s on 2 Sep; 0.26 s in the 5 Sep evidence-pack run) |

## Per class

| Fault class | Detected | Rate | Checks that fired |
|---|---|---:|---|
| F1 wrong-part binding | 49/50 | 98% | C1 bijection and containment, C5 collision |
| F2 inverted joint axis | 41/50 | 82% | C2 axis consistency, C3 travel bounds |
| F3 out-of-range travel | 50/50 | 100% | C3 travel bounds |
| F4 step transposition | 50/50 | 100% | C4 ordering |
| F5 dropped safety condition | 50/50 | 100% | C6 constraint attachment |
| F6 phantom step | 50/50 | 100% | C7 provenance |

## The residual, with a reason for every miss

Ten misses out of three hundred, and they fall into exactly two causes. Both are
properties of the source data rather than of the checks, and both are worth reporting
to the Government because both are fixable at the technical-data end.

**Nine misses: an inverted direction on a joint the authority does not bound.**
All nine are step `stp-110`, the fender bolt. Its joint is declared `continuous` with no
travel limit, and its step text states no direction. There is nothing in the authority to
check the inverted motion against, so C2 has no directional claim to compare and C3 has no
limit to exceed. **The check can only catch a reversed direction where the source states
either a limit or a direction.** A recommendation follows directly: a data module that
states a direction of rotation in the step text makes the error catchable, and that costs
the technical-data author one word.

**One miss: two mirror-image parts swapped.**
The quick-release nut and the skewer lever, bound to each other's geometry. Both are small,
both hang off the same parent, and both sit inside the parent's expanded bounding volume,
so containment cannot separate them and neither part moves in a way that produces a
collision. Geometric checks cannot distinguish parts that are geometrically alike; a part
number read off the asset, or an SME glance, can. That is what the human-on-the-loop review
is for, and it is why the ledger shows the SME what was bound rather than only what failed.

## What this result does not show

The geometry here is a **stand-in**: parametric boxes, not photogrammetry. That is
deliberate and it does not weaken the number, because the seven checks operate on the
binding between the authority set and whatever segments a capture produces, not on mesh
quality. What it does mean is that **no claim is made here about capture, segmentation or
reconstruction accuracy** — those are commodity stages RIGLINE drives, and measuring them
is not this firm's contribution.

The technical data is **surrogate**, authored by Numberz.ai in S1000D Issue 4.2 shape. The
real public S1000D Bike Data Set is the Phase I substrate; the extractor reads the same
element structure and needs no change to be pointed at it.

The pre-registration is **internal**, not deposited with an external registry before the
run. The classes and metric definitions were fixed in `POC_SPEC.md` before any code
existed, and the run followed. Depositing the protocol on OSF before the first scored run
on real photogrammetry is a Phase I action.

## Deliverables

| Path | What it is |
|---|---|
| `08_Analysis/code/spokeline/` | The whole pipeline. `python3 src/run.py` reproduces every number. |
| `runs/latest/metrics.json` | Every figure quoted anywhere. |
| `runs/latest/ledger.json` | The authority set, the scenario, the binding, the findings. |
| `runs/latest/spokeline_front_wheel.gltf` | glTF 2.0, 13 nodes, 6 animations, single file. Opens in Unity, Unreal or Blender. |
| `viewer/spokeline_viewer.html` | The hosted page. Self-contained, no install. |
| `08_Analysis/code/spokeline/runs/PREREGISTRATION.md` | The protocol, fixed before the run. |
