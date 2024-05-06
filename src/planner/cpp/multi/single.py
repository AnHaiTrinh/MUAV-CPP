from abc import ABC, abstractmethod

import numpy as np

from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.multi.planner import MultiCoveragePathPlanner
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory


class MultiAsSingleCoveragePathPlanner(MultiCoveragePathPlanner, ABC):
    name = "Single"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.single_planner_name = kwargs.get("single_planner", "STC")

    @abstractmethod
    def assign(self) -> np.ndarray:
        """
        Get the assignment matrix of uavs to cells
        :return: A 2D numpy array where the value at (i, j) is the index (0-index) of the uav assigned to it
                 Occupied cells are assigned any number < 0
        """
        pass

    def plan(self) -> None:
        assignment_matrix = self.assign()
        for i, uav in enumerate(self.uavs):
            row_idx, col_idx = np.where(assignment_matrix == i)
            for r, c in zip(row_idx, col_idx):
                self.map.assign(r, c, uav)

            single_planner = SingleCoveragePathPlannerFactory.get_planner(
                self.single_planner_name,
                self.map,
                uav,
            )
            single_planner.plan()


class SingleAsMultiCoveragePathPlanner(MultiAsSingleCoveragePathPlanner):
    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        assert len(uavs) == 1
        super().__init__(uavs, _map, **kwargs)

    def assign(self) -> np.ndarray:
        return -1 * self.map.to_numpy()
