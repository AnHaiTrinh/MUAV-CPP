from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory


class SingleAsContinuousCoveragePathPlanner(ContinuousCoveragePathPlanner):
    name = "Single"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        assert len(uavs) == 1
        assert "single_planner" in kwargs
        single_planner_name = kwargs["single_planner"]
        uav = uavs[0]
        for height in range(_map.height):
            for width in range(_map.width):
                if _map.get_cell(height, width).cell_type == CellType.FREE:
                    _map.assign(height, width, uav)
                    if uav.r is None:
                        uav.r = height
                    if uav.c is None:
                        uav.c = width
        self.single_planner = SingleCoveragePathPlannerFactory.get_planner(
            single_planner_name, _map, uav, **kwargs
        )
        super().__init__(uavs, _map, **kwargs)

    def init_plan(self):
        self.single_planner.plan()

    def new_uav_plan(self, uav_name: str):
        raise NotImplementedError("Single planner does not support adding new uav")

    def remove_uav_plan(self, uav_name: str):
        raise NotImplementedError(
            "Single planner does not support removing existing uav"
        )
