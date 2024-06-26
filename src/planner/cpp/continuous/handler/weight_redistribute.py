from collections import deque

import numpy as np

from misc.viz_map_assignee import save_uavs_and_map_info

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.continuous.handler.base import UAVChangeHandler
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory
from src.planner.cpp.utils import (
    transfer_area_subtree,
    map_to_assignment_matrix,
    construct_adj_list,
    dfs_weighted_tree,
    get_assign_count,
    get_partition,
    get_neighbors,
    get_adjacent_cells,
)


class WeightedRedistributeHandler(UAVChangeHandler):
    name = "W_Transfer"

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
        num_uavs = len(self.uavs)
        uav_index = self.uavs.index(uav)

        # Transfer all cells assigned to uav to the uav with minimal number of cells
        assigned = map_to_assignment_matrix(self.map, self.uavs)
        partition = get_partition(assigned, num_uavs)
        neighbors = get_neighbors(assigned, partition[uav_index])

        transfer_to = min(neighbors, key=lambda x: len(partition[x]))
        assigned[assigned == uav_index] = transfer_to
        assigned[assigned > uav_index] -= 1

        if transfer_to > uav_index:
            transfer_to -= 1
        self.uavs.remove(uav)
        self._transfer_top_down(assigned, transfer_to)
        self._reassign(assigned)

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

    def _transfer_top_down(self, assigned: np.ndarray, changed_uav_idx: int) -> None:
        """Modify `assigned` inplace"""
        num_uavs = len(self.uavs)
        target_cell_count = len(self.map.free_cells) / num_uavs

        adj_list = construct_adj_list(assigned)
        assign_count = get_assign_count(assigned, num_uavs)

        tree_adj_list, weights = dfs_weighted_tree(adj_list, assign_count, changed_uav_idx)  # type: ignore
        counter = 0
        save_uavs_and_map_info(self.uavs, assigned, f"remove_{counter}.json")

        def diff(node: int) -> int:
            count, weight = weights[node]
            nonlocal target_cell_count
            return round(target_cell_count * count) - weight

        q = deque([changed_uav_idx])
        while q:
            u = q.popleft()
            for v in sorted(tree_adj_list[u], key=diff):
                transfer_amount = diff(v)
                if transfer_amount < 0:
                    transfer_area_subtree(
                        v,
                        u,
                        get_adjacent_cells(assigned, v, u),
                        -transfer_amount,
                        assigned,
                        (self.uavs[v].r, self.uavs[v].c),  # type: ignore
                    )
                else:
                    transfer_area_subtree(
                        u,
                        v,
                        get_adjacent_cells(assigned, u, v),
                        transfer_amount,
                        assigned,
                        (self.uavs[u].r, self.uavs[u].c),  # type: ignore
                    )
                q.append(v)
                counter += 1
                save_uavs_and_map_info(self.uavs, assigned, f"remove_{counter}.json")

    def _transfer_bottom_up(self, assigned: np.ndarray, changed_uav_idx: int) -> None:
        """Modify `assigned` inplace"""
        num_uavs = len(self.uavs)
        target_cell_count = len(self.map.free_cells) / num_uavs

        adj_list = construct_adj_list(assigned)
        assign_count = get_assign_count(assigned, num_uavs)

        tree_adj_list, weights = dfs_weighted_tree(adj_list, assign_count, changed_uav_idx)  # type: ignore

        def diff(node: int) -> int:
            count, weight = weights[node]
            nonlocal target_cell_count
            return round(target_cell_count * count) - weight

        counter = 0
        save_uavs_and_map_info(self.uavs, assigned, f"add_{counter}.json")

        def handle(node: int):
            for neigh in sorted(tree_adj_list[node], key=diff):
                handle(neigh)
                transfer_amount = diff(neigh)
                if transfer_amount < 0:
                    transfer_area_subtree(
                        neigh,
                        node,
                        get_adjacent_cells(assigned, neigh, node),
                        -transfer_amount,
                        assigned,
                        (self.uavs[neigh].r, self.uavs[neigh].c),  # type: ignore
                    )
                else:
                    transfer_area_subtree(
                        node,
                        neigh,
                        get_adjacent_cells(assigned, node, neigh),
                        transfer_amount,
                        assigned,
                        (self.uavs[node].r, self.uavs[node].c),  # type: ignore
                    )
                nonlocal counter
                counter += 1
                save_uavs_and_map_info(self.uavs, assigned, f"add_{counter}.json")

        handle(changed_uav_idx)
