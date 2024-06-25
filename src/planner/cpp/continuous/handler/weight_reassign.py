from collections import deque

import numpy as np

from src.core.uav import UAV
from src.core.map import Map
from src.planner.cpp.continuous.handler.base import UAVChangeHandler
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory
from src.planner.cpp.utils import (
    construct_adj_list,
    dfs_weighted_tree,
    get_adjacent_cells,
    get_assign_count,
    map_to_assignment_matrix,
    transfer_area_subtree,
    transfer_concurrently,
)


class PropagationHandler(UAVChangeHandler):
    name = "Propagation"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.single_planner_name = kwargs.get("single_planner_name", "STC")

    def handle_new_uav(self, uav: UAV):
        assigned = map_to_assignment_matrix(self.map, self.uavs)
        self.uavs.append(uav)
        num_uavs = len(self.uavs)
        assigned[uav.r, uav.c] = num_uavs - 1
        self._transfer_bottom_up(assigned, num_uavs - 1)
        self._reassign(assigned)

    def handle_removed_uav(self, uav: UAV):
        uav_index = self.uavs.index(uav)

        assigned = map_to_assignment_matrix(self.map, self.uavs)

        self._transfer_top_down(assigned, uav_index)
        self.uavs.remove(uav)
        self._reassign(assigned)

    def _transfer_top_down(
        self, assignmnent_matrix: np.ndarray, changed_uav_idx: int
    ) -> None:
        """Modify `assignment_matrix` inplace"""
        num_uavs = len(self.uavs)

        adj_list = construct_adj_list(assignmnent_matrix)
        assign_count = get_assign_count(assignmnent_matrix, num_uavs)

        tree_adj_list, weights = dfs_weighted_tree(
            adj_list, assign_count, changed_uav_idx
        )

        area_reassign = assign_count[changed_uav_idx] // (num_uavs - 1)

        def amount_to_transfer(parent: int) -> int:
            amount = {child: weights[child][0] for child in tree_adj_list[parent]}
            total_node_count = sum(amount.values())
            nonlocal area_reassign
            for k in amount:
                amount[k] = round(amount[k] * area_reassign / total_node_count)
            return amount

        q = deque([changed_uav_idx])
        while q:
            u = q.popleft()
            transfer_to = amount_to_transfer(u)
            if transfer_to:
                transfer_concurrently(
                    u,
                    transfer_to,
                    assignmnent_matrix,
                    None if u == changed_uav_idx else (self.uavs[u].r, self.uavs[u].c),  # type: ignore
                )
            for node in transfer_to:
                q.append(node)

        assignmnent_matrix[assignmnent_matrix > changed_uav_idx] -= 1

    def _transfer_bottom_up(
        self, assignment_matrix: np.ndarray, changed_uav_idx: int
    ) -> None:
        """Modify `assignment_matrix` inplace"""
        num_uavs = len(self.uavs)
        target_cell_count = len(self.map.free_cells) / num_uavs

        adj_list = construct_adj_list(assignment_matrix)
        assign_count = get_assign_count(assignment_matrix, num_uavs)

        tree_adj_list, weights = dfs_weighted_tree(adj_list, assign_count, changed_uav_idx)  # type: ignore

        def diff(node: int) -> int:
            count, weight = weights[node]
            nonlocal target_cell_count
            return round(target_cell_count * count) - weight

        def handle(node: int):
            for neigh in sorted(tree_adj_list[node], key=diff):
                handle(neigh)
                transfer_amount = diff(neigh)
                if transfer_amount < 0:
                    transfer_area_subtree(
                        neigh,
                        node,
                        get_adjacent_cells(assignment_matrix, neigh, node),
                        -transfer_amount,
                        assignment_matrix,
                        (self.uavs[neigh].r, self.uavs[neigh].c),  # type: ignore
                    )

        handle(changed_uav_idx)

    def _reassign(self, assignment_matrix: np.ndarray) -> None:
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
