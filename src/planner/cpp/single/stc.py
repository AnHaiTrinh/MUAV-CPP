from collections import defaultdict

from src.core.cell import Cell, CellType
from src.planner.cpp.single.planner import SingleCPPPlanner
from src.core.map import Map
from src.core.uav import UAV


class STCPlanner(SingleCPPPlanner):
    name = "STC"

    def __init__(self, area: Map, uav: UAV, **kwargs):
        super().__init__(area, uav, **kwargs)
        # Apply uav's name as a mask to the area
        # Only cells assigned the same name as the uav will be considered as free, otherwise occupied
        assignee = uav.name
        cells = []
        for cell_row in area.cells:
            row = []
            for cell in cell_row:
                if cell.cell_type == CellType.FREE and cell.assign == assignee:
                    row.append(Cell(CellType.FREE, cell.r, cell.c))
                else:
                    row.append(Cell(CellType.OCCUPIED, cell.r, cell.c))
            cells.append(row)
        self.area = Map(cells)
        self.dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.move_dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def plan(self) -> None:
        if self.uav.r is None or self.uav.c is None:
            raise ValueError("UAV coordinates are not set")
        height, width = self.area.height, self.area.width
        start_pos = (self.uav.r, self.uav.c)
        coverage_path: list[tuple[int, int]] = [start_pos]
        visited: set[tuple[int, int]] = {start_pos}

        def cell_to_mega_cell(r: int, c: int) -> tuple[int, int]:
            return r >> 1, c >> 1

        mega_graph = self._construct_mega_graph()
        adj_list = _dfs(cell_to_mega_cell(*start_pos), mega_graph)
        print(adj_list)

        def is_valid_movement(
            current: tuple[int, int], direction: tuple[int, int]
        ) -> bool:
            current_x, current_y = current
            dx, dy = direction
            next_x, next_y = current_x + dx, current_y + dy
            if next_x == -1 or next_x == height or next_y == -1 or next_y == width:
                return False
            _next = (next_x, next_y)
            if _next in visited:
                return False

            current_mega_cell = cell_to_mega_cell(*current)
            next_mega_cell = cell_to_mega_cell(*_next)
            if current_mega_cell != next_mega_cell:
                return next_mega_cell in adj_list[current_mega_cell]

            def get_neighbor_mega_cell(
                curr: tuple[int, int], nxt: tuple[int, int], mega_cell: tuple[int, int]
            ) -> tuple[int, int]:
                mega_x, mega_y = mega_cell
                current_and_next = {curr, nxt}
                if current_and_next == {
                    (mega_x << 1, mega_y << 1),
                    (mega_x << 1, (mega_y << 1) + 1),
                }:
                    return mega_x - 1, mega_y
                if current_and_next == {
                    (mega_x << 1, mega_y << 1),
                    ((mega_x << 1) + 1, mega_y << 1),
                }:
                    return mega_x, mega_y - 1
                if current_and_next == {
                    ((mega_x << 1) + 1, mega_y << 1),
                    ((mega_x << 1) + 1, (mega_y << 1) + 1),
                }:
                    return mega_x + 1, mega_y

                return mega_x, mega_y + 1

            neighbor_mega_cell = get_neighbor_mega_cell(
                current, _next, current_mega_cell
            )
            return not (neighbor_mega_cell in adj_list[current_mega_cell])

        # def adjust_movement(current: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
        #     current_x, current_y = current
        #     dx, dy = direction
        #     next_x, next_y = current_x + dx, current_y + dy
        #     current_mega_cell = cell_to_mega_cell(*current)
        #     next_mega_cell = cell_to_mega_cell(next_x, next_y)
        #     if current_mega_cell != next_mega_cell:
        #         def get_neighbor_mega_cell(
        #             curr: tuple[int, int], nxt: tuple[int, int], mega_cell: tuple[int, int]
        #         ) -> tuple[int, int]:
        #             mega_x, mega_y = mega_cell
        #             current_and_next = {curr, nxt}
        #             if current_and_next == {
        #                 (mega_x << 1, mega_y << 1),
        #                 (mega_x << 1, (mega_y << 1) + 1),
        #             }:
        #                 return mega_x - 1, mega_y
        #             if current_and_next == {
        #                 (mega_x << 1, mega_y << 1),
        #                 ((mega_x << 1) + 1, mega_y << 1),
        #             }:
        #                 return mega_x, mega_y - 1
        #             if current_and_next == {
        #                 ((mega_x << 1) + 1, mega_y << 1),
        #                 ((mega_x << 1) + 1, (mega_y << 1) + 1),
        #             }:
        #                 return mega_x + 1, mega_y
        #
        #             return mega_x, mega_y + 1
        #
        #         neighbor_mega_cell = get_neighbor_mega_cell(
        #             current, (next_x, next_y), current_mega_cell
        #         )
        #         neighbor_x, neighbor_y = neighbor_mega_cell
        #         return (
        #             (neighbor_x << 1) + 1,
        #             (neighbor_y << 1) + 1,
        #         )
        #     return next_x, next_y

        current_pos = start_pos
        stop = False
        while not stop:
            stop = True
            for d in self.dirs:
                if is_valid_movement(current_pos, d):
                    next_pos = (current_pos[0] + d[0], current_pos[1] + d[1])
                    visited.add(next_pos)
                    coverage_path.append(next_pos)
                    current_pos = next_pos
                    stop = False
                    break

        coverage_trajectory = [self.area.get_cell(*pos) for pos in coverage_path]
        self.uav.update_trajectory(coverage_trajectory)

    def _construct_mega_graph(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        Construct the Mega Graph
        :return: Adjacency list of the Mega Graph
        """
        adj_list: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        all_free_cells = [
            (r, c)
            for r in range(self.area.height >> 1)
            for c in range(self.area.width >> 1)
            if self._mega_cell_type((r, c)) == CellType.FREE
        ]
        # First add all preferred edges
        for cell in all_free_cells:
            neighbors, _ = self._neighbor(cell)
            if neighbors:
                adj_list[cell].extend(neighbors)

        # Add other edges to make the graph connected
        for cell in all_free_cells:
            if cell not in adj_list:
                _, unfavorable_neighbors = self._neighbor(cell)
                adj_list[cell].extend(unfavorable_neighbors)
                for neigh in unfavorable_neighbors:
                    adj_list[neigh].append(cell)

        return adj_list

    def _top_left(self, mega_cell_coordinate: tuple[int, int]) -> Cell:
        r, c = mega_cell_coordinate
        return self.area.get_cell(r << 1, c << 1)

    def _top_right(self, mega_cell_coordinate: tuple[int, int]) -> Cell:
        r, c = mega_cell_coordinate
        return self.area.get_cell(r << 1, (c << 1) + 1)

    def _bottom_left(self, mega_cell_coordinate: tuple[int, int]) -> Cell:
        r, c = mega_cell_coordinate
        return self.area.get_cell((r << 1) + 1, c << 1)

    def _bottom_right(self, mega_cell_coordinate: tuple[int, int]) -> Cell:
        r, c = mega_cell_coordinate
        return self.area.get_cell((r << 1) + 1, (c << 1) + 1)

    def _neighbor(
        self, mega_cell: tuple[int, int]
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """
        Get the neighbors and preferred neighbors of the given mega cell
        Neighbors are adjacent mega cells not blocked by any cell occupied. For example:
        curr... 0 | 0 ...nei
        curr... 0 | 0 ...nei
        Unfavorable neighbors are adjacent mega cell not completely blocked by occupied cells. For example:
        curr... 0 | 0 ...nei
        curr... 1 | 1 ...nei
        :param mega_cell: Current mega cell
        :return: neighbors and unfavorable neighbor
        """
        neighbors: list[tuple[int, int]] = []
        unfavorable_neighbors: list[tuple[int, int]] = []

        def get_contacting_cells(
            current_mega_cell: tuple[int, int], direction: tuple[int, int]
        ) -> tuple[Cell, Cell]:
            """
            Get the two cells that are contacting the neighboring mega cell in the given direction
            :param current_mega_cell: The current mega cell
            :param direction: One of four directions (up, down, left, right)
            :return: Two contacting cells
            """
            if direction == (-1, 0):
                return self._top_left(current_mega_cell), self._top_right(
                    current_mega_cell
                )
            if direction == (1, 0):
                return self._bottom_left(current_mega_cell), self._bottom_right(
                    current_mega_cell
                )
            if direction == (0, -1):
                return self._top_left(current_mega_cell), self._bottom_left(
                    current_mega_cell
                )
            if direction == (0, 1):
                return self._top_right(current_mega_cell), self._bottom_right(
                    current_mega_cell
                )
            raise ValueError(f"Invalid direction {direction}")

        height, width = self.area.height >> 1, self.area.width >> 1
        r, c = mega_cell
        for dr, dc in self.dirs:
            nxt_r, nxt_c = r + dr, c + dc
            if nxt_r < 0 or nxt_r >= height or nxt_c < 0 or nxt_c >= width:
                continue
            if self._mega_cell_type((nxt_r, nxt_c)) == CellType.OCCUPIED:
                continue
            nxt = (nxt_r, nxt_c)
            contacting_cells = get_contacting_cells(mega_cell, (dr, dc))
            nxt_contacting_cells = get_contacting_cells(nxt, (-dr, -dc))
            if any(
                cell.cell_type == CellType.FREE for cell in contacting_cells
            ) and any(cell.cell_type == CellType.FREE for cell in nxt_contacting_cells):
                unfavorable_neighbors.append(nxt)
            if all(
                cell.cell_type == CellType.FREE
                for cell in contacting_cells + nxt_contacting_cells
            ):
                neighbors.append(nxt)

        if unfavorable_neighbors is None:
            raise ValueError("Graph is disconnected")
        return neighbors, unfavorable_neighbors

    def _mega_cell_type(self, mega_cell: tuple[int, int]) -> CellType:
        children_cells = [
            self._top_left(mega_cell),
            self._top_right(mega_cell),
            self._bottom_left(mega_cell),
            self._bottom_right(mega_cell),
        ]

        # If any of the children cells is free, the mega cell is free
        # Otherwise, it is occupied
        cell_type = CellType.OCCUPIED
        for cell in children_cells:
            if cell.cell_type == CellType.FREE:
                cell_type = CellType.FREE
                break
        return cell_type


def _dfs(
    start_cell: tuple[int, int], adj_list: dict[tuple[int, int], list[tuple[int, int]]]
) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """
    Minimum Spanning Tree of Mega Graph using DFS
    :param start_cell: the starting mega cell
    :param adj_list: adjacency list of the Mega Graph
    :return: Adjacency list of the MST
    """
    stack: list[tuple[tuple[int, int], tuple[int, int] | None]] = [
        (start_cell, None)
    ]  # (now, parent)
    parents: dict[tuple[int, int], tuple[int, int] | None] = {}

    while stack:
        node, parent = stack.pop()
        if node in parents:
            continue
        parents[node] = parent
        for nei in adj_list[node]:
            if nei not in parents:
                stack.append((nei, node))

    adjacency_list = defaultdict(list)
    for child, parent in parents.items():
        if parent is None:
            continue
        adjacency_list[child].append(parent)
        adjacency_list[parent].append(child)
    return adjacency_list
