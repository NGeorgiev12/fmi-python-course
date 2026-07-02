import numpy as np

from scene_parser import Material

VIEW_DIR = np.array([0., 0., 1.])  # view direction in camera space (distant-viewer approximation)


def compute_lighting(
        normal: np.ndarray,
        light_dir: np.ndarray,
        material: "Material",
        ambient: float = 0.15) -> tuple:
    """Compute the shaded RGB color of a surface point.

    Uses a Blinn-Phong model: an ambient term plus a diffuse term proportional
    to the cosine between the surface normal and the light direction, plus a
    specular highlight based on the half-vector between the light and the
    (fixed) view direction. The result is clamped to the 0-255 range.

    Args:
        normal: Surface normal (need not be unit length; it is normalized).
        light_dir: Direction toward the light (need not be unit length).
        material: Material supplying ``base_color``, ``shininess`` and
            ``specular_color``.
        ambient: Ambient light fraction in [0, 1]; the floor brightness a
            surface keeps even when facing away from the light.

    Returns:
        An (R, G, B) tuple of ints in the range 0-255.
    """
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
    """Compute a smooth (per-vertex) normal for every vertex.

    Accumulates the face normals of all triangles that use a vertex, then
    normalizes. Because the raw face normals are not unit length, larger faces
    contribute more (area-weighting). Each resulting normal is finally oriented
    to point outward, away from the mesh centroid, which keeps lighting correct
    regardless of triangle winding for convex-ish meshes.

    Args:
        vertices: (N, 3) array of vertex positions.
        triangles: (M, 3) array of vertex indices.

    Returns:
        An (N, 3) array of unit, outward-facing vertex normals.
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