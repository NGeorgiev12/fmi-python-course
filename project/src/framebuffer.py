from PIL import Image
import numpy as np


class FrameBuffer:
    """An RGB image buffer that the rasterizer draws into.

    Wraps a ``(height, width, 3)`` array of 8-bit color channels. Pixels are
    addressed by row (height) then column (width), matching the numpy layout,
    with the origin at the top-left corner. Once drawing is finished the buffer
    can be written to disk as an image via :meth:`save_image`.
    """

    def __init__(self, height: int, width: int, background=(0, 0, 0)):
        """Allocate the buffer and fill it with a background color.

        Args:
            height: Image height in pixels (number of rows).
            width: Image width in pixels (number of columns).
            background: RGB fill color for every pixel, as a 3-tuple of
                0-255 values. Defaults to black.
        """
        self._height = height
        self._width = width
        self._framebuffer = np.empty((height, width, 3), dtype=np.uint8)
        self._framebuffer[:, :] = background

    def save_image(self, path) -> None:
        """Write the buffer to disk as an RGB image.

        Args:
            path: Destination file path; the image format is inferred from
                its extension (e.g. ``.png``).
        """
        Image.fromarray(self._framebuffer, mode="RGB").save(path)

    def get_pixel(self, cur_height: int, cur_width: int) -> np.ndarray:
        """Return the color of a single pixel.

        Args:
            cur_height: Row index (y).
            cur_width: Column index (x).

        Returns:
            The pixel's RGB values as a length-3 uint8 array.
        """
        return self._framebuffer[cur_height][cur_width]

    def set_pixel(self, cur_height: int, cur_width: int, color: tuple) -> None:
        """Set the color of a single pixel.

        Args:
            cur_height: Row index (y).
            cur_width: Column index (x).
            color: RGB color to write, as a 3-tuple of 0-255 values.
        """
        self._framebuffer[cur_height][cur_width] = color

    def get_pixels(self) -> np.ndarray:
        """Return the underlying ``(height, width, 3)`` pixel array."""
        return self._framebuffer

    def get_height(self) -> int:
        """Return the image height in pixels."""
        return self._height

    def get_width(self) -> int:
        """Return the image width in pixels."""
        return self._width