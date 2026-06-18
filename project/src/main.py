import numpy as np

from framebuffer import FrameBuffer
from camera import Camera
from triangle import Triangle
from bbox import BoundingBox
from obj_loader import load_obj
from constants import IMAGE_HEIGHT, IMAGE_WIDTH

CAMERA_OFFSET = np.array([0., 0., -5.])
FOV = 60.

def draw_triangle(frame_buffer: FrameBuffer, triangle: Triangle, color: tuple) -> None:
    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if triangle.edge_function((x, y, 0)):
                frame_buffer.set_pixel(y, x, color)

def render_model(frame_buffer: FrameBuffer, color: tuple, path: str) -> None:
    camera = Camera()
    vertices, triangles = load_obj(path)
    vertices += CAMERA_OFFSET

    for tri_indices in triangles:
        v0, v1, v2 = vertices[tri_indices[0]], vertices[tri_indices[1]], vertices[tri_indices[2]]
                
        # check if the object is behind the camera
        if v0[2] >= 0 or v1[2] >= 0 or v2[2] >= 0:
            continue

        p0 = camera.project_point(v0, FOV)
        p1 = camera.project_point(v1, FOV)
        p2 = camera.project_point(v2, FOV)

        triangle = Triangle((*p0, 0), (*p1, 0), (*p2, 0))
        draw_triangle(frame_buffer, triangle, color)

def main():
    frame_buffer = FrameBuffer(IMAGE_HEIGHT, IMAGE_WIDTH)
    color = (0, 255, 0)
    path = "../assets/.obj files/cube.obj"
    render_model(frame_buffer, color, path)
    frame_buffer.save_image("../assets/results/green_cube_2.png")

if __name__ == "__main__":
    main()
