from src.planner.cpp.single.single_planner import SingleCPPPlanner
from src.core.map import Map
from src.core.uav import UAV


class SimpleSTCPlanner(SingleCPPPlanner):
    name = 'STC'

    def plan(self, area: Map, uav: UAV) -> None:
        pass

