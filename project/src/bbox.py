import math

import numpy as np

from triangle import Triangle

class BoundingBox:

    def __init__(self, lower_bound: tuple[int], upper_bound: tuple[int]):
        self._lower_bound = np.array(lower_bound, dtype=float)
        self._upper_bound = np.array(upper_bound, dtype=float)

    @classmethod
    def empty(cls, dim: int = 3) -> "BoundingBox":
        return cls(np.full(dim, math.inf), np.full(dim, -math.inf))

    @classmethod
    def from_points(cls, points) -> "BoundingBox":
        points = np.asarray(points, dtype=float)
        return cls(points.min(axis=0), points.max(axis=0))
    
    def get_lower_bound(self) -> np.ndarray:
        return self._lower_bound
    
    def get_upper_bound(self) -> np.ndarray:
        return self._upper_bound
    
    def include_point(self, point) -> None:
        point = np.array(point)
        self._lower_bound = np.minimum(self._lower_bound, point)
        self._upper_bound = np.maximum(self._upper_bound, point)

    def include_triangle(self, triangle) -> None:
        for vertex in triangle.get_points():
            self.include_point(vertex)

    def include_bbox(self, bbox) -> None:
        self.include_point(bbox.get_lower_bound())
        self.include_point(bbox.get_upper_bound())

