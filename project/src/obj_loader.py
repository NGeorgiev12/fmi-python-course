import numpy as np

def load_obj(path: str) -> tuple[np.ndarray]:
    """
    Load vertices and triangles from a Wavefront .obj file.

    Only geometric vertices (``v``) and faces (``f``) are read; texture
    coordinates, normals and other directives are ignored (for now). Faces with more
    than three vertices are fan-triangulated. File indices are 1-based and are
    converted to 0-based indices into the returned vertex array.

    Args:
        path: Path to the .obj file.

    Returns:
        A tuple (vertices, triangles): vertices is an (N, 3) float array of
        positions, triangles is an (M, 3) int array of indices into it.
    """
    positions = []
    triangles = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            tag = parts[0]

            if tag == "v":
                positions.append([float(c) for c in parts[1:4]])
            elif tag == "f":
                idx = []
                for ref in parts[1:]:
                    v = ref.split("/")[0]
                    i = int(v)
                    i = i - 1 if i > 0 else len(positions) + i  
                    idx.append(i)
                for k in range(1, len(idx) - 1):               
                    triangles.append((idx[0], idx[k], idx[k + 1]))

    return (np.array(positions, dtype=np.float64),
        np.array(triangles, dtype=np.int64))


