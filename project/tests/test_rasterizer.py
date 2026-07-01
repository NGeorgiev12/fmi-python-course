import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triangle import Triangle
from rasterizer import compute_barycentric_coords, compute_depth


class TestBarycentricCoords(unittest.TestCase):
    def setUp(self):
        self.tri = Triangle((0., 0., 0.), (1., 0., 0.), (0., 1., 0.))

    def test_centroid_is_thirds(self):
        w0, w1, w2 = compute_barycentric_coords(self.tri, np.array([1 / 3, 1 / 3, 0.]))
        self.assertAlmostEqual(w0, 1 / 3)
        self.assertAlmostEqual(w1, 1 / 3)
        self.assertAlmostEqual(w2, 1 / 3)

    def test_weights_sum_to_one(self):
        for pt in ([0.2, 0.3, 0.], [0.1, 0.1, 0.], [0.5, 0.25, 0.]):
            w0, w1, w2 = compute_barycentric_coords(self.tri, np.array(pt))
            self.assertAlmostEqual(w0 + w1 + w2, 1.0)

    def test_vertex_p0_gives_weight_one_at_slot0(self):
        # ordering guard: weight of p0 must land in the first slot
        w0, w1, w2 = compute_barycentric_coords(self.tri, np.array([0., 0., 0.]))
        self.assertAlmostEqual(w0, 1.0)
        self.assertAlmostEqual(w1, 0.0)
        self.assertAlmostEqual(w2, 0.0)

    def test_vertex_p1_gives_weight_one_at_slot1(self):
        w0, w1, w2 = compute_barycentric_coords(self.tri, np.array([1., 0., 0.]))
        self.assertAlmostEqual(w0, 0.0)
        self.assertAlmostEqual(w1, 1.0)
        self.assertAlmostEqual(w2, 0.0)

    def test_vertex_p2_gives_weight_one_at_slot2(self):
        w0, w1, w2 = compute_barycentric_coords(self.tri, np.array([0., 1., 0.]))
        self.assertAlmostEqual(w0, 0.0)
        self.assertAlmostEqual(w1, 0.0)
        self.assertAlmostEqual(w2, 1.0)


class TestComputeDepth(unittest.TestCase):
    def test_equal_depths_return_that_depth(self):
        depth = compute_depth((1 / 3, 1 / 3, 1 / 3), (4., 4., 4.))
        self.assertAlmostEqual(depth, 4.0)

    def test_at_vertex_returns_that_vertex_depth(self):
        # weight fully on the third vertex -> its depth
        self.assertAlmostEqual(compute_depth((0., 0., 1.), (2., 5., 8.)), 8.0)
        self.assertAlmostEqual(compute_depth((1., 0., 0.), (2., 5., 8.)), 2.0)

    def test_perspective_correct_midpoint(self):
        # halfway (in screen space) between depth 2 and 6 is NOT 4 (linear),
        # it is the harmonic-style 1/z interpolation -> 3.0
        depth = compute_depth((0.5, 0.5, 0.), (2., 6., 999.))
        self.assertAlmostEqual(depth, 3.0)


if __name__ == "__main__":
    unittest.main()
