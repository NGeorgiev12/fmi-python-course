import numpy as np

from framebuffer import FrameBuffer
from camera import Camera
from triangle import Triangle
from bbox import BoundingBox
from constants import IMAGE_HEIGHT, IMAGE_WIDTH

def render_triangle_3d_coords(frame_buffer: FrameBuffer, color: tuple, fov: float = 90.) -> None:
    
    camera = Camera()
    v0 = np.array([-2., -1., -3.])
    v1 = np.array([2., -1., -3.])
    v2 = np.array([0., 2., -3.])

    p0 = camera.project_point(v0, fov)
    p1 = camera.project_point(v1, fov)
    p2 = camera.project_point(v2, fov)

    triangle = Triangle((*p0, 0), (*p1, 0), (*p2, 0))
    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if triangle.edge_function((x, y, 0)):
                frame_buffer.set_pixel(y, x, color)

def render_two_triangles_3ds(frame_buffer: FrameBuffer, color: tuple, fov: float = 90.) -> None:
    
    camera = Camera()
    v0 = np.array([-2., -1., -3.])
    v1 = np.array([2., -1., -3.])
    v2 = np.array([0., 2., -3.])

    u0 = np.array([-2., -1., -3.])
    u1 = np.array([2., -1., -3.])
    u2 = np.array([4.5, 2., -3.])

    p0 = camera.project_point(v0, fov)
    p1 = camera.project_point(v1, fov)
    p2 = camera.project_point(v2, fov)

    r0 = camera.project_point(u0, fov)
    r1 = camera.project_point(u1, fov)
    r2 = camera.project_point(u2, fov)

    triangle1 = Triangle((*p0, 0), (*p1, 0), (*p2, 0))
    triangle2 = Triangle((*r0, 0), (*r1, 0), (*r2, 0))
    bbox = BoundingBox.from_points(triangle1.get_points())
    bbox.include_triangle(triangle2)
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            for triangle in triangle1, triangle2:
                if triangle.edge_function((x, y, 0)):
                    frame_buffer.set_pixel(y, x, color)

def main():
    frame_buffer = FrameBuffer(IMAGE_HEIGHT, IMAGE_WIDTH)
    color = (0, 255, 0)
    render_two_triangles_3ds(frame_buffer, color, )
    frame_buffer.save_image("../assets/two_triangles_3ds.png")

if __name__ == "__main__":
    main()
