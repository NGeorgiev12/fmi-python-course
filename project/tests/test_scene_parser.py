import os
import sys
import json
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scene_parser import (
    ImageConfig, Camera, Light, Transform, Material, Model, Scene, load_scene,
)


class TestImageConfig(unittest.TestCase):
    def test_from_dict(self):
        img = ImageConfig.from_dict({"width": 800, "height": 600, "output": "out.png"})
        self.assertEqual((img.width, img.height, img.output), (800, 600, "out.png"))

    def test_creates_framebuffer_of_right_size(self):
        img = ImageConfig.from_dict({"width": 8, "height": 4, "output": "o.png"})
        fb = img.create_frame_buffer()
        self.assertEqual((fb.get_width(), fb.get_height()), (8, 4))


class TestCamera(unittest.TestCase):
    def test_from_dict(self):
        cam = Camera.from_dict(
            {"eye": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0], "fov": 60}
        )
        np.testing.assert_allclose(cam.eye, [0, 0, 5])
        np.testing.assert_allclose(cam.target, [0, 0, 0])
        np.testing.assert_allclose(cam.up, [0, 1, 0])
        self.assertEqual(cam.fov, 60.0)

    def test_fov_is_required(self):
        with self.assertRaises(KeyError):
            Camera.from_dict({"eye": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0]})


class TestLight(unittest.TestCase):
    def test_from_dict(self):
        light = Light.from_dict({"direction": [1, 0, 0], "ambient": 0.3})
        np.testing.assert_allclose(light.direction, [1, 0, 0])
        self.assertEqual(light.ambient, 0.3)

    def test_ambient_defaults(self):
        light = Light.from_dict({"direction": [1, 0, 0]})
        self.assertEqual(light.ambient, 0.15)


class TestTransform(unittest.TestCase):
    def test_from_dict(self):
        tr = Transform.from_dict(
            {"translation": [1, 2, 3], "rotation": [10, 20, 30], "scale": [2, 2, 2]}
        )
        self.assertEqual(tr.translation, (1, 2, 3))
        self.assertEqual(tr.rotation, (10, 20, 30))
        self.assertEqual(tr.scale, (2, 2, 2))

    def test_defaults_are_identity(self):
        tr = Transform.from_dict({})
        self.assertEqual(tr.translation, (0., 0., 0.))
        self.assertEqual(tr.rotation, (0., 0., 0.))
        self.assertEqual(tr.scale, (1., 1., 1.))


class TestMaterial(unittest.TestCase):
    def test_from_dict(self):
        mat = Material.from_dict(
            {"base_color": [10, 20, 30], "shininess": 16, "specular_color": [1, 2, 3]}
        )
        self.assertEqual(mat.base_color, (10, 20, 30))
        self.assertEqual(mat.shininess, 16.0)
        self.assertEqual(mat.specular_color, (1, 2, 3))

    def test_defaults(self):
        mat = Material.from_dict({})
        self.assertEqual(mat.base_color, (200, 200, 0))
        self.assertEqual(mat.shininess, 32.0)
        self.assertEqual(mat.specular_color, (255, 255, 255))


class TestModel(unittest.TestCase):
    def test_from_dict_nests_material_and_transform(self):
        model = Model.from_dict({
            "path": "m.obj",
            "shading": "phong",
            "base_color": [1, 2, 3],
            "transform": {"rotation": [0, 90, 0]},
        })
        self.assertEqual(model.path, "m.obj")
        self.assertEqual(model.shading, "phong")
        self.assertIsInstance(model.material, Material)
        self.assertEqual(model.material.base_color, (1, 2, 3))
        self.assertIsInstance(model.transform, Transform)
        self.assertEqual(model.transform.rotation, (0, 90, 0))

    def test_shading_defaults_to_flat(self):
        model = Model.from_dict({"path": "m.obj"})
        self.assertEqual(model.shading, "flat")


class TestLoadScene(unittest.TestCase):
    def test_load_scene_from_file(self):
        scene_dict = {
            "image": {"width": 320, "height": 240, "output": "o.png"},
            "camera": {"eye": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0], "fov": 45},
            "light": {"direction": [0, 1, 0], "ambient": 0.2},
            "model": {"path": "m.obj", "shading": "flat", "base_color": [9, 9, 9]},
        }
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(scene_dict, f)
        try:
            scene = load_scene(path)
        finally:
            os.remove(path)

        self.assertIsInstance(scene, Scene)
        self.assertEqual(scene.image.width, 320)
        self.assertEqual(scene.camera.fov, 45.0)
        self.assertEqual(scene.light.ambient, 0.2)
        self.assertEqual(scene.model.material.base_color, (9, 9, 9))


if __name__ == "__main__":
    unittest.main()
