from enum import Enum

import numpy as np


class CellType(Enum):
    FREE = 0
    OCCUPIED = 1
    UAV = 2
    BASE = 3


class Cell:
    def __init__(self, cell_type: CellType, r: int, c: int, assign: str = ""):
        self.cell_type: CellType = cell_type
        self.r = r
        self.c = c
        self.assign = assign

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.r, self.c

    def distance(self, other: "Cell") -> np.float64:
        return np.sqrt(np.square(self.c - other.c) + np.square(self.r - other.r))

    def __repr__(self):
        return f"Cell({self.cell_type.value}, {self.r}, {self.c}, {self.assign})"
