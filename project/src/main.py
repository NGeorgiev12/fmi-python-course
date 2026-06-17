import numpy as np

from framebuffer import FrameBuffer
from triangle import Triangle
from bbox import BoundingBox

IMAGE_WIDTH = 960
IMAGE_HEIGHT = 540

def render_triangle(frame_buffer: FrameBuffer, color: tuple) -> None:
    v0 = np.array([180, 430, 0])
    v1 = np.array([780, 430, 0])
    v2 = np.array([480, 110, 0])

    triangle = Triangle(v0, v1, v2)
    bbox = BoundingBox.from_points(triangle.get_points())
    lower = bbox.get_lower_bound()
    upper = bbox.get_upper_bound()
    min_x, min_y = int(lower[0]), int(lower[1])
    max_x, max_y = int(upper[0]), int(upper[1])

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if triangle.edge_function((x, y, 0)):
                frame_buffer.set_pixel(y, x, color)

def main():
    frame_buffer = FrameBuffer(IMAGE_HEIGHT, IMAGE_WIDTH)
    color = (255, 0, 0)
    render_triangle(frame_buffer, color)
    frame_buffer.save_image("../assets/red_triangle.png")

if __name__ == "__main__":
    main()
