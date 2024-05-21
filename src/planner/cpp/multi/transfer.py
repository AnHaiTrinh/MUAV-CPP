from collections import deque

import numpy as np

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.multi.single import MultiAsSingleCoveragePathPlanner
from src.planner.cpp.utils import get_partition, transfer_area, get_neighbors

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
            partition = get_partition(self.assigned, self.num_uavs)

            for node in sorted(range(self.num_uavs), key=lambda x: len(partition[x])):
                neighbors = get_neighbors(self.assigned, partition[node])
                for target_node in sorted(
                    neighbors, key=lambda x: len(partition[x]), reverse=True
                ):
                    buyer = len(partition[node])
                    if buyer > self.target_cell_count:
                        continue
                    # seller = len(partition[target_node])
                    # diff = seller - buyer
                    # if diff < 1 or (diff == 1 and seller == self.target_cell_count + 1):
                    #     continue

                    to_transfer = self.target_cell_count - buyer
                    init_pos = (self.uavs[target_node].r, self.uavs[target_node].c)  # type: ignore
                    success = transfer_area(
                        target_node,
                        node,
                        neighbors[target_node],
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
    from src.planner.cpp.utils import get_assign_count
    import time

    my_map = load_map_from_file("../../../../images_filled/Denver_0.png")
    NUM_UAVS = 8
    my_uavs = [UAV(name=f"UAV{i + 1}") for i in range(NUM_UAVS)]

    transfer = AreaTransferringPlanner(my_uavs, my_map)
    start = time.perf_counter()
    transfer.plan()
    print(f"Time: {time.perf_counter() - start}")
    print(get_assign_count(transfer.assigned, NUM_UAVS))
