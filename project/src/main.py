from rasterizer import render_model
from scene_parser import load_scene
from PIL import Image

def main():
    # scene = load_scene("../assets/json_files/purple_dragon.json")
    # frames = 12

    # for i in range(frames):
    #     angle = i * 360 / frames    
    #     scene.model.transform.rotation = (0, angle, 0)
    #     scene.image.output = f"../assets/results/purple_dragon{i:02d}.png"
    #     render_model(scene)

    frames = [Image.open(f"../assets/results/purple_dragon{i:02d}.png") for i in range(12)]

    frames[0].save(
        "../assets/results/dragon.gif",
        save_all=True,           
        append_images=frames[1:],
        duration=100,           
        loop=0,                  
    )
    
if __name__ == "__main__":
    main()
