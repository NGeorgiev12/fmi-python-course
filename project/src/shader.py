import numpy as np

from scene_parser import Material

VIEW_DIR = np.array([0., 0., 1.])

def compute_lighting(
        normal: np.ndarray,
        light_dir: np.ndarray,
        material: "Material",
        ambient: float = 0.15) -> tuple:

    n = normal / np.linalg.norm(normal)
    l = light_dir / np.linalg.norm(light_dir)

    diffuse = max(0.0, float(np.dot(n, l)))
    specular = 0.
    if diffuse > 0.:
        h = l + VIEW_DIR
        h /= np.linalg.norm(h)
        specular = max(0., float(np.dot(n, h))) ** material.shininess

    diffuse_scale = ambient + (1. - ambient) * diffuse
    return tuple(
        int(min(255, bc * diffuse_scale + sc * specular))
        for bc, sc in zip(material.base_color, material.specular_color)
    )

def compute_vertex_normals(vertices: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """
    Smooth (per-vertex) нормала за всеки връх: натрупваш нормалите на всички
    стени, които го ползват, после нормираш.

    Args:
        vertices: (N, 3) позиции на върховете.
        triangles: (M, 3) индекси на върховете.

    Returns:
        (N, 3) единични нормали на върховете.
    """
    normals = np.zeros_like(vertices)
    for i0, i1, i2 in triangles:
        v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
        face_normal = np.cross(v1 - v0, v2 - v0) 
        normals[i0] += face_normal
        normals[i1] += face_normal
        normals[i2] += face_normal

    center = vertices.mean(axis=0)
    outward = vertices - center 
    pointing_inward = np.sum(normals * outward, axis=1) < 0
    normals[pointing_inward] = -normals[pointing_inward]

    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    lengths[lengths == 0] = 1.0  
    return normals / lengths