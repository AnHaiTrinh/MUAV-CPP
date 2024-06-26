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
    assign_count = np.zeros(size, dtype=int)
    for value, count in zip(values, counts):
        if value >= 0:
            assign_count[value] = count

    return assign_count


def construct_adj_list(
    assigned: np.ndarray,
) -> dict[int, set[int]]:
    """
    Construct adjacency list for the assigned matrix.
    The assigned matrix is assumed to be labeled from 0 and occupied cells are labeled < 0.
    :param assigned: assignment matrix
    :return: adjacency list of UAVs
    """
    row, col = assigned.shape
    adj_list: dict[int, set[int]] = defaultdict(set)
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
                    adj_list[assigned[r, c]].add(assigned[nr, nc])  # type: ignore
                    adj_list[assigned[nr, nc]].add(assigned[r, c])  # type: ignore
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


def _is_connected(
    mat: np.ndarray, start: tuple[int, int], end: tuple[int, int]
) -> bool:
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
    sender: int,
    receiver: int,
    neighbors: set[tuple[int, int]],
    transfer_amount: int,
    assigned: np.ndarray,
    init_seller_pos: tuple[int, int],
) -> int:
    """
    Transfer cells from seller to buyer.
    :param sender: The sending node (losing area)
    :param receiver: The receiving node (gaining area)
    :param neighbors: The cells belonging to the seller node adjacent to the buyer node
    :param transfer_amount: The ideal amount of cells to transfer
    :param assigned: The assignment matrix
    :param init_seller_pos: The original position for the seller node
    :return: The amount of cells successfully transferred
    """
    row, col = assigned.shape

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

    transferred = 0
    queue = deque(neighbors)
    while queue and transfer_amount > transferred:
        r, c = queue.popleft()
        if (r, c) == init_seller_pos:
            continue
        if strongly_connected((r, c), receiver) and _is_not_bridge(assigned, (r, c)):
            assigned[r, c] = receiver
            transferred += 1
            for dr, dc in _4_DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == sender:
                    queue.append((nr, nc))

    return transferred


def transfer_area_subtree(
    sender: int,
    receiver: int,
    neighbors: set[tuple[int, int]],
    transfer_amount: int,
    assigned: np.ndarray,
    init_seller_pos: tuple[int, int],
) -> int:
    """
    Transfer cells from seller to buyer.
    :param sender: The sending node (losing area)
    :param receiver: The receiving node (gaining area)
    :param neighbors: The cells belonging to the seller node adjacent to the buyer node
    :param transfer_amount: The ideal amount of cells to transfer
    :param assigned: The assignment matrix
    :param init_seller_pos: The original position for the seller node
    :return: The amount of cells successfully transferred
    """
    row, col = assigned.shape
    transferred = 0
    queue = deque(neighbors)
    while queue and transfer_amount > transferred:
        r, c = queue.popleft()
        if assigned[r, c] != sender or (r, c) == init_seller_pos:
            continue
        if _is_not_bridge(assigned, (r, c)):
            assigned[r, c] = receiver
            transferred += 1
            for dr, dc in _4_DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == sender:
                    queue.append((nr, nc))
        else:
            subtrees = _dfs_subtree(assigned, (r, c))
            transfer_subtrees = list(
                filter(lambda x: init_seller_pos not in x, subtrees)
            )
            if (
                sum(len(subtree) for subtree in transfer_subtrees)
                >= transfer_amount - transferred
            ):
                continue
            assigned[r, c] = receiver
            transferred += 1
            for subtree in transfer_subtrees:
                for cr, cc in subtree:
                    assigned[cr, cc] = receiver
                    transferred += 1
                    for cdr, cdc in _4_DIRS:
                        cnr, cnc = cr + cdr, cc + cdc
                        if (
                            0 <= cnr < row
                            and 0 <= cnc < col
                            and assigned[cnr, cnc] == sender
                        ):
                            queue.append((cnr, cnc))

    return transferred


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


def transfer_concurrently(
    from_node: int,
    to_nodes: dict[int, int],
    assigned: np.ndarray,
    from_node_init_pos: tuple[int, int] | None,
) -> None:
    """
    Concurrently transfer from node to all of `to_nodes`.
    :param from_node: Node to tranfer area from
    :param to_nodes: Dict of nodes to transfer area to. Value is their desired transfer amount
    :param assigned: Assignment matrix
    :param from_node_init_pos: The initial position of `from_node` to avoid. If None then take all of its area.
    """
    row, col = assigned.shape
    transferred = {node: 0 for node in to_nodes}
    queues = {
        node: deque(get_adjacent_cells(assigned, from_node, node)) for node in to_nodes
    }
    while queues:
        for node in to_nodes:
            if node not in queues:
                continue
            if from_node_init_pos is None and len(queues) == 1:
                assigned[assigned == from_node] = node
                del queues[node]
                break
            q = queues[node]
            while q:
                r, c = q.popleft()
                if (r, c) == from_node_init_pos or assigned[r, c] != from_node:
                    continue
                if _is_not_bridge(assigned, (r, c)):
                    assigned[r, c] = node
                    transferred[node] += 1
                    for dr, dc in _4_DIRS:
                        nr, nc = r + dr, c + dc
                        if (
                            0 <= nr < row
                            and 0 <= nc < col
                            and assigned[nr, nc] == from_node
                        ):
                            q.append((nr, nc))
                    break
                else:
                    subtrees = _dfs_subtree(assigned, (r, c))
                    transfer_subtrees = list(
                        filter(lambda x: from_node_init_pos not in x, subtrees)
                    )
                    if (
                        sum(len(subtree) for subtree in transfer_subtrees)
                        >= to_nodes[node] - transferred[node]
                    ):
                        continue
                    assigned[r, c] = node
                    transferred[node] += 1
                    for subtree in transfer_subtrees:
                        for cr, cc in subtree:
                            assigned[cr, cc] = node
                            transferred[node] += 1
                            for cdr, cdc in _4_DIRS:
                                cnr, cnc = cr + cdr, cc + cdc
                                if (
                                    0 <= cnr < row
                                    and 0 <= cnc < col
                                    and assigned[cnr, cnc] == from_node
                                ):
                                    q.append((cnr, cnc))
                    break

            if transferred[node] >= to_nodes[node] or not q:
                del queues[node]


def dfs_weighted_tree(
    adj_list: dict[int, Iterable[int]],
    node_weights: np.ndarray[int],
    root: int,
) -> tuple[dict[int, list[int]], dict[int, tuple[int, int]]]:
    """
    Run Depth First Search on the adjacency list to get the weighted tree
    :param adj_list: adjacency list of nodes
    :param node_weights: the weight of each node
    :param root: root node
    :return: Adjacency list of DFS tree, Dict of each node to the number of children and theirs weights
    """
    adj_list_weighted: dict[int, list[int]] = defaultdict(list)
    visited: set[int] = set()

    q = deque([(root, None)])
    while q:
        node, parent = q.popleft()
        if node in visited:
            continue

        visited.add(node)
        if parent is not None:
            adj_list_weighted[parent].append(node)  # type: ignore

        for neighbor in adj_list[node]:
            if neighbor != parent:
                q.append((neighbor, node))  # type: ignore

    node_weight: dict[int, tuple[int, int]] = {}

    def transverse(_node: int) -> tuple[int, int]:
        count = 1
        weight = node_weights[_node]
        for child in adj_list_weighted[_node]:
            child_count, child_weight = transverse(child)
            count += child_count
            weight += child_weight
        node_weight[_node] = (count, weight)
        return count, weight

    transverse(root)
    return adj_list_weighted, node_weight


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


def get_adjacent_cells(
    assigned: np.ndarray, from_label: int, to_label: int
) -> set[tuple[int, int]]:
    row, col = assigned.shape
    adjacent_cells = set()
    for r in range(row):
        for c in range(col):
            if assigned[r, c] == from_label:
                for dr, dc in _4_DIRS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < row and 0 <= nc < col and assigned[nr, nc] == to_label:
                        adjacent_cells.add((r, c))
                        break
    return adjacent_cells
