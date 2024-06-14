from collections import deque

import numpy as np

from src.core.uav import UAV
from src.core.map import Map
from src.planner.cpp.multi.single import MultiAsSingleCoveragePathPlanner


class VoronoiCoveragePathPlanner(MultiAsSingleCoveragePathPlanner):
    name = "Voronoi"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.dirs = ((-1, 0), (0, -1), (0, 1), (1, 0))

    def assign(self) -> np.ndarray:
        assignment_matrix = -1 * self.map.to_numpy()
        row, col = assignment_matrix.shape
        q = deque([((uav.r, uav.c), i + 1) for i, uav in enumerate(self.uavs)])
        while q:
            (r, c), label = q.popleft()
            if assignment_matrix[r, c] > 0:
                continue
            assignment_matrix[r, c] = label
            for dr, dc in self.dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and assignment_matrix[nr, nc] == 0:
                    q.append(((nr, nc), label))
        return assignment_matrix - 1
