from rasterizer import render_model
from framebuffer import FrameBuffer
from constants import IMAGE_HEIGHT, IMAGE_WIDTH

def main():
    frame_buffer = FrameBuffer(IMAGE_HEIGHT, IMAGE_WIDTH)
    color = (0, 255, 0)
    path = "../assets/.obj files/cube_rotated.obj"
    render_model(frame_buffer, color, path)
    frame_buffer.save_image("../assets/results/red_yellow_rotated_cube.png")

if __name__ == "__main__":
    main()
