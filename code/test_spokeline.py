# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — the tests that run before any number is produced (EVIDENCE_PACK.md).

Stdlib only. A failing test stops reproduce.sh before the scored run.
"""
import os, sys, random, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "spokeline", "src"))
import aas as A, geometry as G, scenario as S, checks as C, inject as I

CORPUS = os.path.join(HERE, "spokeline", "corpus", "s1000d")


class SpokelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aas = A.extract(CORPUS)
        cls.scn = S.build(cls.aas, G.TRUE_BINDING)

    def test_corpus_shape(self):
        a = self.aas
        self.assertEqual(len(a["sources"]), 4)
        self.assertEqual(len(a["parts"]), 13)
        self.assertEqual(len(a["joints"]), 9)
        self.assertEqual(len(a["steps"]), 6)
        self.assertEqual(len(a["constraints"]), 7)
        self.assertEqual(len(a["markings"]), len(a["sources"]))

    def test_clean_binding_has_no_failure(self):
        f = C.run_all(self.aas, G.TRUE_BINDING, self.scn)
        self.assertEqual(C.failures(f), [])
        self.assertEqual(len(f) - len(C.failures(f)), 2)   # the two legitimate advisories

    def test_every_part_bound_to_a_list(self):
        for pid in self.aas["parts"]:
            self.assertTrue(G.segs_of(G.TRUE_BINDING, pid), pid)

    def test_deterministic_classes_are_detected(self):
        # F3 to F6 detect at 50/50 in the scored run; one fixed-seed trial each must fail.
        rng = random.Random(1)
        for name, fn in I.CLASSES:
            if name[:2] not in ("F3", "F4", "F5", "F6"):
                continue
            b2, s2, desc, expect = fn(self.aas, G.TRUE_BINDING, self.scn, rng)
            self.assertTrue(C.failures(C.run_all(self.aas, b2, s2)), name)

    def test_gltf_export_builds(self):
        import export_gltf as E
        g = E.build(self.aas, G.TRUE_BINDING, self.scn)
        self.assertEqual(len(g["nodes"]), 13)
        self.assertEqual(len(g["animations"]), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
