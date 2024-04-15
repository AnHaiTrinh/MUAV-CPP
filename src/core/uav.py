from numpy.random import choice

from src.core.cell import Cell
from src.render.colors import ColorManager


class UAV:
    def __init__(
        self,
        name: str | None = None,
        r: int | None = None,
        c: int | None = None,
        trajectory: list[Cell] | None = None,
    ):
        if name is None:
            self.name = uav_name_generator()
        else:
            self.name = name
        self.r = r
        self.c = c
        self.trajectory = trajectory
        self.pos_idx: int | None = None
        if self.r is not None and self.c is not None and self.trajectory is not None:
            self.init_position()
        self.color = ColorManager.get_color()

    def move(self) -> None:
        if self.pos_idx is None:
            raise ValueError("UAV position index is not initialized")
        if self.trajectory is None:
            raise ValueError("UAV trajectory is not initialized")

        self.pos_idx = (self.pos_idx + 1) % len(self.trajectory)
        next_cell = self.trajectory[self.pos_idx]
        self.r = next_cell.r
        self.c = next_cell.c

    def get_trajectory_length(self) -> float:
        if not self.trajectory:
            return 0.0
        distance = 0.0
        trajectory_length = len(self.trajectory)
        for i in range(trajectory_length):
            distance += self.trajectory[i].distance(
                self.trajectory[(i + 1) % trajectory_length]
            )
        return distance

    def update_trajectory(self, trajectory: list[Cell]) -> None:
        self.trajectory = trajectory
        if self.r is None or self.c is None:
            self.r, self.c = self.trajectory[0].r, self.trajectory[0].c
        self.init_position()

    def init_position(self):
        found = False
        for idx, cell in enumerate(self.trajectory):
            if cell.r == self.r and cell.c == self.c:
                self.pos_idx = idx
                found = True
                break
        if not found:
            raise ValueError(
                f"Initial position ({self.r}, {self.c}) not found in trajectory {[(cell.r, cell.c) for cell in self.trajectory]}"
            )

    def __str__(self):
        return f"UAV {self.name}"


def uav_name_generator() -> str:
    return "UAV-" + "".join(str(i) for i in choice(10, size=6))
