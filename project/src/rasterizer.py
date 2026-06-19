import numpy as np

from framebuffer import FrameBuffer
from camera import Camera
from triangle import Triangle
from bbox import BoundingBox
from obj_loader import load_obj

CAMERA_OFFSET = np.array([0., 0., -5.])
FOV = 60.
PALETTE = [(255, 0, 0), (255, 255, 0)]
def compute_barycentric_coords(triangle: Triangle, hit_point: np.ndarray) -> tuple:
    p0, p1, p2 = triangle.get_points()
    double_area = triangle.get_area() * 2.

    base_vec_1 = p1 - p0
    base_vec_2 = p2 - p0

    p0_to_hit_point = hit_point - p0
    u = np.linalg.norm(np.cross(p0_to_hit_point, base_vec_1)) / double_area
    v = np.linalg.norm(np.cross(base_vec_2, p0_to_hit_point)) / double_area
    w = 1. - u - v

    return u, v, w

def compute_depth(bary_coords: tuple, depths: tuple) -> float:
    z0, z1, z2 = depths
    u, v, w = bary_coords
    inv_z = u / z0 + v / z1 + w / z2
    return 1 / inv_z

def draw_triangle(
        frame_buffer: FrameBuffer, 
        triangle: Triangle,
        depth_buffer: np.ndarray,
        color: tuple,
        depth_coefs: tuple,) -> None:

    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            hit_point = np.array([x, y, 0])
            if triangle.edge_function(hit_point):
                bary_coords = compute_barycentric_coords(triangle, hit_point)
                depth = compute_depth(bary_coords, depth_coefs)
                if depth < depth_buffer[y, x]:
                    depth_buffer[y, x] = depth
                    frame_buffer.set_pixel(y, x, color)

def render_model(frame_buffer: FrameBuffer, color: tuple, path: str) -> None:
    depth_buffer = np.full(
        (frame_buffer.get_height(), frame_buffer.get_width()), 
        np.inf, 
        dtype=float
    )
    camera = Camera()
    vertices, triangles = load_obj(path)
    vertices += CAMERA_OFFSET

    for ti, tri_indices in enumerate(triangles):
        v0, v1, v2 = vertices[tri_indices[0]], vertices[tri_indices[1]], vertices[tri_indices[2]]
                
        # check if the object is behind the camera
        if v0[2] >= 0 or v1[2] >= 0 or v2[2] >= 0:
            continue

        px0, py0, z0 = camera.project_point(v0, FOV)
        px1, py1, z1 = camera.project_point(v1, FOV)
        px2, py2, z2 = camera.project_point(v2, FOV)
        color = PALETTE[ti % len(PALETTE)]

        triangle = Triangle((px0, py0, 0.), (px1, py1, 0.), (px2, py2, 0.))
        draw_triangle(frame_buffer, triangle, depth_buffer, color, depth_coefs=(z0, z1, z2))