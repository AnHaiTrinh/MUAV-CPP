from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandlerFactory
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory


class ContinuousCoveragePathPlanner:
    def __init__(self, uavs: list[UAV], _map: Map, multi_planner: str, handler: str = "NoOp", **kwargs):
        self.uavs = uavs
        self.map = _map
        self.multi_planner = MultiCoveragePathPlannerFactory.get_planner(multi_planner, uavs, _map, **kwargs)
        self.handler = UAVChangeHandlerFactory.get_handler(handler, uavs, _map, **kwargs)

    def plan(self):
        self.multi_planner.plan()

    def handle_new_uav(self, uav: UAV):
        self.handler.handle_new_uav(uav)

    def handle_removed_uav(self, uav: UAV):
        self.handler.handle_removed_uav(uav)
