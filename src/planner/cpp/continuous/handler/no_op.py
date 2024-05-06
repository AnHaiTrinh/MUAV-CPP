from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandler


class NoOpHandler(UAVChangeHandler):
    name = "NoOp"

    def handle_new_uav(self, uav: UAV):
        raise NotImplementedError("NoOpHandler does not support adding UAVs")

    def handle_removed_uav(self, uav: UAV):
        raise NotImplementedError("NoOpHandler does not support removing UAVs")
