import heapq
from collections import defaultdict

from src.core.cell import Cell
from src.planner.cpp.single.planner import SingleCPPPlanner
from src.core.map import Map
from src.core.uav import UAV


class SimpleSTCPlanner(SingleCPPPlanner):
    name = "STC"

    def __init__(self, area: Map, uav: UAV, **kwargs):
        super().__init__(area, uav, **kwargs)
        self.dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def plan(self) -> None:
        def cell_to_mega_cell(cell_x: int, cell_y: int) -> tuple[int, int]:
            return cell_x >> 1, cell_y >> 1

        if self.uav.r is None or self.uav.c is None:
            raise ValueError("UAV coordinates are not set")
        height, width = self.area.height, self.area.width
        start_pos = (self.uav.r, self.uav.c)
        coverage_path: list[tuple[int, int]] = [start_pos]
        visited: set[tuple[int, int]] = {start_pos}

        mega_area = self._construct_mega_graph()
        adj_list = self._mst(
            mega_area.get_cell(*cell_to_mega_cell(self.uav.r, self.uav.c)), mega_area
        )

        def is_valid_movement(
            current: tuple[int, int], direction: tuple[int, int]
        ) -> bool:
            current_x, current_y = current
            dx, dy = direction
            next_x, next_y = current_x + dx, current_y + dy
            if next_x == -1 or next_x == height or next_y == -1 or next_y == width:
                return False
            next = (next_x, next_y)
            if next in visited:
                return False

            current_mega_cell = cell_to_mega_cell(*current)
            next_mega_cell = cell_to_mega_cell(*next)
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
                current, next, current_mega_cell
            )
            return not (neighbor_mega_cell in adj_list[current_mega_cell])

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

    def _construct_mega_graph(self) -> Map:
        height, width = self.area.height, self.area.width
        mega_cells = []
        for r in range(height >> 1):
            mega_row = []
            for c in range(width >> 1):
                # Assuming all four cells in a mega cell are homogeneous
                cell = self.area.get_cell(r << 1, c << 1)
                mega_row.append(Cell(cell.cell_type, cell.r, cell.c, cell.assign))
            mega_cells.append(mega_row)
        return Map(mega_cells)

    def _mst(
            self, start_cell: Cell, graph: Map
    ) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        Minimum Spanning Tree algorithm
        :return: Adjacency list of the MST
        """
        assignee = start_cell.assign
        if not assignee:
            raise ValueError("Start cell is not assigned to any UAV")
        heap: list[tuple[int, tuple[int, int], tuple[int, int] | None]] = [
            (0, (start_cell.r, start_cell.c), None)
        ]  # (cost, now, parent)
        parents = {}
        while heap:
            _, now, parent = heapq.heappop(heap)
            if now in parents:
                continue
            parents[now] = parent
            now_x, now_y = now
            for dx, dy in self.dirs:
                new_x, new_y = now_x + dx, now_y + dy
                new = (new_x, new_y)
                if 0 <= new_x < graph.height and 0 <= new_y < graph.width:
                    if (
                            new not in parents
                            and graph.get_cell(new_x, new_y).assign == assignee
                    ):
                        heapq.heappush(heap, (1, new, now))

        adjacency_list = defaultdict(list)
        for child, parent in parents.items():
            if parent is None:
                continue
            adjacency_list[child].append(parent)
            adjacency_list[parent].append(child)
        return adjacency_list
