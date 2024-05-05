from collections import deque, defaultdict

import numpy as np

from src.planner.cpp.continuous.planner import ContinuousCoveragePathPlanner
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory

_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0))


class AreaStealingPlanner(ContinuousCoveragePathPlanner):
    name = "Stealing"

    def __init__(self, uavs, _map, **kwargs):
        super().__init__(uavs, _map, **kwargs)
        self.assigned = self._initial_assign()

        self.single_planner_name = kwargs.get("single_planner_name", "STC")
        self.max_iter = kwargs.get("max_iter", 100)

        self.init_plan()

    def init_plan(self):
        row, col = self.assigned.shape
        equal = False
        iteration = 0
        while (not equal) and iteration < self.max_iter:
            equal = True
            assign_count = _get_assign_count(self.assigned)
            adj_list = _construct_adj_list(self.assigned)

            for node in sorted(adj_list, key=lambda x: assign_count[x]):
                candidates = adj_list[node]
                for target_node in sorted(candidates, key=lambda x: assign_count[x], reverse=True):
                    buyer = assign_count[node]
                    seller = assign_count[target_node]
                    diff = seller - buyer
                    if diff < 1 or (diff == 1 and seller == self.target_cell_count + 1):
                        continue

                    to_transfer = (diff + 1) // 2
                    init_pos = (self.uavs[target_node - 1].r, self.uavs[target_node - 1].c)
                    queue = deque(adj_list[target_node][node])
                    while queue and to_transfer > 0:
                        r, c = queue.popleft()
                        if self.assigned[r, c] == target_node and _is_connected(self.assigned, (r, c)):
                            if (r, c) == init_pos:
                                continue
                            self.assigned[r, c] = node
                            to_transfer -= 1
                            for _dr, _dc in _DIRS:
                                _nr, _nc = r + _dr, c + _dc
                                if (
                                        0 <= _nr < row
                                        and 0 <= _nc < col
                                        and self.assigned[_nr, _nc] == target_node
                                ):
                                    queue.append((_nr, _nc))

                    if to_transfer == (diff + 1) // 2:
                        continue

                    equal = False
                    break

                if not equal:
                    break

            iteration += 1

        for i, uav in enumerate(self.uavs):
            row_idx, col_idx = np.where(self.assigned == i + 1)
            for r, c in zip(row_idx, col_idx):
                self.map.assign(r, c, uav)

            planner = SingleCoveragePathPlannerFactory.get_planner(
                self.single_planner_name, self.map, uav
            )
            planner.plan()

    def _initial_assign(self) -> np.ndarray:
        """Assign using BFS with sources at each UAV's initial position."""
        q: deque[tuple[tuple[int, int], int]] = deque(
            ((uav.r, uav.c), i + 1) for i, uav in enumerate(self.uavs))  # type: ignore
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

        return assigned

    def new_uav_plan(self, uav_name: str) -> None:
        raise NotImplementedError("AreaStealingPlanner does not support adding new UAVs")

    def remove_uav_plan(self, uav_name: str) -> None:
        raise NotImplementedError("AreaStealingPlanner does not support removing UAVs")


def _get_assign_count(assigned: np.ndarray) -> dict[int, int]:
    _values, _counts = np.unique(assigned.astype(int), return_counts=True)
    return {value: count for value, count in zip(_values, _counts) if value > 0}


def _construct_adj_list(
    assigned: np.ndarray,
) -> dict[int, dict[int, set[tuple[int, int]]]]:
    """
    Construct adjacency list for the assigned matrix.
    Vertices: UAVs
    Edges: A set of cells adjacent to the other UAV
    :param assigned: assignment matrix
    :return: adjacency list of UAVs
    """
    row, col = assigned.shape
    _adj_list: dict[int, dict[int, set[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for _r in range(row):
        for _c in range(col):
            if assigned[_r, _c] == -1:
                continue
            for _dr, _dc in _DIRS[:2]:
                _nr, _nc = _r + _dr, _c + _dc
                if (
                    0 <= _nr < row
                    and 0 <= _nc < col
                    and 0 < assigned[_nr, _nc] != assigned[_r, _c]
                ):
                    _adj_list[assigned[_r, _c]][assigned[_nr, _nc]].add((_r, _c))  # type: ignore
                    _adj_list[assigned[_nr, _nc]][assigned[_r, _c]].add((_nr, _nc))  # type: ignore
    return _adj_list


def _is_connected(mat: np.ndarray, cell: tuple[int, int]) -> bool:
    """
    Check if removing `cell` from `mat` will result in a connected assignment.
    :param mat: assignment matrix
    :param cell: the cell to remove
    :return: True if connected, False otherwise
    """
    _row, _col = mat.shape
    _label = mat[cell]
    _r, _c = cell

    _neighbors: list[tuple[int, int] | None] = [None] * 4  # top, bottom, left, right
    if _r > 0 and mat[_r - 1, _c] == _label:
        _neighbors[0] = (_r - 1, _c)
    if _r < _row - 1 and mat[_r + 1, _c] == _label:
        _neighbors[1] = (_r + 1, _c)
    if _c > 0 and mat[_r, _c - 1] == _label:
        _neighbors[2] = (_r, _c - 1)
    if _c < _col - 1 and mat[_r, _c + 1] == _label:
        _neighbors[3] = (_r, _c + 1)

    # Check every pair of neighbors to see if they are still connected
    for _i in range(4):
        for _j in range(_i):
            if _neighbors[_i] and _neighbors[_j]:
                # Remove the label, check for connectivity then restore the label
                mat[cell] = -1
                connected = _dfs(mat, _neighbors[_i], _neighbors[_j])  # type: ignore
                mat[cell] = _label
                if not connected:
                    return False
    return True


def _dfs(mat: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> bool:
    row, col = mat.shape
    stack = [start]
    visited = set()
    assert mat[start] == mat[end]
    _label = mat[start]
    while stack:
        r, c = stack.pop()
        if (r, c) == end:
            return True
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for _dr, _dc in _DIRS:
            _nr, _nc = r + _dr, c + _dc
            if 0 <= _nr < row and 0 <= _nc < col and mat[_nr, _nc] == _label:
                stack.append((_nr, _nc))
    return False
