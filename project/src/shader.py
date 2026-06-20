import numpy as np

def compute_diffuse(
        normal: np.ndarray, 
        light_dir: np.ndarray,
        base_color: tuple, 
        ambient: float = 0.15
    ) -> tuple:

    n = normal / np.linalg.norm(normal)
    l = light_dir / np.linalg.norm(light_dir)
    intensity = max(0.0, float(np.dot(n, l)))
    scale = ambient + (1.0 - ambient) * intensity
    return tuple(int(min(255, c * scale)) for c in base_color)

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

    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    lengths[lengths == 0] = 1.0  
    return normals / lengths