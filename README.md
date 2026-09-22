# 08_Analysis — SPOKELINE, the NV071 proof point

**What the study does.** Given an Articulation Authority Set extracted from four surrogate
S1000D Issue 4.2 data modules (front-wheel removal on a bicycle, Model Ident Code SPOKE1,
fictional) and a proposed binding of that authority to geometry, it injects six classes of
generator fault, fifty trials each under seed 20260902, and counts how often seven
deterministic checks catch the wrong motion. Fifty runs on the unmodified scenario are the
false-positive control. Every figure quoted in Volume 2 §5.1 is written by `spokeline/src/run.py`.

**What it does not model.** Capture, segmentation and reconstruction: the geometry is a
parametric stand-in (boxes), so no claim about photogrammetry accuracy follows from it. The
technical data is surrogate and no Navy data is used. The pre-registration
(`code/spokeline/runs/PREREGISTRATION.md`) is internal, not deposited externally.

## Run it

```bash
08_Templates_and_Styleguides/scripts/evidence_pack.sh 2026-09_SBIR_September/DON26BZ05-NV071_3D_TRAINING
```

That runs `code/reproduce.sh` (tests first, then corpus, scored run, glTF export, manifest),
tees to `logs/run_<UTC>.log`, hashes `results/*.json` into `results/_result_digests.txt` and
appends a row to `RUN_RECORD.md`. Stdlib Python only; under a second of compute.

## Folder

| Path | What it is |
|---|---|
| `code/reproduce.sh` | one command, every number |
| `code/test_spokeline.py` | runs first; corpus shape, clean control, deterministic classes, glTF build |
| `code/manifest.py` | writes `results/manifest.json` (run identifier from source digests + seed) |
| `code/spokeline/src/` | the pipeline: `aas.py` extract, `geometry.py`, `scenario.py`, `checks.py` (C1–C7), `inject.py` (F1–F6), `run.py`, `export_gltf.py`, `build_viewer.py` |
| `code/spokeline/corpus/s1000d/` | the four surrogate data modules, regenerated identically by `make_corpus.py` |
| `code/spokeline/runs/PREREGISTRATION.md` | protocol fixed before the scored run |
| `results/spokeline_metrics.json` | every figure quoted anywhere (copy of `runs/latest/metrics.json`) |
| `results/spokeline_ledger.json` | authority set, scenario, binding, findings |
| `results/spokeline_front_wheel.gltf` | glTF 2.0, 13 nodes, 6 animations |
| `results/manifest.json`, `results/_result_digests.txt` | identity and hashes of the run |
| `results/RESULTS.md` | the narrative and the residual analysis |
| `logs/`, `RUN_RECORD.md` | one log and one row per execution |
| `POC_SPEC.md` | design and scope, written before any code |

## Known gaps, 5 September 2026

- `export_gltf.py` was broken by the 3 September C1 rewrite (binding became part → list of
  segments) and raised `TypeError`; patched 5 September to read the first bound segment. The
  exported glTF is byte-identical to the 3 September file.
- ~~`build_viewer.py` is not in `reproduce.sh`; the JS port of C1 predates the 3 Sep
  coverage-and-identity rewrite.~~ **Closed 12 September.** `src/viewer_app.js` C1 now
  matches `checks.py` (every actionable part to one or more segments, each segment to
  exactly one part, unclaimed geometry must be declared non-actionable, union-AABB
  containment in the parent); the payload carries `non_actionable`. `reproduce.sh` runs
  `build_viewer.py` after the glTF export and the manifest hashes the page. The page also
  gained a proper document head (`<!doctype html>`, `<meta charset="utf-8">`): the 3 Sep
  file had none and showed mojibake when opened as a file. Verified headless: clean run
  gives the two C3 advisories only; F1 (SPK-1200 for SPK-1400) gives the same three C1
  messages and the C5 as the Python run. Screenshot in `06_Evidence/`. Run of record
  moved to `002125890a0861f8` (12 Sep, row 2 of `RUN_RECORD.md`), then to
  `b416e5443392f08b` (row 3) when every source file gained a rights header;
  290/300 and 0/50 reproduced exactly both times, ledger digest unchanged.
- **Rights headers, 12 September.** All 11 source files open with three comment lines
  naming Numberz.ai Inc., Raghu Venkat (PI) and Dr. Tricha Anjali, the topic, company
  funding and the SBIR data-rights assertion under DFARS 252.227-7018. Comments only;
  no check, generator or threshold moved, and the metrics are identical.
- Wall clock is machine-dependent (0.2 s on 2 Sep, 0.26 s in the 5 Sep VM run); the volume
  says "under a second" rather than quoting one machine's figure.

## Repository

Public copy of the `08_Analysis/` evidence pack behind the SPOKELINE submission to DON26BZ05-NV071, released 19 September 2026 by Numberz.ai Inc. under the MIT License (`LICENSE`). The study was company-funded; no Government funding. The four S1000D modules under `code/spokeline/corpus/` are surrogates authored by Numberz.ai for this study and are included. No Government technical data is used. Run identifiers are the first 16 hex digits of a SHA-256 over the source digests, so the tree as committed reproduces the identifier in `results/manifest.json`; `RUN_RECORD.md` lists every run, including the ones that failed. Cite with `CITATION.cff`. The other packs from the same month are listed at https://github.com/NumberzRiseAgain/september-2026-evidence-packs. One identifier note: the run of record through 19 September 2026 15:14 UTC was `b416e5443392f08b`, which is the value the README above and the pursuit's evidence note quote; replacing the proposal-time header line in the sources with the licence line on 19 September moved the identifier to `346e4b8c6d419337` (the ledger and every result digest unchanged). `RUN_RECORD.md` carries both runs.
