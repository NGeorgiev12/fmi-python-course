import math

import numpy as np

from transforms import *
from framebuffer import FrameBuffer
from triangle import Triangle
from bbox import BoundingBox
from camera import project_point
from obj_loader import load_obj
from shader import compute_lighting, compute_vertex_normals
from constants import EPSILON

MODEL_MATRIX = (
    translation(0., 0., 0.)
    @ rotation_y(math.radians(35)) @ rotation_x(math.radians(28))
    @ scaling(1., 1., 1.)
)
EYE = np.array([0., 0., 5.])    
TARGET = np.array([0., 0., 0.])   
UP = np.array([0., 1., 0.])
VIEW_MATRIX = look_at(EYE, TARGET, UP)
FOV = 60.
LIGHT_DIR = np.array([0.6, 0.8, 1.0])
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
        depth_buffer: np.ndarray,
        depth_coefs: tuple,
        shading: str,
        color: tuple = None,
        vertex_normals: tuple = None) -> None:

    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x = min(int(upper[0]), frame_buffer.get_width() - 1)
    max_y = min(int(upper[1]), frame_buffer.get_height() - 1)

    if shading == "phong":
        n0, n1, n2 = vertex_normals

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            hit_point = np.array([x, y, 0])
            if triangle.edge_function(hit_point):
                w0, w1, w2 = compute_barycentric_coords(triangle, hit_point)
                depth = compute_depth((w0, w1, w2), depth_coefs)

                if depth < depth_buffer[y, x]:
                    depth_buffer[y, x] = depth

                    if shading == "flat":
                        pixel_color = color
                    else:
                        normal = w0 * n0 + w1 * n1 + w2 * n2
                        normal /= np.linalg.norm(normal)
                        pixel_color = compute_lighting(normal, LIGHT_DIR, BASE_COLOR, AMBIENT)
                    
                    frame_buffer.set_pixel(y, x, pixel_color)

def render_model(frame_buffer: FrameBuffer, path: str, shading: str = "flat") -> None:
    depth_buffer = np.full(
        (frame_buffer.get_height(), frame_buffer.get_width()),
        np.inf, 
        dtype=float
    )
    vertices, triangles = load_obj(path)
    vertices_normals = compute_vertex_normals(vertices, triangles)

    vertices = transform_points(MODEL_MATRIX, vertices)
    vertices = transform_points(VIEW_MATRIX, vertices)

    vertices_normals = transform_directions(MODEL_MATRIX, vertices_normals)
    vertices_normals = transform_directions(VIEW_MATRIX, vertices_normals)
    vertices_normals /= np.linalg.norm(vertices_normals, axis=1, keepdims=True)

    total = len(triangles)
    for i, tri_indices in enumerate(triangles):
        print(f"\rRendering: {(i + 1) / total * 100:5.1f}%", end="", flush=True)

        v0, v1, v2 = vertices[tri_indices[0]], vertices[tri_indices[1]], vertices[tri_indices[2]]
        if v0[2] >= -EPSILON or v1[2] >= -EPSILON or v2[2] >= -EPSILON:
            continue

        px0, py0, z0 = project_point(v0, FOV)
        px1, py1, z1 = project_point(v1, FOV)
        px2, py2, z2 = project_point(v2, FOV)
        triangle = Triangle((px0, py0, 0.), (px1, py1, 0.), (px2, py2, 0.))

        if shading == "flat":
            face_normal = np.cross(v1 - v0, v2 - v0)
            face_normal /= np.linalg.norm(face_normal)
            centre_point = (v0 + v1 + v2) / 3.

            if np.dot(face_normal, -centre_point) < EPSILON:
                face_normal = -face_normal
            color = compute_lighting(face_normal, LIGHT_DIR, BASE_COLOR, AMBIENT)
            draw_triangle(
                frame_buffer, 
                triangle, 
                depth_buffer, 
                depth_coefs=(z0, z1, z2),
                shading="flat", 
                color=color
            )
        else:
            vertex_normals = (
                vertices_normals[tri_indices[0]],
                vertices_normals[tri_indices[1]],
                vertices_normals[tri_indices[2]],
            )
            draw_triangle(
                frame_buffer, 
                triangle, 
                depth_buffer, 
                depth_coefs=(z0, z1, z2),
                shading="phong", 
                vertex_normals=vertex_normals)

    print()