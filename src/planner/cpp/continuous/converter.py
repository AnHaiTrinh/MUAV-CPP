from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory


class SingleAsContinuousCoveragePathPlanner(ContinuousCoveragePathPlanner):
    name = "single"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        assert len(uavs) == 1
        super().__init__(uavs, _map, **kwargs)
        assert "single_planner" in kwargs
        single_planner_name = kwargs["single_planner"]
        self.__class__.name = f"single_{single_planner_name}"
        self.single_planner = SingleCoveragePathPlannerFactory.get_planner(
            single_planner_name, _map, uavs[0], **kwargs
        )

    def init_plan(self):
        self.single_planner.plan()

    def new_uav_plan(self, uav_name: str):
        raise NotImplementedError("Single planner does not support adding new uav")

    def remove_uav_plan(self, uav_name: str):
        raise NotImplementedError("Single planner does not support removing existing uav")
