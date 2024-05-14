import random

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandlerFactory
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory

random.seed(42069)


class ContinuousCoveragePathPlanner:
    def __init__(self, uavs: list[UAV], _map: Map, multi_planner: str, handler: str = "Transfer", **kwargs):
        self.uavs = uavs
        self.map = _map
        for uav in self.uavs:
            self.allocate_initial_uav_position(uav)
        self.multi_planner = MultiCoveragePathPlannerFactory.get_planner(multi_planner, uavs, _map, **kwargs)
        self.handler = UAVChangeHandlerFactory.get_handler(handler, uavs, _map, **kwargs)

    def plan(self):
        self.multi_planner.plan()

    def handle_new_uav(self, uav_name: str):
        uav = UAV(name=uav_name)
        self.allocate_initial_uav_position(uav)
        self.handler.handle_new_uav(uav)

    def handle_removed_uav(self, uav_name: str):
        uav = next((uav for uav in self.uavs if uav.name == uav_name), None)
        if uav is None:
            raise ValueError(f"UAV {uav_name} not found")
        self.handler.handle_removed_uav(uav)

    def allocate_initial_uav_position(self, new_uav: UAV) -> None:
        if new_uav.r is not None and new_uav.c is not None:
            return
        while True:
            free_cell = random.choice(self.map.free_cells)
            for uav in self.uavs:
                if free_cell == (uav.r, uav.c):
                    continue
            new_uav.r = free_cell.r
            new_uav.c = free_cell.c
            print(f"{new_uav.name} starts at {(new_uav.r, new_uav.c)}")
            break
