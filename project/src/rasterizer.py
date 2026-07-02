import math

import numpy as np

from transforms import (
    translation, rotation_x, rotation_y, rotation_z, scaling,
    look_at, transform_points, transform_directions,
)
from scene_parser import Scene, Material
from framebuffer import FrameBuffer
from triangle import Triangle
from bbox import BoundingBox
from camera import project_point
from obj_loader import load_obj
from shader import compute_lighting, compute_vertex_normals

EPSILON = 1e-6


def compute_barycentric_coords(triangle: Triangle, hit_point: np.ndarray) -> tuple:
    """Compute the barycentric weights of a point within a triangle.

    Each weight is the area of the sub-triangle opposite its vertex divided by
    the total area, so the weights sum to 1 and equal (1, 0, 0), (0, 1, 0) and
    (0, 0, 1) at the three vertices respectively. Used to interpolate per-vertex
    quantities (depth, normals) across the triangle.

    Args:
        triangle: The triangle, in screen space.
        hit_point: The point to weight, in the same space as the triangle.

    Returns:
        A tuple (w0, w1, w2) of weights aligned with the triangle's vertices.
    """
    p0, p1, p2 = triangle.get_points()
    double_area = triangle.get_area() * 2.

    w0 = np.linalg.norm(np.cross(p1 - hit_point, p2 - hit_point)) / double_area
    w1 = np.linalg.norm(np.cross(p2 - hit_point, p0 - hit_point)) / double_area
    w2 = 1. - w0 - w1

    return w0, w1, w2


def compute_depth(bary_coords: tuple, depths: tuple) -> float:
    """Interpolate perspective-correct depth at a point inside a triangle.

    Interpolates 1/z linearly in screen space (not z itself) and inverts the
    result, which is the correct way to interpolate depth under perspective.

    Args:
        bary_coords: The (w0, w1, w2) barycentric weights of the point.
        depths: The (z0, z1, z2) depths at the triangle's three vertices.

    Returns:
        The perspective-correct interpolated depth at the point.
    """
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
        light_dir: np.ndarray,
        material: "Material",
        ambient: float,
        color: tuple = None,
        vertex_normals: tuple = None) -> None:
    """Rasterize one triangle into the frame buffer with depth testing.

    Iterates the pixels within the triangle's screen-space bounding box (clamped
    to the image), keeps those inside the triangle, and for each one runs the
    depth test against the depth buffer. Surviving pixels are colored either with
    a precomputed flat color or, for Phong shading, by interpolating the vertex
    normals and lighting them per pixel.

    Args:
        frame_buffer: The image buffer to draw into.
        triangle: The triangle in screen space.
        depth_buffer: The (height, width) array of current nearest depths.
        depth_coefs: The (z0, z1, z2) camera-space depths of the vertices.
        shading: Either ``"flat"`` or ``"phong"``.
        light_dir: Direction toward the light (used for Phong shading).
        material: Material used for Phong shading.
        ambient: Ambient light fraction used for Phong shading.
        color: Precomputed color for flat shading (required when shading is
            ``"flat"``).
        vertex_normals: The three per-vertex normals (required when shading is
            ``"phong"``).
    """
    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = max(int(lower[0]), 0), max(int(lower[1]), 0)
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
                        pixel_color = compute_lighting(normal, light_dir, material, ambient)

                    frame_buffer.set_pixel(y, x, pixel_color)


def render_model(scene: Scene) -> None:
    """Render a scene to an image file.

    Runs the full pipeline: builds the model and view matrices from the scene,
    loads the mesh, computes vertex normals, transforms vertices and normals
    into camera space, then projects and rasterizes every triangle with depth
    testing. Triangles behind the camera are skipped. Flat shading lights one
    normal per face; Phong shading interpolates vertex normals per pixel. The
    finished frame buffer is written to the scene's output path.

    Args:
        scene: The fully parsed scene describing image, camera, light and model.
    """
    image = scene.image
    camera = scene.camera
    light = scene.light
    model = scene.model
    transform = model.transform

    frame_buffer = image.create_frame_buffer()
    depth_buffer = np.full(
        (frame_buffer.get_height(), frame_buffer.get_width()),
        np.inf, dtype=float,
    )

    model_matrix = (
        translation(*transform.translation)
        @ rotation_z(math.radians(transform.rotation[2]))
        @ rotation_y(math.radians(transform.rotation[1]))
        @ rotation_x(math.radians(transform.rotation[0]))
        @ scaling(*transform.scale)
    )
    view_matrix = look_at(camera.eye, camera.target, camera.up)

    vertices, triangles = load_obj(model.path)
    vertices_normals = compute_vertex_normals(vertices, triangles)

    vertices = transform_points(model_matrix, vertices)
    vertices = transform_points(view_matrix, vertices)

    vertices_normals = transform_directions(model_matrix, vertices_normals)
    vertices_normals = transform_directions(view_matrix, vertices_normals)
    vertices_normals /= np.linalg.norm(vertices_normals, axis=1, keepdims=True)

    fov = camera.fov
    width, height = image.width, image.height
    shading = model.shading
    total = len(triangles)

    for i, tri_indices in enumerate(triangles):
        print(f"\rRendering: {(i + 1) / total * 100:5.1f}%", end="", flush=True)

        v0, v1, v2 = vertices[tri_indices[0]], vertices[tri_indices[1]], vertices[tri_indices[2]]
        if v0[2] >= -EPSILON or v1[2] >= -EPSILON or v2[2] >= -EPSILON:
            continue

        px0, py0, z0 = project_point(v0, fov, width, height)
        px1, py1, z1 = project_point(v1, fov, width, height)
        px2, py2, z2 = project_point(v2, fov, width, height)
        triangle = Triangle((px0, py0, 0.), (px1, py1, 0.), (px2, py2, 0.))

        if shading == "flat":
            face_normal = np.cross(v1 - v0, v2 - v0)
            face_normal /= np.linalg.norm(face_normal)
            centre_point = (v0 + v1 + v2) / 3.
            if np.dot(face_normal, -centre_point) < 0:
                face_normal = -face_normal
            color = compute_lighting(face_normal, light.direction, model.material, light.ambient)
            draw_triangle(
                frame_buffer,
                triangle,
                depth_buffer,
                (z0, z1, z2),
                shading="flat",
                light_dir=light.direction,
                material=model.material,
                ambient=light.ambient,
                color=color,
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
                (z0, z1, z2),
                shading="phong",
                light_dir=light.direction,
                material=model.material,
                ambient=light.ambient,
                vertex_normals=vertex_normals
            )

    print()
    frame_buffer.save_image(image.output)