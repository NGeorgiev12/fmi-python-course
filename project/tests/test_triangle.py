import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from triangle import Triangle
from exceptions.CollinearTriangleBaseVectorsException import CollinearTriangleBaseVectorsException


class TestTriangle(unittest.TestCase):
    def setUp(self):
        # right triangle in the z=0 plane, area 0.5, outward normal +z
        self.tri = Triangle((0., 0., 0.), (1., 0., 0.), (0., 1., 0.))

    def test_area_of_right_triangle(self):
        self.assertAlmostEqual(self.tri.get_area(), 0.5)

    def test_area_scales_with_size(self):
        big = Triangle((0., 0., 0.), (2., 0., 0.), (0., 2., 0.))
        self.assertAlmostEqual(big.get_area(), 2.0)

    def test_normal_is_unit_length(self):
        n = self.tri.get_normal_vec()
        self.assertAlmostEqual(np.linalg.norm(n), 1.0)

    def test_normal_direction(self):
        # winding (0,0,0)->(1,0,0)->(0,1,0) gives +z by right-hand rule
        np.testing.assert_allclose(self.tri.get_normal_vec(), [0., 0., 1.], atol=1e-9)

    def test_get_points_returns_three_vertices(self):
        p0, p1, p2 = self.tri.get_points()
        np.testing.assert_array_equal(p0, [0., 0., 0.])
        np.testing.assert_array_equal(p1, [1., 0., 0.])
        np.testing.assert_array_equal(p2, [0., 1., 0.])

    def test_centroid_is_inside(self):
        self.assertTrue(self.tri.edge_function((1 / 3, 1 / 3, 0.)))

    def test_vertex_is_inside(self):
        # a vertex lies on two edges -> counted as inside (epsilon tolerance)
        self.assertTrue(self.tri.edge_function((0., 0., 0.)))

    def test_point_on_edge_is_inside(self):
        self.assertTrue(self.tri.edge_function((0.5, 0., 0.)))

    def test_point_outside_is_outside(self):
        self.assertFalse(self.tri.edge_function((1., 1., 0.)))
        self.assertFalse(self.tri.edge_function((-0.5, -0.5, 0.)))

    def test_collinear_vertices_raise(self):
        with self.assertRaises(CollinearTriangleBaseVectorsException):
            Triangle((0., 0., 0.), (1., 1., 1.), (2., 2., 2.))

    def test_degenerate_duplicate_vertices_raise(self):
        with self.assertRaises(CollinearTriangleBaseVectorsException):
            Triangle((0., 0., 0.), (0., 0., 0.), (1., 0., 0.))


if __name__ == "__main__":
    unittest.main()
