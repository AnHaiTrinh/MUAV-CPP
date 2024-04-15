from planner.cpp.single.single_planner import SingleCPPPlanner
from core.map import Map
from core.uav import UAV


class SimpleSTCPlanner(SingleCPPPlanner):
    name = 'STC'

    def plan(self, area: Map, uav: UAV) -> None:
        pass

