import os
import sys
import math
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bbox import BoundingBox


class TestBoundingBox(unittest.TestCase):
    def test_from_points_bounds(self):
        bbox = BoundingBox.from_points([[0., 0., 0.], [1., 2., 3.], [-1., 5., 1.]])
        np.testing.assert_allclose(bbox.get_lower_bound(), [-1., 0., 0.])
        np.testing.assert_allclose(bbox.get_upper_bound(), [1., 5., 3.])

    def test_from_2d_points(self):
        bbox = BoundingBox.from_points([[10., 20.], [5., 40.], [30., 15.]])
        np.testing.assert_allclose(bbox.get_lower_bound(), [5., 15.])
        np.testing.assert_allclose(bbox.get_upper_bound(), [30., 40.])

    def test_empty_starts_inverted(self):
        bbox = BoundingBox.empty(3)
        self.assertTrue(np.all(np.isinf(bbox.get_lower_bound())))
        self.assertTrue(np.all(np.isinf(bbox.get_upper_bound())))

    def test_include_point_expands(self):
        bbox = BoundingBox.empty(3)
        bbox.include_point([1., 1., 1.])
        bbox.include_point([-2., 3., 0.])
        np.testing.assert_allclose(bbox.get_lower_bound(), [-2., 1., 0.])
        np.testing.assert_allclose(bbox.get_upper_bound(), [1., 3., 1.])

    def test_include_bbox_merges(self):
        a = BoundingBox.from_points([[0., 0., 0.], [2., 2., 2.]])
        b = BoundingBox.from_points([[-1., 1., 1.], [3., 1., 1.]])
        a.include_bbox(b)
        np.testing.assert_allclose(a.get_lower_bound(), [-1., 0., 0.])
        np.testing.assert_allclose(a.get_upper_bound(), [3., 2., 2.])


if __name__ == "__main__":
    unittest.main()
