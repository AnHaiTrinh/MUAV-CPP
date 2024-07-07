from src.render.renderer import Renderer

main_renderer = Renderer(num_uavs=1, map_size=(8, 8))
main_renderer.run()
