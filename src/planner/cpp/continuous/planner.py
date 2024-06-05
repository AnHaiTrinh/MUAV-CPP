import random

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandlerFactory
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory

random.seed(42069)


class ContinuousCoveragePathPlanner:
    def __init__(
        self, uavs: list[UAV], _map: Map, multi_planner: str, handler: str, **kwargs
    ):
        self.uavs = uavs
        self.map = _map
        for uav in self.uavs:
            self.allocate_initial_uav_position(uav)
        self.multi_planner = MultiCoveragePathPlannerFactory.get_planner(
            multi_planner, uavs, _map, **kwargs
        )
        self.handler = UAVChangeHandlerFactory.get_handler(
            handler, uavs, _map, multi_planner_name=multi_planner, **kwargs
        )

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


if __name__ == "__main__":
    from src.core.utils import load_map_from_file
    from src.planner.cpp.utils import get_assign_count, map_to_assignment_matrix
    import time

    my_map = load_map_from_file("../../../../images_filled/Denver_0.png")
    NUM_UAVS = 8
    my_uavs = [UAV(name=f"UAV{i + 1}") for i in range(NUM_UAVS)]

    transfer = ContinuousCoveragePathPlanner(
        my_uavs, my_map, multi_planner="Transfer", handler="Voronoi"
    )
    start = time.perf_counter()
    transfer.plan()
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(map_to_assignment_matrix(my_map, my_uavs), NUM_UAVS))

    for _ in range(random.randint(0, 100)):
        for my_uav in my_uavs:
            my_uav.move()
    start = time.perf_counter()
    transfer.handle_removed_uav("UAV2")
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(map_to_assignment_matrix(my_map, my_uavs), NUM_UAVS - 1))

    for _ in range(random.randint(0, 100)):
        for my_uav in my_uavs:
            my_uav.move()
    start = time.perf_counter()
    transfer.handle_new_uav("UAV10")
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(map_to_assignment_matrix(my_map, my_uavs), NUM_UAVS))

    for _ in range(random.randint(0, 100)):
        for my_uav in my_uavs:
            my_uav.move()
    start = time.perf_counter()
    transfer.handle_new_uav("UAV100")
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(map_to_assignment_matrix(my_map, my_uavs), NUM_UAVS + 1))

    for _ in range(random.randint(0, 100)):
        for my_uav in my_uavs:
            my_uav.move()
    start = time.perf_counter()
    transfer.handle_removed_uav("UAV5")
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(map_to_assignment_matrix(my_map, my_uavs), NUM_UAVS))
