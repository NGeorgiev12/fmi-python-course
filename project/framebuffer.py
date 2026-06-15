from PIL import Image
import numpy as np

class FrameBuffer:

    def __init__(self, height: int, width: int, background=(0, 0, 0)):
        self._height = height
        self._width = width
        self._framebuffer = np.empty((height, width, 3), dtype=np.uint8)
        self._framebuffer[:, :] = background

    def save_image(self, path) -> None:
        Image.fromarray(self._framebuffer, mode="RGB").save(path)

    def get_pixel(self, cur_height: int, cur_width: int) -> np.ndarray:
        return self._framebuffer[cur_height][cur_width]

    def set_pixel(self, cur_height: int, cur_width: int, color: tuple) -> None:
        self._framebuffer[cur_height][cur_width] = color

    def get_pixels(self) -> np.ndarray:
        return self._framebuffer

if __name__ == "__main__":
    w, h = 256, 256
    fb = FrameBuffer(h, w)
    xs = np.linspace(0, 255, w, dtype=np.uint8)
    ys = np.linspace(0, 255, h, dtype=np.uint8)
    buffer = fb.get_pixels()
    buffer[:, :, 0] = xs[np.newaxis, :] 
    buffer[:, :, 1] = ys[:, np.newaxis]
    fb.save_image("assets/test_gradient.png")
    print("Записах test_gradient.png")