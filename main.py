from misc.viz_map_assignee import parse_uavs_and_map
from src.render.renderer import Renderer

main_renderer = Renderer(num_uavs=8)
uavs, maps = parse_uavs_and_map("add_7.json")
main_renderer.map_component._map = maps
main_renderer.uavs = uavs
main_renderer.run()
