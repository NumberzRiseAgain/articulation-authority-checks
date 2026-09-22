#!/usr/bin/env bash
# SPOKELINE — regenerate every number quoted in Volume 2 §5.1 in one command.
# Stdlib Python only. No network, no GPU, no install step. Seed 20260902 is fixed in run.py.
# Run through 08_Templates_and_Styleguides/scripts/evidence_pack.sh, which logs and hashes it.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
A="$(dirname "$HERE")"
cd "$HERE"
echo "--- tests first"
python3 -m unittest -v test_spokeline
echo "--- surrogate corpus (deterministic; identical bytes on every run)"
python3 spokeline/src/make_corpus.py
echo "--- scored run"
python3 spokeline/src/run.py
echo "--- glTF export"
python3 spokeline/src/export_gltf.py
echo "--- viewer page (self-contained HTML over runs/latest; the seven checks ported to JS)"
python3 spokeline/src/build_viewer.py
echo "--- copy results to 08_Analysis/results and write the manifest"
mkdir -p "$A/results"
cp spokeline/runs/latest/metrics.json "$A/results/spokeline_metrics.json"
cp spokeline/runs/latest/ledger.json  "$A/results/spokeline_ledger.json"
cp spokeline/runs/latest/spokeline_front_wheel.gltf "$A/results/spokeline_front_wheel.gltf"
python3 manifest.py
echo "--- done"
