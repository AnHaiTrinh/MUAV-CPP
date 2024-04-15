import numpy as np

from src.core.cell import Cell, CellType
from src.core.uav import UAV


class Map:
    def __init__(self, cells: list[list[Cell]]):
        self.cells = cells
        self.height = len(cells)
        self.width = len(cells[0])

    @staticmethod
    def create_empty_map(width: int, height: int) -> "Map":
        cells = [
            [Cell(CellType.FREE, r, c) for r in range(width)] for c in range(height)
        ]
        return Map(cells)

    @staticmethod
    def from_numpy(array: np.ndarray) -> "Map":
        height, width = array.shape
        cells = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell(CellType(int(array[i, j])), i, j))
            cells.append(row)
        return Map(cells)

    def get_cell(self, r: int, c: int) -> Cell:
        return self.cells[r][c]

    def set_cell(self, r: int, c: int, cell_type: CellType) -> None:
        self.cells[r][c].cell_type = cell_type

    def to_numpy(self) -> np.ndarray:
        return np.array(
            [[cell.cell_type.value for cell in row] for row in self.cells],
            dtype=np.uint8,
        )

    def assign(self, r: int, c: int, uav: UAV) -> None:
        self.cells[r][c].assign = uav.name

    def __repr__(self):
        return "\n".join("\t".join(str(cell) for cell in row) for row in self.cells)

    def __str__(self):
        return "\n".join(
            "\t".join(str(cell.cell_type.value) for cell in row) for row in self.cells
        )