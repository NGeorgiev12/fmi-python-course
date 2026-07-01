import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from framebuffer import FrameBuffer


class TestFrameBuffer(unittest.TestCase):
    def test_dimensions(self):
        fb = FrameBuffer(height=4, width=6)
        self.assertEqual(fb.get_height(), 4)
        self.assertEqual(fb.get_width(), 6)

    def test_pixels_shape_is_h_w_3(self):
        fb = FrameBuffer(height=4, width=6)
        self.assertEqual(fb.get_pixels().shape, (4, 6, 3))

    def test_default_background_is_black(self):
        fb = FrameBuffer(height=2, width=2)
        self.assertTrue(np.all(fb.get_pixels() == 0))

    def test_custom_background(self):
        fb = FrameBuffer(height=2, width=2, background=(10, 20, 30))
        np.testing.assert_array_equal(fb.get_pixel(0, 0), [10, 20, 30])
        np.testing.assert_array_equal(fb.get_pixel(1, 1), [10, 20, 30])

    def test_set_and_get_pixel_roundtrip(self):
        fb = FrameBuffer(height=4, width=6)
        fb.set_pixel(1, 2, (255, 128, 64))
        np.testing.assert_array_equal(fb.get_pixel(1, 2), [255, 128, 64])

    def test_set_pixel_indexes_row_then_column(self):
        # set_pixel(y, x) must write at [y][x], not [x][y]
        fb = FrameBuffer(height=4, width=6)
        fb.set_pixel(3, 5, (1, 2, 3))  # valid only if [y=3][x=5]
        np.testing.assert_array_equal(fb.get_pixels()[3, 5], [1, 2, 3])

    def test_setting_one_pixel_leaves_others_black(self):
        fb = FrameBuffer(height=3, width=3)
        fb.set_pixel(0, 0, (255, 255, 255))
        self.assertTrue(np.all(fb.get_pixel(2, 2) == 0))


if __name__ == "__main__":
    unittest.main()
