import numpy as np

def rotation_x(angle_rad: float) -> np.ndarray:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]], 
        dtype=float
    )

def rotation_y(angle_rad: float) -> np.ndarray:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]], 
        dtype=float
    )

def rotation_z(angle_rad: float) -> np.ndarray:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]], 
        dtype=float
    )

def translation(tx: float, ty: float, tz: float) -> np.ndarray:
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]], 
        dtype=float
    )

def scaling(sx: float, sy: float, sz: float) -> np.ndarray:
    return np.array([
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1]], 
        dtype=float
    )

def look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
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
    homogeneous = np.hstack([points, np.ones((len(points), 1))]) 
    transformed = homogeneous @ matrix.T                          
    return transformed[:, :3]                                     

def transform_directions(matrix: np.ndarray, directions: np.ndarray) -> np.ndarray:
    """Трансформира посоки/нормали с обратно-транспонираната 3x3 част."""
    normal_matrix = np.linalg.inv(matrix[:3, :3]).T
    return directions @ normal_matrix.T