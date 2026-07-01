import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from obj_loader import load_obj


def write_obj(text):
    fd, path = tempfile.mkstemp(suffix=".obj")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return path


class TestObjLoader(unittest.TestCase):
    def tearDown(self):
        # clean any temp files created per-test
        for p in getattr(self, "_paths", []):
            try:
                os.remove(p)
            except OSError:
                pass

    def _load(self, text):
        path = write_obj(text)
        self._paths = getattr(self, "_paths", []) + [path]
        return load_obj(path)

    def test_reads_vertices(self):
        v, _ = self._load("v 1 2 3\nv 4 5 6\nv 7 8 9\nf 1 2 3\n")
        np.testing.assert_allclose(v, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_face_is_zero_based(self):
        # file indices are 1-based -> become 0-based
        _, t = self._load("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        np.testing.assert_array_equal(t, [[0, 1, 2]])

    def test_quad_is_fan_triangulated(self):
        _, t = self._load(
            "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nf 1 2 3 4\n"
        )
        np.testing.assert_array_equal(t, [[0, 1, 2], [0, 2, 3]])

    def test_ngon_fan_triangulation(self):
        # a pentagon -> 3 triangles sharing vertex 0
        _, t = self._load(
            "v 0 0 0\nv 1 0 0\nv 2 1 0\nv 1 2 0\nv 0 1 0\nf 1 2 3 4 5\n"
        )
        np.testing.assert_array_equal(t, [[0, 1, 2], [0, 2, 3], [0, 3, 4]])

    def test_face_with_slashes(self):
        # v/vt/vn form: only the vertex index is used
        _, t = self._load(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1/1/1 2/2/2 3/3/3\n"
        )
        np.testing.assert_array_equal(t, [[0, 1, 2]])

    def test_negative_indices_are_relative(self):
        # -1 refers to the last vertex, etc.
        _, t = self._load("v 0 0 0\nv 1 0 0\nv 0 1 0\nf -3 -2 -1\n")
        np.testing.assert_array_equal(t, [[0, 1, 2]])

    def test_comments_and_blank_lines_ignored(self):
        v, t = self._load(
            "# a comment\n\nv 0 0 0\n\n# another\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        )
        self.assertEqual(len(v), 3)
        np.testing.assert_array_equal(t, [[0, 1, 2]])


if __name__ == "__main__":
    unittest.main()
