from collections import deque

import numpy as np

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandler
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory
from src.planner.cpp.utils import get_partition, map_to_assignment_matrix, get_neighbors

_DIRS = ((0, 1), (0, -1), (1, 0), (-1, 0))


class VoronoiHandler(UAVChangeHandler):
    name = "Voronoi"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)

        self.single_planner_name = kwargs.get("single_planner_name", "STC")

    def handle_new_uav(self, uav: UAV) -> None:
        self.uavs.append(uav)
        assigned = map_to_assignment_matrix(self.map, self.uavs)
        assigned[uav.r, uav.c] = len(self.uavs) - 1
        labels = self._expand(assigned, (uav.r, uav.c))  # type: ignore
        self.voronoi_reassign(assigned, labels)

    def handle_removed_uav(self, uav: UAV) -> None:
        num_uavs = len(self.uavs)
        uav_index = self.uavs.index(uav)

        assigned = map_to_assignment_matrix(self.map, self.uavs)
        partition = get_partition(assigned, num_uavs)
        neighbors = get_neighbors(assigned, partition[uav_index])
        labels = list(neighbors.keys())

        transfer_to = labels[0]
        assigned[assigned == uav_index] = transfer_to
        assigned[assigned > uav_index] -= 1

        self.uavs.pop(uav_index)
        self.voronoi_reassign(
            assigned, [label if label <= uav_index else label - 1 for label in labels]
        )

    def voronoi_reassign(
        self, assignment_matrix: np.ndarray, labels: list[int]
    ) -> None:
        """Modify assignment_matrix inplace"""
        row, col = assignment_matrix.shape
        partitions = get_partition(assignment_matrix, len(self.uavs))
        cells: set[tuple[int, int]] = set()
        for label in labels:
            cells = cells.union(partitions[label])

        q = deque([(self.uavs[label].r, self.uavs[label].c, label) for label in labels])
        while q:
            r, c, label = q.popleft()
            if (r, c) not in cells:
                continue
            cells.remove((r, c))
            assignment_matrix[r, c] = label
            for dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and (nr, nc) in cells:
                    q.append((nr, nc, label))

        for i, uav in enumerate(self.uavs):
            row_idx, col_idx = np.where(assignment_matrix == i)
            for r, c in zip(row_idx, col_idx):
                self.map.assign(r, c, uav)

        for uav in self.uavs:
            single_planner = SingleCoveragePathPlannerFactory.get_planner(
                self.single_planner_name,
                self.map,
                uav,
            )
            single_planner.plan()

    def _expand(
        self, assignment_matrix: np.ndarray, start: tuple[int, int]
    ) -> list[int]:
        """Run BFS from start cell to get all labels of uav in the adjacent area"""
        row, col = assignment_matrix.shape
        ideal_area = len(self.map.free_cells) // len(self.uavs)
        labels = set()
        visited = set()
        q = deque([start])
        while q and ideal_area > 0:
            r, c = q.popleft()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            ideal_area -= 1
            for dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col:
                    label = assignment_matrix[nr, nc]
                    if label >= 0:
                        labels.add(assignment_matrix[nr, nc])  # type: ignore
                        q.append((nr, nc))
        return list(labels)  # type: ignore
