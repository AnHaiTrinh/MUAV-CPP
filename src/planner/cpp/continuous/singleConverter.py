from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory


class SingleAsContinuousCoveragePathPlanner(ContinuousCoveragePathPlanner):
    name = "Single"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        assert len(uavs) == 1
        super().__init__(uavs, _map, **kwargs)
        single_planner_name = kwargs.get("single_planner", "STC")
        uav = uavs[0]
        for height in range(_map.height):
            for width in range(_map.width):
                if _map.get_cell(height, width).cell_type == CellType.FREE:
                    _map.assign(height, width, uav)

        self.single_planner = SingleCoveragePathPlannerFactory.get_planner(
            single_planner_name, _map, uav, **kwargs
        )
        self.init_plan()

    def init_plan(self):
        self.single_planner.plan()

    def new_uav_plan(self, uav_name: str):
        raise NotImplementedError("Single planner does not support adding new uav")

    def remove_uav_plan(self, uav_name: str):
        raise NotImplementedError(
            "Single planner does not support removing existing uav"
        )
