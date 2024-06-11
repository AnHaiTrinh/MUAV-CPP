import os
import logging
import random
import time
from collections.abc import Callable

from src.core.map import Map
from src.core.uav import UAV
from src.core.utils import load_map_from_file

random.seed(42069)
IMAGES_DIR = "images_filled/"


def setup(
    num_uavs: int, init_uav_pos: bool = False, init_assign: bool = False
) -> list[tuple[str, Map, list[UAV]]]:
    tests = []
    for img_file in os.listdir(IMAGES_DIR):
        my_map = load_map_from_file(os.path.join(IMAGES_DIR, img_file))
        my_uavs = [UAV(has_color=False) for _ in range(num_uavs)]
        if init_uav_pos:
            for my_uav in my_uavs:
                start = random.choice(my_map.free_cells)
                my_uav.r, my_uav.c = start.r, start.c

        if init_assign:
            for cell in my_map.free_cells:
                cell.assign = my_uavs[0].name
        tests.append((img_file, my_map, my_uavs))
    return tests


def movements(num_change: int) -> list[tuple[int, bool]]:
    return [
        (random.randint(1000, 2000), bool(random.randint(0, 1)))
        for _ in range(num_change)
    ]


def get_logger(fn: str):
    logger = logging.getLogger()
    logger.setLevel("INFO")
    handler = logging.FileHandler(fn, mode="a")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def time_func(func: Callable, *args) -> tuple[float, bool]:
    success = True
    start = time.perf_counter()
    try:
        func(*args)
    except Exception as exp:
        print(exp)
        success = False
    end = time.perf_counter()
    return end - start, success
