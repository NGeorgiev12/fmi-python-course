import math
from typing import Self

import numpy as np


class BoundingBox:
    """An axis-aligned bounding box in 2D or 3D.

    Stored as a lower-bound and an upper-bound corner. Used by the rasterizer
    to find the pixel rectangle a projected triangle can cover, so that only
    those pixels are tested for coverage.
    """

    def __init__(self, lower_bound: tuple[int], upper_bound: tuple[int]):
        """Build a box from its two extreme corners.

        Args:
            lower_bound: The minimum coordinate along each axis.
            upper_bound: The maximum coordinate along each axis.
        """
        self._lower_bound = np.array(lower_bound, dtype=float)
        self._upper_bound = np.array(upper_bound, dtype=float)

    @classmethod
    def empty(cls, dim: int = 3) -> "BoundingBox":
        """Create an inverted, empty box that expands on the first insertion.

        Lower bounds start at +inf and upper bounds at -inf, so that the first
        :meth:`include_point` (or :meth:`include_bbox`) sets the real extents.

        Args:
            dim: Number of dimensions (2 or 3).

        Returns:
            An empty BoundingBox ready to accumulate points.
        """
        return cls(np.full(dim, math.inf), np.full(dim, -math.inf))

    @classmethod
    def from_points(cls, points) -> Self:
        """Build the tight box enclosing a set of points.

        Args:
            points: An (N, D) array-like of coordinates.

        Returns:
            The smallest axis-aligned box containing every point.
        """
        points = np.asarray(points, dtype=float)
        return cls(points.min(axis=0), points.max(axis=0))

    def get_lower_bound(self) -> np.ndarray:
        """Return the lower-bound (minimum) corner."""
        return self._lower_bound

    def get_upper_bound(self) -> np.ndarray:
        """Return the upper-bound (maximum) corner."""
        return self._upper_bound

    def include_point(self, point) -> None:
        """Grow the box in place so it also contains ``point``.

        Args:
            point: A coordinate to enclose.
        """
        point = np.array(point)
        self._lower_bound = np.minimum(self._lower_bound, point)
        self._upper_bound = np.maximum(self._upper_bound, point)

    def include_triangle(self, triangle) -> None:
        """Grow the box in place to contain all vertices of a triangle.

        Args:
            triangle: An object exposing ``get_points()`` -> its vertices.
        """
        for vertex in triangle.get_points():
            self.include_point(vertex)

    def include_bbox(self, bbox) -> None:
        """Grow the box in place to contain another bounding box.

        Args:
            bbox: The BoundingBox to merge into this one.
        """
        self.include_point(bbox.get_lower_bound())
        self.include_point(bbox.get_upper_bound())