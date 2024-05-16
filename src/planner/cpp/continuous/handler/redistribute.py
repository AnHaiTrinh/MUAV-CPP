from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandler
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory


class RedistributeHandler(UAVChangeHandler):
    name = "Redistribute"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.multi_planner_name = kwargs.get("multi_planner_name", "Transfer")
        self.kwargs = kwargs

    def handle_new_uav(self, uav: UAV) -> None:
        self.uavs.append(uav)
        self.reassign()

    def handle_removed_uav(self, uav: UAV) -> None:
        self.uavs.remove(uav)
        self.reassign()

    def reassign(self) -> None:
        self.map.clear_assignment()
        multi_planner = MultiCoveragePathPlannerFactory.get_planner(
            self.multi_planner_name,
            self.uavs,
            self.map,
            **self.kwargs,
        )
        multi_planner.plan()
