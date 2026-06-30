import json
import numpy as np

from dataclasses import dataclass
from framebuffer import FrameBuffer

@dataclass
class ImageConfig:
    width: int
    height: int
    output: str

    @classmethod
    def from_dict(cls, data: dict) -> "ImageConfig":
        return cls(
            width=data["width"],
            height=data["height"],
            output=data["output"],
        )

    def create_frame_buffer(self) -> FrameBuffer:
        return FrameBuffer(self.height, self.width)

@dataclass
class Camera:
    eye: np.ndarray
    target: np.ndarray
    up: np.ndarray
    fov: float

    @classmethod
    def from_dict(cls, data: dict) -> "Camera":
        return cls(
            eye=np.array(data["eye"], dtype=float),
            target=np.array(data["target"], dtype=float),
            up=np.array(data["up"], dtype=float),
            fov=float(data["fov"]),
        )


@dataclass
class Light:
    direction: np.ndarray
    ambient: float

    @classmethod
    def from_dict(cls, data: dict) -> "Light":
        return cls(
            direction=np.array(data["direction"], dtype=float),
            ambient=float(data.get("ambient", 0.15)),
        )


@dataclass
class Transform:
    translation: tuple
    rotation: tuple 
    scale: tuple

    @classmethod
    def from_dict(cls, data: dict) -> "Transform":
        return cls(
            translation=tuple(data.get("translation", [0., 0., 0.])),
            rotation=tuple(data.get("rotation", [0., 0., 0.])),
            scale=tuple(data.get("scale", [1., 1., 1.])),
        )


@dataclass
class Material:
    base_color: tuple
    shininess: float
    specular_color: tuple

    @classmethod
    def from_dict(cls, data: dict) -> "Material":
        return cls(
            base_color=tuple(data.get("base_color", [200, 200, 0])),
            shininess=float(data.get("shininess", 32.)),
            specular_color=tuple(data.get("specular_color", [255, 255, 255])),
        )


@dataclass
class Model:
    path: str
    shading: str
    material: Material
    transform: Transform

    @classmethod
    def from_dict(cls, data: dict) -> "Model":
        return cls(
            path=data["path"],
            shading=data.get("shading", "flat"),
            material=Material.from_dict(data), 
            transform=Transform.from_dict(data.get("transform", {})),
        )

@dataclass
class Scene:
    image: ImageConfig
    camera: Camera
    light: Light
    model: Model


def load_scene(path: str) -> Scene:
    with open(path, "r") as f:
        data = json.load(f)

    return Scene(
        image=ImageConfig.from_dict(data["image"]),
        camera=Camera.from_dict(data["camera"]),
        light=Light.from_dict(data["light"]),
        model=Model.from_dict(data["model"]),
    )