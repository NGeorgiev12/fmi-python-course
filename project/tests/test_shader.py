import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shader import compute_lighting, compute_vertex_normals
from scene_parser import Material


def make_material(base=(200, 0, 200), shininess=32.0, specular=(255, 255, 255)):
    return Material(base_color=base, shininess=shininess, specular_color=specular)


class TestComputeVertexNormals(unittest.TestCase):
    def setUp(self):
        # a tetrahedron centred near the origin
        self.vertices = np.array([
            [1., 1., 1.],
            [-1., -1., 1.],
            [-1., 1., -1.],
            [1., -1., -1.],
        ])
        self.triangles = np.array([
            [0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2],
        ])

    def test_output_shape(self):
        n = compute_vertex_normals(self.vertices, self.triangles)
        self.assertEqual(n.shape, self.vertices.shape)

    def test_normals_are_unit_length(self):
        n = compute_vertex_normals(self.vertices, self.triangles)
        np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0, atol=1e-9)

    def test_normals_point_outward(self):
        # after outward-orientation, each normal should agree with the
        # direction from the mesh centre to the vertex
        n = compute_vertex_normals(self.vertices, self.triangles)
        center = self.vertices.mean(axis=0)
        outward = self.vertices - center
        dots = np.sum(n * outward, axis=1)
        self.assertTrue(np.all(dots >= -1e-9))


class TestComputeLighting(unittest.TestCase):
    def test_dark_side_is_base_times_ambient(self):
        # normal faces away from the light -> only ambient term
        mat = make_material(base=(200, 0, 200))
        color = compute_lighting(
            np.array([0., 0., 1.]), np.array([0., 0., -1.]), mat, ambient=0.15
        )
        self.assertEqual(color, (30, 0, 30))  # int(200*0.15)=30, int(0)=0

    def test_lit_side_brighter_than_dark_side(self):
        mat = make_material()
        lit = compute_lighting(
            np.array([0., 0., 1.]), np.array([0.2, 0.2, 1.]), mat, ambient=0.15
        )
        dark = compute_lighting(
            np.array([0., 0., 1.]), np.array([0., 0., -1.]), mat, ambient=0.15
        )
        self.assertGreater(sum(lit), sum(dark))

    def test_result_is_clamped_to_255(self):
        mat = make_material(base=(255, 255, 255))
        color = compute_lighting(
            np.array([0., 0., 1.]), np.array([0., 0., 1.]), mat, ambient=0.15
        )
        self.assertTrue(all(0 <= c <= 255 for c in color))
        self.assertEqual(color, (255, 255, 255))

    def test_returns_integer_tuple(self):
        mat = make_material()
        color = compute_lighting(
            np.array([0., 0., 1.]), np.array([0., 1., 1.]), mat, ambient=0.15
        )
        self.assertIsInstance(color, tuple)
        self.assertTrue(all(isinstance(c, int) for c in color))

    def test_normalization_independent_of_input_length(self):
        # normal / light length should not matter (both get normalised)
        mat = make_material()
        a = compute_lighting(np.array([0., 0., 2.]), np.array([0., 0., 3.]), mat)
        b = compute_lighting(np.array([0., 0., 1.]), np.array([0., 0., 1.]), mat)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
