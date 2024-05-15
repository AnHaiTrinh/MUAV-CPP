import numpy as np

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandler
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory
from src.planner.cpp.utils import get_partition, transfer_area, map_to_assignment_matrix, get_neighbors


class TransferHandler(UAVChangeHandler):
    name = "Transfer"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)

        self.single_planner_name = kwargs.get("single_planner_name", "STC")
        self.max_iter = kwargs.get("max_iter", 100)

    def handle_new_uav(self, uav: UAV):
        assigned = map_to_assignment_matrix(self.map, self.uavs)
        assigned[uav.r, uav.c] = len(self.uavs)
        self.uavs.append(uav)
        self.reassign(assigned)

    def handle_removed_uav(self, uav: UAV):
        num_uavs = len(self.uavs)
        uav_index = self.uavs.index(uav)

        # Transfer all cells assigned to uav to the uav with minimal number of cells
        assigned = map_to_assignment_matrix(self.map, self.uavs)
        partition = get_partition(assigned, num_uavs)
        neighbors = get_neighbors(assigned, partition[uav_index])
        
        transfer_to = min(neighbors, key=lambda x: len(partition[x]))
        assigned[assigned == uav_index] = transfer_to
        assigned[assigned > uav_index] -= 1

        self.uavs.remove(uav)
        self.reassign(assigned)

    def reassign(self, assignment_matrix: np.ndarray):
        self._transfer(assignment_matrix)
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

    def _transfer(self, assigned: np.ndarray):
        num_uavs = len(self.uavs)
        target_cell_count = len(self.map.free_cells) // num_uavs
        equal = False
        iteration = 0
        while (not equal) and iteration < self.max_iter:
            equal = True
            partition = get_partition(assigned, num_uavs)
            for node in sorted(range(num_uavs), key=lambda x: len(partition[x])):
                neighbors = get_neighbors(assigned, partition[node])
                for target_node in sorted(
                        neighbors, key=lambda x: len(partition[x]), reverse=True
                ):
                    buyer = len(partition[node])
                    seller = len(partition[target_node])
                    diff = seller - buyer
                    if diff < 1 or (diff == 1 and seller == target_cell_count + 1):
                        continue

                    to_transfer = (diff + 1) // 2
                    init_pos = (self.uavs[target_node].r, self.uavs[target_node].c)  # type: ignore
                    success = transfer_area(
                        target_node,
                        node,
                        neighbors[target_node],
                        to_transfer,
                        assigned,
                        init_pos,  # type: ignore
                    )
                    if not success:
                        continue

                    equal = False
                    break

                if not equal:
                    break

            iteration += 1
