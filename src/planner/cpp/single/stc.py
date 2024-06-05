from collections import defaultdict

from src.core.cell import Cell, CellType
from src.planner.cpp.single.planner import SingleCoveragePathPlanner
from src.core.map import Map
from src.core.uav import UAV


class STCPlanner(SingleCoveragePathPlanner):
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
        mst_algo = f'_{kwargs.get("mst_algo", "kruskal")}'
        if not hasattr(self, mst_algo):
            raise KeyError(f"Unsupported MST algorithm {mst_algo}")
        self.mst_algo = getattr(self, mst_algo)
        self.area = Map(cells)
        self.dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    @staticmethod
    def _cell_to_mega_cell(cell: tuple[int, int]) -> tuple[int, int]:
        return cell[0] >> 1, cell[1] >> 1

    def plan(self) -> None:
        if self.uav.r is None or self.uav.c is None:
            raise ValueError("UAV coordinates are not set")
        height, width = self.area.height, self.area.width
        start_pos = (self.uav.r, self.uav.c)
        coverage_path: list[tuple[int, int]] = [start_pos]
        visited: set[tuple[int, int]] = {start_pos}

        adj_list = self.mst_algo(start_pos)

        def is_valid_movement(
            current: tuple[int, int],
            direction: tuple[int, int],
        ) -> bool:
            current_r, current_c = current
            dx, dy = direction
            next_r, next_c = current_r + dx, current_c + dy
            if next_r == -1 or next_r == height or next_c == -1 or next_c == width:
                return False
            _next = (next_r, next_c)
            if _next in visited:
                return False

            current_mega_cell = self._cell_to_mega_cell(current)
            next_mega_cell = self._cell_to_mega_cell(_next)
            if current_mega_cell != next_mega_cell:
                return next_mega_cell in adj_list[current_mega_cell]

            def get_neighbor_mega_cell(
                curr: tuple[int, int], nxt: tuple[int, int]
            ) -> tuple[int, int]:
                mega_r, mega_c = self._cell_to_mega_cell(curr)
                current_and_next = {curr, nxt}
                if current_and_next == {
                    (mega_r << 1, mega_c << 1),
                    (mega_r << 1, (mega_c << 1) + 1),
                }:
                    return mega_r - 1, mega_c
                if current_and_next == {
                    (mega_r << 1, mega_c << 1),
                    ((mega_r << 1) + 1, mega_c << 1),
                }:
                    return mega_r, mega_c - 1
                if current_and_next == {
                    ((mega_r << 1) + 1, mega_c << 1),
                    ((mega_r << 1) + 1, (mega_c << 1) + 1),
                }:
                    return mega_r + 1, mega_c

                return mega_r, mega_c + 1

            neighbor_mega_cell = get_neighbor_mega_cell(current, _next)
            return not (neighbor_mega_cell in adj_list[current_mega_cell])

        current_pos = start_pos
        last_dir = (1, 0)
        stop = False
        while not stop:
            stop = True
            for d in self.dirs:
                if is_valid_movement(current_pos, d):
                    next_pos = (current_pos[0] + d[0], current_pos[1] + d[1])
                    visited.add(next_pos)
                    last_coverage_pos = coverage_path[-1]
                    if last_coverage_pos == current_pos:
                        if self.area.get_cell(*next_pos).cell_type == CellType.FREE:
                            coverage_path.append(next_pos)
                        else:
                            symmetric_next_pos = self._symmetric_cell(next_pos, d)
                            if (
                                self.area.get_cell(*symmetric_next_pos).cell_type
                                == CellType.FREE
                            ):
                                coverage_path.append(symmetric_next_pos)
                    else:
                        if last_coverage_pos == self._symmetric_cell(current_pos, d):
                            if self.area.get_cell(*next_pos).cell_type == CellType.FREE:
                                coverage_path.append(next_pos)
                            else:
                                next_coverage_pos = (
                                    last_coverage_pos[0] + d[0],
                                    last_coverage_pos[1] + d[1],
                                )
                                if (
                                    self.area.get_cell(*next_coverage_pos).cell_type
                                    == CellType.FREE
                                ):
                                    coverage_path.append(next_coverage_pos)
                        elif last_coverage_pos == self._symmetric_cell(
                            current_pos, last_dir
                        ):
                            if next_pos != last_coverage_pos:
                                next_coverage_pos = (
                                    current_pos[0] + last_dir[0],
                                    current_pos[1] + last_dir[1],
                                )
                                if (
                                    self.area.get_cell(*next_coverage_pos).cell_type
                                    == CellType.FREE
                                ):
                                    coverage_path.append(next_coverage_pos)
                                if (
                                    self.area.get_cell(*next_pos).cell_type
                                    == CellType.FREE
                                ):
                                    coverage_path.append(next_pos)
                                else:
                                    symmetric_next_pos = self._symmetric_cell(
                                        next_pos, d
                                    )
                                    if (
                                        self.area.get_cell(
                                            *symmetric_next_pos
                                        ).cell_type
                                        == CellType.FREE
                                    ):
                                        coverage_path.append(symmetric_next_pos)
                    current_pos = next_pos
                    last_dir = d
                    stop = False
                    break

        coverage_trajectory = [
            self.area.get_cell(*pos) for pos in _deduplicate_path(coverage_path)
        ]
        self.uav.update_trajectory(coverage_trajectory)

    def _kruskal(
        self, start_cell: tuple[int, int]
    ) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        Minimum Spanning Tree of Mega Graph using Kruskal Algorithm
        :param start_cell: the starting cell
        :return: Adjacency list of the MST in the mega graph
        """

        class UnionFind:
            def __init__(self, free_cells: list[tuple[int, int]]):
                self.parents = {free_cell: free_cell for free_cell in free_cells}
                self.ranks = {free_cell: 0 for free_cell in free_cells}
                self.n_components = len(free_cells)

            def find(self, cell: tuple[int, int]) -> tuple[int, int]:
                if self.parents[cell] != cell:
                    self.parents[cell] = self.find(self.parents[cell])
                return self.parents[cell]

            def union(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> bool:
                root1, root2 = self.find(cell1), self.find(cell2)
                if root1 == root2:
                    return False
                if self.ranks[root1] < self.ranks[root2]:
                    root1, root2 = root2, root1
                self.parents[root2] = root1
                self.ranks[root1] += self.ranks[root1] == self.ranks[root2]
                self.n_components -= 1
                return True

        start_mega_cell = self._cell_to_mega_cell(start_cell)
        assert self._mega_cell_type(start_mega_cell) == CellType.FREE

        all_free_mega_cells: list[tuple[int, int]] = []
        for r in range(self.area.height >> 1):
            for c in range(self.area.width >> 1):
                if self._mega_cell_type((r, c)) == CellType.FREE:
                    all_free_mega_cells.append((r, c))

        uf = UnionFind(all_free_mega_cells)
        adj_list = defaultdict(list)
        for mega_cell in all_free_mega_cells:
            neighbors, _ = self._neighbor(mega_cell)
            for neighbor in neighbors:
                if uf.union(mega_cell, neighbor):
                    adj_list[mega_cell].append(neighbor)
                    adj_list[neighbor].append(mega_cell)
                    if uf.n_components == 1:
                        return adj_list

        for mega_cell in all_free_mega_cells:
            _, secondary_neighbors = self._neighbor(mega_cell)
            for secondary_neighbor in secondary_neighbors:
                if uf.union(mega_cell, secondary_neighbor):
                    adj_list[mega_cell].append(secondary_neighbor)
                    adj_list[secondary_neighbor].append(mega_cell)
                    if uf.n_components == 1:
                        return adj_list

        if uf.n_components == 1:
            return adj_list
        raise ValueError("Graph is disconnected")

    def _dfs(
        self, start_cell: tuple[int, int]
    ) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        Minimum Spanning Tree of Mega Graph using Depth First Search
        :param start_cell: the starting cell
        :return: the path in the Mega Graph
        """
        start_mega_cell = self._cell_to_mega_cell(start_cell)
        assert self._mega_cell_type(start_mega_cell) == CellType.FREE

        parents: dict[tuple[int, int], tuple[int, int] | None] = {}
        stack: list[tuple[tuple[int, int], tuple[int, int] | None]] = [
            (start_mega_cell, None)
        ]
        while stack:
            current, parent = stack.pop()
            if current in parents:
                continue
            parents[current] = parent
            neighbors, secondary_neighbors = self._neighbor(current)
            for neighbor in neighbors + secondary_neighbors:
                stack.append((neighbor, current))

        adj_list = defaultdict(list)
        for mega_cell, parent in parents.items():
            if parent is not None:
                adj_list[mega_cell].append(parent)
                adj_list[parent].append(mega_cell)
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
        Secondary neighbors are adjacent mega cell not completely blocked by occupied cells. For example:
        curr... 0 | 0 ...nei
        curr... 1 | 1 ...nei
        :param mega_cell: Current mega cell
        :return: neighbors and secondary neighbors
        """
        neighbors: list[tuple[int, int]] = []
        secondary_neighbors: list[tuple[int, int]] = []

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
            nxt_contacting_cells = (
                self.area.get_cell(
                    contacting_cells[0].r + dr, contacting_cells[0].c + dc
                ),
                self.area.get_cell(
                    contacting_cells[1].r + dr, contacting_cells[1].c + dc
                ),
            )
            if any(
                cell1.cell_type == CellType.FREE and cell2.cell_type == CellType.FREE
                for cell1, cell2 in zip(contacting_cells, nxt_contacting_cells)
            ):
                secondary_neighbors.append(nxt)
            if all(
                cell.cell_type == CellType.FREE
                for cell in contacting_cells + nxt_contacting_cells
            ):
                neighbors.append(nxt)
        return neighbors, secondary_neighbors

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

    def _symmetric_cell(
        self, cell: tuple[int, int], direction: tuple[int, int]
    ) -> tuple[int, int]:
        """
        The symmetric cell is defined as the cell that is symmetric to the current cell in its mega cell
        with respect to the movement direction. There are two symmetric axes: vertical and horizontal.
        vertical axis
        :param cell: A cell in the original area
        :param direction: One of four movements (up, down, left, right)
        :return: The symmetric cell
        """
        mega_cell = self._cell_to_mega_cell(cell)
        if direction == (-1, 0) or direction == (1, 0):  # Vertical
            if cell == self._top_left(mega_cell).coordinate:
                return self._top_right(mega_cell).coordinate
            if cell == self._top_right(mega_cell).coordinate:
                return self._top_left(mega_cell).coordinate
            if cell == self._bottom_left(mega_cell).coordinate:
                return self._bottom_right(mega_cell).coordinate
            if cell == self._bottom_right(mega_cell).coordinate:
                return self._bottom_left(mega_cell).coordinate
        else:  # Horizontal
            if cell == self._top_left(mega_cell).coordinate:
                return self._bottom_left(mega_cell).coordinate
            if cell == self._top_right(mega_cell).coordinate:
                return self._bottom_right(mega_cell).coordinate
            if cell == self._bottom_left(mega_cell).coordinate:
                return self._top_left(mega_cell).coordinate
            if cell == self._bottom_right(mega_cell).coordinate:
                return self._top_right(mega_cell).coordinate

        raise ValueError(f"Invalid cell {cell} and direction {direction}")


def _deduplicate_path(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Deduplicate the path by removing the consecutive duplicate cells
    :param path: The path to deduplicate
    :return: The deduplicated path
    """
    deduplicated_path = [path[0]]
    for i in range(1, len(path)):
        if path[i] != path[i - 1]:
            deduplicated_path.append(path[i])
    return deduplicated_path
