import random

from src.core.map import Map
from src.core.cell import CellType
from src.core.uav import UAV
from src.core.utils import load_map_from_file

cmd = "python multiRobotPathPlanner.py -grid {width} {height} -obs_pos {obs_pos} -in_pos {in_pos}"


def convert_to_darp(_map: Map, uavs: list[UAV]) -> None:
    free_cells = _map.free_cells
    obs_cells = _map.occupied_cells
    used_cells = set()

    for uav in uavs:
        while uav.r is None or uav.c is None:
            free_cell = random.choice(free_cells)
            if free_cell in used_cells:
                continue
            used_cells.add(free_cell)
            uav.r = free_cell[0]
            uav.c = free_cell[1]
            # print(f"{uav.name} starts at {(uav.r, uav.c)}")

    obs_pos = [str(_map.width * obs[0] + obs[1]) for obs in obs_cells]
    in_pos = [str(_map.width * uav.r + uav.c) for uav in uavs]  # type: ignore

    formatted_cmd = cmd.format(
        width=_map.width,
        height=_map.height,
        obs_pos=" ".join(obs_pos),
        in_pos=" ".join(in_pos),
    )
    print(formatted_cmd)
    print(f"Measure-Command {{ {formatted_cmd} }}")


my_map = load_map_from_file("../images_filled/Denver_0.png")

convert_to_darp(my_map, [UAV() for _ in range(5)])
