import numpy as np


def rotation_x(angle_rad: float) -> np.ndarray:
    """Build a 4x4 homogeneous rotation matrix about the X axis.

    Args:
        angle_rad: Rotation angle in radians (counter-clockwise looking
            down the +X axis toward the origin).

    Returns:
        A 4x4 rotation matrix.
    """
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]],
        dtype=float
    )


def rotation_y(angle_rad: float) -> np.ndarray:
    """Build a 4x4 homogeneous rotation matrix about the Y axis.

    Args:
        angle_rad: Rotation angle in radians.

    Returns:
        A 4x4 rotation matrix.
    """
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]],
        dtype=float
    )


def rotation_z(angle_rad: float) -> np.ndarray:
    """Build a 4x4 homogeneous rotation matrix about the Z axis.

    Args:
        angle_rad: Rotation angle in radians.

    Returns:
        A 4x4 rotation matrix.
    """
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]],
        dtype=float
    )


def translation(tx: float, ty: float, tz: float) -> np.ndarray:
    """Build a 4x4 homogeneous translation matrix.

    Args:
        tx: Translation along X.
        ty: Translation along Y.
        tz: Translation along Z.

    Returns:
        A 4x4 translation matrix.
    """
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]],
        dtype=float
    )


def scaling(sx: float, sy: float, sz: float) -> np.ndarray:
    """Build a 4x4 homogeneous (possibly non-uniform) scaling matrix.

    Args:
        sx: Scale factor along X.
        sy: Scale factor along Y.
        sz: Scale factor along Z.

    Returns:
        A 4x4 scaling matrix.
    """
    return np.array([
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1]],
        dtype=float
    )


def look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Build a view matrix that moves the world into camera space.

    Constructs an orthonormal camera basis from the eye/target/up vectors,
    then returns the matrix that first translates the world so the camera is
    at the origin and then rotates it so the camera looks down the -z axis.

    Args:
        eye: Camera position in world space.
        target: The point the camera looks at.
        up: Approximate up direction; it is re-orthogonalized internally, so
            it need only be non-parallel to the view direction.

    Returns:
        A 4x4 view matrix (rotation composed with translation).
    """
    forward = target - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)

    rotation = np.array([
        [ right[0],     right[1],     right[2],    0.],
        [ true_up[0],   true_up[1],   true_up[2],  0.],
        [-forward[0],  -forward[1],  -forward[2],  0.],
        [ 0.,           0.,           0.,          1.],
    ])
    translation_to_origin = np.array([
        [1., 0., 0., -eye[0]],
        [0., 1., 0., -eye[1]],
        [0., 0., 1., -eye[2]],
        [0., 0., 0., 1.],
    ])
    return rotation @ translation_to_origin


def transform_points(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Apply a 4x4 transform to a batch of 3D points.

    Points are treated as positions (homogeneous w = 1), so the translation
    part of the matrix affects them.

    Args:
        matrix: A 4x4 transformation matrix.
        points: An (N, 3) array of point positions.

    Returns:
        An (N, 3) array of transformed positions.
    """
    homogeneous = np.hstack([points, np.ones((len(points), 1))])
    transformed = homogeneous @ matrix.T
    return transformed[:, :3]


def transform_directions(matrix: np.ndarray, directions: np.ndarray) -> np.ndarray:
    """Apply a transform to direction vectors (e.g. normals).

    Uses the inverse-transpose of the matrix's 3x3 part so that normals stay
    perpendicular to their surfaces under non-uniform scaling. Translation has
    no effect on directions. The results are not re-normalized.

    Args:
        matrix: A 4x4 transformation matrix.
        directions: An (N, 3) array of direction vectors.

    Returns:
        An (N, 3) array of transformed directions.
    """
    normal_matrix = np.linalg.inv(matrix[:3, :3]).T
    return directions @ normal_matrix.T