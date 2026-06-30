import math

def project_point(point: tuple, fov_degrees: float, width: int, height: int) -> tuple:
    """
    Project a 3D point from camera space to 2D raster (pixel) coordinates.

    Applies a perspective projection: the point is divided by its depth so that
    distant points map closer to the image center, then converted from
    normalized device coordinates to pixels using the image dimensions from
    config. The camera sits at the origin looking down the -z axis, so points
    in front of the camera have z < 0.

    Args:
        point: A 3D point (x, y, z) in camera space.
        fov_degrees: The vertical field of view, in degrees.

    Returns:
        A (px, py) tuple of raster coordinates, with the origin at the top-left
        corner and y increasing downward.
    """
    x, y, z = point
    aspect = width / height
    scale = math.tan(math.radians(fov_degrees) / 2.)

    z = -z
    ndc_x = (x / z) / (scale * aspect)
    ndc_y = (y / z) / scale

    px = (ndc_x + 1.0) * 0.5 * width
    py = (1.0 - ndc_y) * 0.5 * height

    return px, py, z