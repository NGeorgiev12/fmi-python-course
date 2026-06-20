from rasterizer import render_model
from framebuffer import FrameBuffer
from constants import IMAGE_HEIGHT, IMAGE_WIDTH

def main():
    frame_buffer = FrameBuffer(IMAGE_HEIGHT, IMAGE_WIDTH)
    path = "../assets/.obj files/sphere.obj"
    render_model(frame_buffer, path)
    frame_buffer.save_image("../assets/results/smooth_sphere.png")

if __name__ == "__main__":
    main()
