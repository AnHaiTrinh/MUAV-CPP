from enum import Enum

import numpy as np


class CellType(Enum):
    FREE = 0
    OCCUPIED = 1
    UAV = 2
    BASE = 3


class Cell:
    def __init__(self, cell_type: CellType, r: int, c: int):
        self.cell_type: CellType = cell_type
        self.r = r
        self.c = c

    def distance(self, other: "Cell") -> float:
        return np.sqrt(np.square(self.c - other.c) + np.square(self.r - other.r))

    def __str__(self):
        return f"Cell({self.cell_type.value}, {self.r}, {self.c})"


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

    def __repr__(self):
        return "\n".join("\t".join(str(cell) for cell in row) for row in self.cells)

    def __str__(self):
        return "\n".join(
            "\t".join(str(cell.cell_type.value) for cell in row) for row in self.cells
        )
