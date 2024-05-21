import random
from collections import defaultdict, deque
from collections.abc import Iterable

import numpy as np

from src.core.map import Map
from src.core.uav import UAV

random.seed(42069)
_4_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0))
_8_DIRS = ((-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1))


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
            for dr, dc in _4_DIRS[:2]:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < row
                    and 0 <= nc < col
                    and 0 < assigned[nr, nc] != assigned[r, c]
                ):
                    adj_list[assigned[r, c]][assigned[nr, nc]].add((r, c))  # type: ignore
                    adj_list[assigned[nr, nc]][assigned[r, c]].add((nr, nc))  # type: ignore
    return adj_list


def _is_not_bridge(assigned: np.ndarray, cell: tuple[int, int]) -> bool:
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

    # Remove the label, check for connectivity then restore the label
    assigned[cell] = -1
    # Check every pair of neighbors to see if they are still connected
    for i in range(4):
        for j in range(i):
            if neighbors[i] and neighbors[j]:
                connected = _is_connected(assigned, neighbors[i], neighbors[j])  # type: ignore
                if not connected:
                    assigned[cell] = label
                    return False

    assigned[cell] = label
    return True


def _is_connected(mat: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> bool:
    row, col = mat.shape
    q = deque([start])
    visited = set()
    assert mat[start] == mat[end]
    label = mat[start]
    while q:
        r, c = q.popleft()
        if (r, c) == end:
            return True
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in _4_DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < row and 0 <= nc < col and mat[nr, nc] == label:
                q.append((nr, nc))
    return False


def transfer_area(
    seller: int,
    buyer: int,
    neighbors: set[tuple[int, int]],
    transfer_amount: int,
    assigned: np.ndarray,
    init_seller_pos: tuple[int, int],
) -> bool:
    """
    Transfer cells from seller to buyer.
    :param seller: The seller node (losing area)
    :param buyer: The buyer node (gaining area)
    :param neighbors: The cells belonging to the seller node adjacent to the buyer node
    :param transfer_amount: The ideal amount of cells to transfer
    :param assigned: The assignment matrix
    :param init_seller_pos: The original position for the seller node
    :return: Whether the transfer was successful
    """
    row, col = assigned.shape
    amount = transfer_amount

    def strongly_connected(cell: tuple[int, int], label: int) -> bool:
        """
        Check if cell is connected to at least 1/4 of its neighbors with `label`(8-direction).
        """
        nonlocal row, col, assigned
        _r, _c = cell
        neighbor_count = new_label_neighbor_count = 0
        for _dr, _dc in _8_DIRS:
            _nr, _nc = _r + _dr, _c + _dc
            if 0 <= _nr < row and 0 <= _nc < col and assigned[_nr, _nc] >= 0:
                neighbor_count += 1
                if assigned[_nr, _nc] == label:
                    new_label_neighbor_count += 1
        return new_label_neighbor_count * 4 > neighbor_count

    queue = deque(neighbors)
    while queue and amount > 0:
        r, c = queue.popleft()
        if (r, c) == init_seller_pos:
            continue
        if _is_not_bridge(assigned, (r, c)) and strongly_connected((r, c), buyer):
            assigned[r, c] = buyer
            amount -= 1
            for dr, dc in _4_DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == seller:
                    queue.append((nr, nc))

    if amount == transfer_amount:
        return False

    return True


def transfer_area_subtree(
    seller: int,
    buyer: int,
    neighbors: set[tuple[int, int]],
    transfer_amount: int,
    assigned: np.ndarray,
    init_seller_pos: tuple[int, int],
):
    """
    Transfer cells from seller to buyer.
    :param seller: The seller node (losing area)
    :param buyer: The buyer node (gaining area)
    :param neighbors: The cells belonging to the seller node adjacent to the buyer node
    :param transfer_amount: The ideal amount of cells to transfer
    :param assigned: The assignment matrix
    :param init_seller_pos: The original position for the seller node
    :return: Whether the transfer was successful
    """
    row, col = assigned.shape
    amount = transfer_amount

    queue = deque(neighbors)
    while queue and amount > 0:
        r, c = queue.popleft()
        if assigned[r, c] == buyer or (r, c) == init_seller_pos:
            continue
        subtrees = _dfs_subtree(assigned, (r, c))
        if len(subtrees) == 1:
            assigned[r, c] = buyer
            amount -= 1
            for dr, dc in _4_DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == seller:
                    queue.append((nr, nc))
        else:
            transfer_subtrees = filter(lambda x: init_seller_pos not in x, subtrees)
            if sum(len(subtree) for subtree in transfer_subtrees) <= amount:
                break
            assigned[r, c] = buyer
            for subtree in transfer_subtrees:
                for cr, cc in subtree:
                    assigned[cr, cc] = buyer
                    amount -= 1
                    for cdr, cdc in _4_DIRS:
                        cnr, cnc = cr + cdr, cc + cdc
                        if 0 <= cnr < row and 0 <= cnc < col and assigned[cnr, cnc] == seller:
                            queue.append((cnr, cnc))

    if amount == transfer_amount:
        return False

    return True


def _dfs_subtree(mat: np.ndarray, root: tuple[int, int]) -> list[set[tuple[int, int]]]:
    """
    Run Depth First Search on mat starting from root.
    :param mat: matrix to run DFS on
    :param root: the coordinate of root _node
    :return: list of subtrees of `root` on the resulting DFS tree
    """
    _row, _col = mat.shape
    _label = mat[root]
    stack: list[tuple[tuple[int, int], set[tuple[int, int]]]] = []
    subtrees: list[set[tuple[int, int]]] = []
    visited = {root}
    _r, _c = root
    for _dr, _dc in _4_DIRS:
        _nr, _nc = _r + _dr, _c + _dc
        if 0 <= _nr < _row and 0 <= _nc < _col and mat[_nr, _nc] == _label:
            subtree: set[tuple[int, int]] = set()
            subtrees.append(subtree)
            stack.append(((_nr, _nc), subtree))

    while stack:
        _node, subtree = stack.pop()
        if _node in visited:
            continue
        visited.add(_node)
        subtree.add(_node)
        _r, _c = _node
        for _dr, _dc in _4_DIRS:
            _nr, _nc = _r + _dr, _c + _dc
            if 0 <= _nr < _row and 0 <= _nc < _col and mat[_nr, _nc] == _label:
                stack.append(((_nr, _nc), subtree))

    return [subtree for subtree in subtrees if subtree]


# def dfs_weighted_tree(adj_list: dict[int, Iterable[int]], root: int) -> dict[int, tuple[int, int]]:
#     """
#     Run Depth First Search on the adjacency list to get the weighted tree
#     :param adj_list: adjacency list of nodes
#     :param root: root node
#     :return: Adjacency list of DFS tree weighted by the number of child nodes
#     """
#    pass


def map_to_assignment_matrix(_map: Map, uavs: list[UAV]) -> np.ndarray:
    assigned = -1 * _map.to_numpy()
    uav_names = {uav.name: i for i, uav in enumerate(uavs)}
    for r in range(_map.height):
        for c in range(_map.width):
            if assigned[r, c] < 0:
                continue
            label = _map.get_cell(r, c).assign
            assigned[r, c] = uav_names[label]
    return assigned


def get_partition(assigned: np.ndarray, size: int) -> list[list[tuple[int, int]]]:
    partition: list[list[tuple[int, int]]] = [[] for _ in range(size)]
    for index, val in np.ndenumerate(assigned):
        if val >= 0:
            partition[val].append(index)
    return partition


def get_neighbors(
    assigned: np.ndarray, cells: list[tuple[int, int]]
) -> dict[int, set[tuple[int, int]]]:
    row, col = assigned.shape
    neighbors = defaultdict(set)
    label = assigned[cells[0]]
    for r, c in cells:
        for dr, dc in _4_DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < row and 0 <= nc < col and 0 <= assigned[nr, nc] != label:
                neighbors[assigned[nr, nc]].add((nr, nc))
    return neighbors
