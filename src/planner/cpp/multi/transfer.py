from collections import deque
from itertools import cycle

import numpy as np

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.multi.single import MultiAsSingleCoveragePathPlanner
from src.planner.cpp.utils import get_partition, transfer_area_subtree, get_neighbors

_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0))


class AreaTransferringPlanner(MultiAsSingleCoveragePathPlanner):
    name = "Transfer"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.assigned = self._initial_assign()

        self.single_planner_name = kwargs.get("single_planner_name", "STC")
        self.max_iter = kwargs.get("max_iter", 50)
        self.uav_iter = cycle(range(len(self.uavs)))
        self.consecutive_failures = 0

    def assign(self) -> np.ndarray:
        iteration = 0
        while iteration < self.max_iter:
            partition = get_partition(self.assigned, self.num_uavs)

            node = next(self.uav_iter)
            neighbors = get_neighbors(self.assigned, partition[node])
            success = False
            for target_node in sorted(
                neighbors, key=lambda x: len(partition[x]), reverse=True
            ):
                receiver_count = len(partition[node])
                if receiver_count > self.target_cell_count:
                    continue
                sender_count = len(partition[target_node])
                diff = sender_count - receiver_count
                if diff < 1 or (diff == 1 and sender_count == self.target_cell_count + 1):
                    continue

                to_transfer = (diff + 1) >> 1
                init_pos = (self.uavs[target_node].r, self.uavs[target_node].c)  # type: ignore
                transferred = transfer_area_subtree(
                    target_node,
                    node,
                    neighbors[target_node],
                    to_transfer,
                    self.assigned,
                    init_pos,  # type: ignore
                )
                if transferred:
                    success = True
                    break

            if not success:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.num_uavs:
                    break
            else:
                self.consecutive_failures = 0
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
                if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == 0:
                    q.append(((nr, nc), label))

        return assigned - 1


if __name__ == "__main__":
    from src.core.utils import load_map_from_file
    from src.planner.cpp.utils import (
        get_assign_count,
        dfs_weighted_tree,
        construct_adj_list,
    )
    import time

    my_map = load_map_from_file("../../../../images_filled/Denver_0.png")
    NUM_UAVS = 8
    my_uavs = [UAV(name=f"UAV{i + 1}") for i in range(NUM_UAVS)]

    transfer = AreaTransferringPlanner(my_uavs, my_map)
    start = time.perf_counter()
    transfer.plan()
    print(f"Time: {time.perf_counter() - start}")
    assign_count = get_assign_count(transfer.assigned, NUM_UAVS)
    print(assign_count)

    adj_list = construct_adj_list(transfer.assigned)
    print({k: [_v for _v in v] for k, v in adj_list.items()})
    adj_list_weight, weights = dfs_weighted_tree(adj_list, assign_count, 0)  # type: ignore
    print(adj_list_weight)
    print(weights)
