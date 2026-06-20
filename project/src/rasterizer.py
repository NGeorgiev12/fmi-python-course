import numpy as np

from framebuffer import FrameBuffer
from camera import project_point
from triangle import Triangle
from bbox import BoundingBox
from obj_loader import load_obj
from shader import compute_diffuse, compute_vertex_normals
from constants import EPSILON

CAMERA_OFFSET = np.array([0., 0., -5.])
FOV = 60.
LIGHT_DIR = np.array([0.6, 0.8, 1.0])   # горе-дясно-отпред; +z осветява челните стени
BASE_COLOR = (200, 200, 0)
AMBIENT = 0.15

def compute_barycentric_coords(triangle: Triangle, hit_point: np.ndarray) -> tuple:
    p0, p1, p2 = triangle.get_points()
    double_area = triangle.get_area() * 2.

    w0 = np.linalg.norm(np.cross(p1 - hit_point, p2 - hit_point)) / double_area
    w1 = np.linalg.norm(np.cross(p2 - hit_point, p0 - hit_point)) / double_area
    w2 = 1. - w0 - w1   

    return w0, w1, w2

def compute_depth(bary_coords: tuple, depths: tuple) -> float:
    z0, z1, z2 = depths
    u, v, w = bary_coords
    inv_z = u / z0 + v / z1 + w / z2
    return 1 / inv_z

def draw_triangle(
        frame_buffer: FrameBuffer, 
        triangle: Triangle,
        vertex_normals: tuple,
        depth_buffer: np.ndarray,
        depth_coefs: tuple) -> None:

    n0, n1, n2 = vertex_normals
    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            hit_point = np.array([x, y, 0])
            if triangle.edge_function(hit_point):
                w0, w1, w2 = compute_barycentric_coords(triangle, hit_point)
                depth = compute_depth((w0, w1, w2), depth_coefs)
                if depth < depth_buffer[y, x]:
                    depth_buffer[y, x] = depth
                    normal = w0 * n0 + w1 * n1 + w2 * n2
                    normal /= np.linalg.norm(normal)
                    color = compute_diffuse(normal, LIGHT_DIR, BASE_COLOR, AMBIENT)
                    frame_buffer.set_pixel(y, x, color)

def render_model(frame_buffer: FrameBuffer, path: str) -> None:
    depth_buffer = np.full(
        (frame_buffer.get_height(), frame_buffer.get_width()), 
        np.inf, 
        dtype=float
    )
    vertices, triangles = load_obj(path)
    vertices_normals = compute_vertex_normals(vertices, triangles)
    vertices += CAMERA_OFFSET

    for tri_indices in triangles:
        v0, v1, v2 = vertices[tri_indices[0]], vertices[tri_indices[1]], vertices[tri_indices[2]]
                
        # check if the object is behind the camera
        if v0[2] >= -EPSILON or v1[2] >= -EPSILON or v2[2] >= -EPSILON:
            continue

        normal = Triangle(v0, v1, v2).get_normal_vec()
        centre_point = (v0 + v1 + v2) / 3.
        if np.dot(normal, -centre_point) < EPSILON:
            normal *= -1.
         
        color = compute_diffuse(normal, LIGHT_DIR, BASE_COLOR, AMBIENT)
        px0, py0, z0 = project_point(v0, FOV)
        px1, py1, z1 = project_point(v1, FOV)
        px2, py2, z2 = project_point(v2, FOV)
        vertex_normals = vertices_normals[tri_indices[0]], vertices_normals[tri_indices[1]], vertices_normals[tri_indices[2]]

        triangle = Triangle((px0, py0, 0.), (px1, py1, 0.), (px2, py2, 0.))
        draw_triangle(
            frame_buffer, 
            triangle,
            vertex_normals, 
            depth_buffer, 
            depth_coefs=(z0, z1, z2)
        )