import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from camera import project_point

WIDTH, HEIGHT, FOV = 800, 600, 60.0


class TestProjectPoint(unittest.TestCase):
    def test_on_axis_point_projects_to_center(self):
        px, py, depth = project_point((0., 0., -5.), FOV, WIDTH, HEIGHT)
        self.assertAlmostEqual(px, WIDTH / 2)
        self.assertAlmostEqual(py, HEIGHT / 2)

    def test_returns_positive_depth(self):
        # camera looks down -z; a point at z=-5 has depth +5
        _, _, depth = project_point((0., 0., -5.), FOV, WIDTH, HEIGHT)
        self.assertAlmostEqual(depth, 5.0)

    def test_point_right_of_axis_projects_right_of_center(self):
        px, _, _ = project_point((1., 0., -5.), FOV, WIDTH, HEIGHT)
        self.assertGreater(px, WIDTH / 2)

    def test_point_above_axis_projects_above_center(self):
        # +y in world is up; screen y grows downward, so py < center
        _, py, _ = project_point((0., 1., -5.), FOV, WIDTH, HEIGHT)
        self.assertLess(py, HEIGHT / 2)

    def test_farther_point_projects_closer_to_center(self):
        near_px, _, _ = project_point((1., 0., -5.), FOV, WIDTH, HEIGHT)
        far_px, _, _ = project_point((1., 0., -10.), FOV, WIDTH, HEIGHT)
        # the farther point is less displaced from the center
        self.assertLess(abs(far_px - WIDTH / 2), abs(near_px - WIDTH / 2))


if __name__ == "__main__":
    unittest.main()
