from rasterizer import render_model
from scene_parser import load_scene

def main():
    scene = load_scene("../assets/json_files/sphere.json")
    render_model(scene)

if __name__ == "__main__":
    main()
