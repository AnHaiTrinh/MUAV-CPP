from core.environment import Cell
from core.utils import uav_name_generator


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
        if self.r and self.c:
            self.init_position()

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

    def update_position(self, r: int, c: int) -> None:
        self.r = r
        self.c = c

    def update_trajectory(self, trajectory: list[Cell]) -> None:
        self.trajectory = trajectory
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
                f"Initial position ({self.r}, {self.c}) not found in trajectory {self.trajectory}"
            )

    def __str__(self):
        return f"UAV {self.name}"
