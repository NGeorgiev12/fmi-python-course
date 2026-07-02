import json
import numpy as np

from dataclasses import dataclass
from framebuffer import FrameBuffer


@dataclass
class ImageConfig:
    """Output image settings: dimensions and destination path."""

    width: int
    height: int
    output: str

    @classmethod
    def from_dict(cls, data: dict) -> "ImageConfig":
        """Build an ImageConfig from the ``image`` section of a scene dict.

        Args:
            data: Mapping with keys ``width``, ``height`` and ``output``.

        Returns:
            The parsed ImageConfig.
        """
        return cls(
            width=data["width"],
            height=data["height"],
            output=data["output"],
        )

    def create_frame_buffer(self) -> FrameBuffer:
        """Create a blank FrameBuffer matching this config's dimensions."""
        return FrameBuffer(self.height, self.width)


@dataclass
class Camera:
    """Camera placement and lens: eye, target, up and field of view."""

    eye: np.ndarray
    target: np.ndarray
    up: np.ndarray
    fov: float

    @classmethod
    def from_dict(cls, data: dict) -> "Camera":
        """Build a Camera from the ``camera`` section of a scene dict.

        Args:
            data: Mapping with keys ``eye``, ``target``, ``up`` and ``fov``.

        Returns:
            The parsed Camera.
        """
        return cls(
            eye=np.array(data["eye"], dtype=float),
            target=np.array(data["target"], dtype=float),
            up=np.array(data["up"], dtype=float),
            fov=float(data["fov"]),
        )


@dataclass
class Light:
    """A directional light: a direction toward the light and an ambient floor."""

    direction: np.ndarray
    ambient: float

    @classmethod
    def from_dict(cls, data: dict) -> "Light":
        """Build a Light from the ``light`` section of a scene dict.

        Args:
            data: Mapping with key ``direction`` and optional ``ambient``
                (defaults to 0.15).

        Returns:
            The parsed Light.
        """
        return cls(
            direction=np.array(data["direction"], dtype=float),
            ambient=float(data.get("ambient", 0.15)),
        )


@dataclass
class Transform:
    """A model's placement: translation, rotation (degrees) and scale."""

    translation: tuple
    rotation: tuple
    scale: tuple

    @classmethod
    def from_dict(cls, data: dict) -> "Transform":
        """Build a Transform, filling in identity defaults for missing fields.

        Args:
            data: Mapping with optional keys ``translation``, ``rotation``
                (Euler angles in degrees, x/y/z) and ``scale``.

        Returns:
            The parsed Transform (identity where fields are absent).
        """
        return cls(
            translation=tuple(data.get("translation", [0., 0., 0.])),
            rotation=tuple(data.get("rotation", [0., 0., 0.])),
            scale=tuple(data.get("scale", [1., 1., 1.])),
        )


@dataclass
class Material:
    """Surface appearance: base color, shininess and specular color."""

    base_color: tuple
    shininess: float
    specular_color: tuple

    @classmethod
    def from_dict(cls, data: dict) -> "Material":
        """Build a Material, filling in defaults for missing fields.

        Args:
            data: Mapping with optional keys ``base_color``, ``shininess``
                and ``specular_color``.

        Returns:
            The parsed Material.
        """
        return cls(
            base_color=tuple(data.get("base_color", [200, 200, 0])),
            shininess=float(data.get("shininess", 32.)),
            specular_color=tuple(data.get("specular_color", [255, 255, 255])),
        )


@dataclass
class Model:
    """A renderable model: mesh path, shading mode, material and transform."""

    path: str
    shading: str
    material: Material
    transform: Transform

    @classmethod
    def from_dict(cls, data: dict) -> "Model":
        """Build a Model from the ``model`` section of a scene dict.

        The material fields are read from the same ``model`` mapping, and the
        transform is read from a nested ``transform`` mapping (both optional
        with sensible defaults).

        Args:
            data: Mapping with key ``path`` and optional ``shading`` (defaults
                to ``"flat"``), material fields and a ``transform`` sub-mapping.

        Returns:
            The parsed Model.
        """
        return cls(
            path=data["path"],
            shading=data.get("shading", "flat"),
            material=Material.from_dict(data),
            transform=Transform.from_dict(data.get("transform", {})),
        )


@dataclass
class Scene:
    """A complete scene: image, camera, light and model."""

    image: ImageConfig
    camera: Camera
    light: Light
    model: Model


def load_scene(path: str) -> Scene:
    """Load and parse a JSON scene file into a Scene object.

    Args:
        path: Path to the JSON scene file. It must contain the top-level
            sections ``image``, ``camera``, ``light`` and ``model``.

    Returns:
        The fully parsed Scene.
    """
    with open(path, "r") as f:
        data = json.load(f)

    return Scene(
        image=ImageConfig.from_dict(data["image"]),
        camera=Camera.from_dict(data["camera"]),
        light=Light.from_dict(data["light"]),
        model=Model.from_dict(data["model"]),
    )