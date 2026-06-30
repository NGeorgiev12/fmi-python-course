import numpy as np

from exceptions.CollinearTriangleBaseVectorsException import CollinearTriangleBaseVectorsException
EPSILON = 1e-6

class Triangle:
    """
    A triangle defined by three vertices in 2D or 3D space.
    On construction the triangle precomputes its normal vector and its
    area from two edge vectors via their cross product. It exposes a
    point-in-triangle test (``edge_function``) used by the rasterizer to
    decide which pixels a triangle covers.
    """

    def __init__(self, point0: tuple, point1: tuple, point2: tuple):
        """
        Build the triangle and precompute its normal and area.

        Args:
            point0, point1, point2: The three vertices, each a sequence of
                coordinates (tuple or array). Converted to numpy arrays internally.

        Raises:
            CollinearTriangleBaseVectorsException: If the three vertices are
                collinear (zero area) and therefore cannot form a triangle.
        """
        self._point0, self._point1, self._point2 = np.array(point0), np.array(point1), np.array(point2)
        v0 = self._point1 - self._point0
        v1 = self._point2 - self._point0
        self._normal_vec = np.cross(v0, v1)
        self._area = np.linalg.norm(self._normal_vec) / 2.0

        if np.allclose(self._area, 0.0):
            raise CollinearTriangleBaseVectorsException(
                "Can't construct a triangle with two collinear base vectors."
            )
        
    def get_area(self) -> float:
        """Return the area of the triangle."""
        return self._area
    
    def get_normal_vec(self) -> np.ndarray:
        """Return the unit (normalized) normal vector of the triangle's plane."""
        return self._normal_vec / np.linalg.norm(self._normal_vec)
    
    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return tuple of the triangle points""" 
        return self._point0, self._point1, self._point2
    
    def edge_function(self, point) -> bool:
        """
        Test whether a point lies inside the triangle.

        Uses the inside-outside test: for each edge, the cross product of the
        edge vector with the vector from the edge's start vertex to ``point``
        must point in the same direction as the triangle normal (non-negative
        dot product). A small epsilon tolerance keeps points lying exactly on
        an edge classified as inside.

        Args:
             point: The point to test, as a sequence of coordinates matching the
                vertices' dimensionality.

        Returns: True if the point is inside or on an edge of the triangle, else False.
        """
        point = np.array(point, dtype=float)
        edge0 = self._point1 - self._point0
        edge1 = self._point2 - self._point1
        edge2 = self._point0 - self._point2

        point_edge0_vec = point - self._point0
        point_edge1_vec = point - self._point1
        point_edge2_vec = point - self._point2

        checkE0 = np.dot(self._normal_vec, np.cross(edge0, point_edge0_vec)) >= -EPSILON
        checkE1 = np.dot(self._normal_vec, np.cross(edge1, point_edge1_vec)) >= -EPSILON
        checkE2 = np.dot(self._normal_vec, np.cross(edge2, point_edge2_vec)) >= -EPSILON

        return checkE0 and checkE1 and checkE2 
    