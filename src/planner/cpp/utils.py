from collections import defaultdict

import numpy as np

from src.core.map import Map
from src.core.uav import UAV

_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def get_assign_count(assigned: np.ndarray, size: int) -> np.ndarray:
    values, counts = np.unique(assigned, return_counts=True)
    assign_count = np.zeros(size)
    for value, count in zip(values, counts):
        if value >= 0:
            assign_count[value] = count

    return assign_count


def construct_adj_list(
    assigned: np.ndarray,
) -> dict[int, dict[int, set[tuple[int, int]]]]:
    """
    Construct adjacency list for the assigned matrix.
    The assigned matrix is assumed to be labeled from 0 and occupied cells are labeled < 0.
    :param assigned: assignment matrix
    :return: adjacency list of UAVs
    Vertices: UAVs
    Edges: A set of cells adjacent to the other UAV
    """
    row, col = assigned.shape
    adj_list: dict[int, dict[int, set[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for r in range(row):
        for c in range(col):
            if assigned[r, c] < 0:
                continue
            for dr, dc in _DIRS[:2]:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < row
                    and 0 <= nc < col
                    and 0 < assigned[nr, nc] != assigned[r, c]
                ):
                    adj_list[assigned[r, c]][assigned[nr, nc]].add((r, c))  # type: ignore
                    adj_list[assigned[nr, nc]][assigned[r, c]].add((nr, nc))  # type: ignore
    return adj_list


def is_bridge(assigned: np.ndarray, cell: tuple[int, int]) -> bool:
    """
    Check if removing `cell` from `mat` will result in a connected assignment.
    :param assigned: assignment matrix
    :param cell: the cell to remove
    :return: True if connected, False otherwise
    """
    row, col = assigned.shape
    label = assigned[cell]
    r, c = cell

    neighbors: list[tuple[int, int] | None] = [None] * 4  # top, bottom, left, right
    if r > 0 and assigned[r - 1, c] == label:
        neighbors[0] = (r - 1, c)
    if r < row - 1 and assigned[r + 1, c] == label:
        neighbors[1] = (r + 1, c)
    if c > 0 and assigned[r, c - 1] == label:
        neighbors[2] = (r, c - 1)
    if c < col - 1 and assigned[r, c + 1] == label:
        neighbors[3] = (r, c + 1)

    # Check every pair of neighbors to see if they are still connected
    for i in range(4):
        for j in range(i):
            if neighbors[i] and neighbors[j]:
                # Remove the label, check for connectivity then restore the label
                assigned[cell] = -1
                connected = _dfs(assigned, neighbors[i], neighbors[j])  # type: ignore
                assigned[cell] = label
                if not connected:
                    return False
    return True


def _dfs(mat: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> bool:
    row, col = mat.shape
    stack = [start]
    visited = set()
    assert mat[start] == mat[end]
    label = mat[start]
    while stack:
        r, c = stack.pop()
        if (r, c) == end:
            return True
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in _DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < row and 0 <= nc < col and mat[nr, nc] == label:
                stack.append((nr, nc))
    return False


def convert_to_assignment_matrix(_map: Map, uavs: list[UAV]) -> np.ndarray:
    assigned = -1 * _map.to_numpy()
    uav_names = {uav.name: i for i, uav in enumerate(uavs)}
    for r in range(_map.height):
        for c in range(_map.width):
            if assigned[r, c] < 0:
                continue
            label = _map.get_cell(r, c).assign
            assigned[r, c] = uav_names[label]
    return assigned
