from collections import deque

import numpy as np

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.multi.single import MultiAsSingleCoveragePathPlanner
from src.planner.cpp.utils import get_assign_count, construct_adj_list, transfer_area

_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0))


class AreaTransferringPlanner(MultiAsSingleCoveragePathPlanner):
    name = "Transfer"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.assigned = self._initial_assign()

        self.single_planner_name = kwargs.get("single_planner_name", "STC")
        self.max_iter = kwargs.get("max_iter", 100)

    def assign(self) -> np.ndarray:
        equal = False
        iteration = 0
        while (not equal) and iteration < self.max_iter:
            equal = True
            assign_count = get_assign_count(self.assigned, self.num_uavs)
            adj_list = construct_adj_list(self.assigned)

            for node in sorted(adj_list, key=lambda x: assign_count[x]):
                candidates = adj_list[node]
                for target_node in sorted(
                    candidates, key=lambda x: assign_count[x], reverse=True
                ):
                    buyer = assign_count[node]
                    seller = assign_count[target_node]
                    diff = seller - buyer
                    if diff < 1 or (diff == 1 and seller == self.target_cell_count + 1):
                        continue

                    to_transfer = (diff + 1) // 2
                    init_pos = (self.uavs[target_node].r, self.uavs[target_node].c)  # type: ignore
                    success = transfer_area(
                        target_node,
                        node,
                        adj_list[target_node][node],
                        to_transfer,
                        self.assigned,
                        init_pos,  # type: ignore
                    )
                    if not success:
                        continue

                    equal = False
                    break

                if not equal:
                    break

            iteration += 1

        return self.assigned

    def _initial_assign(self) -> np.ndarray:
        """Assign using BFS with sources at each UAV's initial position."""
        q: deque[tuple[tuple[int, int], int]] = deque(
            ((uav.r, uav.c), i + 1) for i, uav in enumerate(self.uavs)  # type: ignore
        )  # type: ignore
        assigned = -1 * self.map.to_numpy()
        row, col = assigned.shape

        while q:
            (r, c), label = q.popleft()
            if assigned[r, c] > 0:
                continue
            assigned[r, c] = label
            for dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col:
                    if assigned[nr, nc] == 0:
                        q.append(((nr, nc), label))

        return assigned - 1


if __name__ == "__main__":
    from src.core.utils import load_map_from_file

    my_map = load_map_from_file("../../../../images_filled/London_2.png")

    my_uavs = [UAV(name=f"UAV{i + 1}") for i in range(8)]

    transfer = AreaTransferringPlanner(my_uavs, my_map)
    transfer.plan()
