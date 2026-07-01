import os
import sys
import math
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from transforms import (
    rotation_x, rotation_y, rotation_z, translation, scaling,
    look_at, transform_points, transform_directions,
)

I4 = np.eye(4)


class TestRotations(unittest.TestCase):
    def test_zero_angle_is_identity(self):
        for rot in (rotation_x, rotation_y, rotation_z):
            np.testing.assert_allclose(rot(0.0), I4, atol=1e-12)

    def test_full_turn_is_identity(self):
        for rot in (rotation_x, rotation_y, rotation_z):
            np.testing.assert_allclose(rot(2 * math.pi), I4, atol=1e-9)

    def test_rotation_z_ninety_maps_x_to_y(self):
        p = transform_points(rotation_z(math.radians(90)), np.array([[1., 0., 0.]]))
        np.testing.assert_allclose(p[0], [0., 1., 0.], atol=1e-9)

    def test_rotation_y_ninety_maps_x_to_minus_z(self):
        p = transform_points(rotation_y(math.radians(90)), np.array([[1., 0., 0.]]))
        np.testing.assert_allclose(p[0], [0., 0., -1.], atol=1e-9)

    def test_two_opposite_rotations_cancel(self):
        m = rotation_x(math.radians(37)) @ rotation_x(math.radians(-37))
        np.testing.assert_allclose(m, I4, atol=1e-9)


class TestTranslationScaling(unittest.TestCase):
    def test_translation_moves_point(self):
        p = transform_points(translation(2., -3., 5.), np.array([[1., 1., 1.]]))
        np.testing.assert_allclose(p[0], [3., -2., 6.])

    def test_scaling_scales_point(self):
        p = transform_points(scaling(2., 3., 4.), np.array([[1., 1., 1.]]))
        np.testing.assert_allclose(p[0], [2., 3., 4.])

    def test_translation_does_not_move_directions(self):
        d = transform_directions(translation(9., 9., 9.), np.array([[1., 0., 0.]]))
        np.testing.assert_allclose(d[0], [1., 0., 0.], atol=1e-12)


class TestLookAt(unittest.TestCase):
    def setUp(self):
        self.view = look_at(
            np.array([0., 0., 5.]), np.array([0., 0., 0.]), np.array([0., 1., 0.])
        )

    def test_eye_maps_to_origin(self):
        p = transform_points(self.view, np.array([[0., 0., 5.]]))
        np.testing.assert_allclose(p[0], [0., 0., 0.], atol=1e-9)

    def test_origin_maps_in_front_of_camera(self):
        # camera at z=5 looking at origin -> origin sits at z=-5 in camera space
        p = transform_points(self.view, np.array([[0., 0., 0.]]))
        np.testing.assert_allclose(p[0], [0., 0., -5.], atol=1e-9)

    def test_on_axis_camera_matches_plain_offset(self):
        # this view is exactly the old CAMERA_OFFSET = [0,0,-5]
        pts = np.array([[1., 2., 3.], [-4., 0., 1.]])
        np.testing.assert_allclose(
            transform_points(self.view, pts), pts + np.array([0., 0., -5.]), atol=1e-9
        )


class TestTransformDirections(unittest.TestCase):
    def test_pure_rotation_matches_point_transform(self):
        m = rotation_y(math.radians(90))
        d = transform_directions(m, np.array([[1., 0., 0.]]))
        p = transform_points(m, np.array([[1., 0., 0.]]))
        np.testing.assert_allclose(d[0], p[0], atol=1e-9)


if __name__ == "__main__":
    unittest.main()
