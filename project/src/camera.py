import math


def project_point(point: tuple, fov_degrees: float, width: int, height: int) -> tuple:
    """Project a 3D camera-space point to 2D raster (pixel) coordinates.

    Applies a perspective projection: the point is divided by its depth so that
    distant points map closer to the image center, then converted from
    normalized device coordinates to pixels using the image dimensions. The
    camera sits at the origin looking down the -z axis, so points in front of
    the camera have z < 0.

    Args:
        point: A 3D point (x, y, z) in camera space.
        fov_degrees: The vertical field of view, in degrees.
        width: Image width in pixels (used for aspect ratio and pixel scale).
        height: Image height in pixels (used for aspect ratio and pixel scale).

    Returns:
        A tuple (px, py, depth): px and py are raster coordinates with the
        origin at the top-left corner and y increasing downward; depth is the
        positive distance in front of the camera (-z).
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