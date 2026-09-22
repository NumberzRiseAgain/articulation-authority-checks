# SPOKELINE — pre-registration of the scored run

**Written 2 September 2026. Read the timeline note at the bottom before citing this.**

## What was fixed before any code was written

The six fault classes, the check each is expected to trip, and the metric definitions
were fixed in `08_Analysis/POC_SPEC.md` before a line of the pipeline existed.

| Class | Injected fault | Expected detector |
|---|---|---|
| F1 | Two parts bound to each other's geometry | C1 bijection and containment |
| F2 | The driven direction of a motion inverted | C2 axis consistency, or C3 travel bounds |
| F3 | A motion driven past its stated limit | C3 travel bounds |
| F4 | Two genuinely dependent steps swapped | C4 ordering |
| F5 | A warning, caution, tool or torque not carried onto its step | C6 constraint attachment |
| F6 | A plausible step with no source in the authority set | C7 provenance |

## Metric definitions, fixed in advance

- **Detection rate, per class** — the fraction of injected faults on which at least one
  check returns a finding of severity `fail`. A finding of severity `advisory` does not
  count as a detection.
- **False-positive rate** — the fraction of runs on the unmodified scenario that return
  any finding of severity `fail`. Advisories are counted and reported separately.
- **Residual** — every miss, grouped by the exact fault injected, with a stated reason.
  Misses are reported, never absorbed into a rounded rate.
- **Trials** — 50 per class, seed 20260902, fixed before the run.

## What counts as a fault, and what does not

F4 injects only transpositions between steps that stand in a genuine dependency, that is
where one part is an ancestor of the other in the illustrated parts breakdown. Swapping
two independent steps is not an error, and counting a non-detection there would inflate
the rate. F1 excludes ancestor pairs for the same reason.

## Timeline note, stated plainly

The classes and metric definitions above were fixed in `POC_SPEC.md` before the pipeline
was written, and the run followed. **They were not deposited with an external registry
before the run**, so this is an internal pre-registration and should be described that
way and not as an independent one. Depositing the protocol on OSF before the first scored
run on real photogrammetry is a Phase I action and is named as such in Volume 2.
