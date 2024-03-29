from core.environment import Cell


class UAV:
    def __init__(self, name: str, r: int, c: int, trajectory: list[Cell]):
        self.name: str = name
        self.r: int = r
        self.c: int = c
        self.trajectory: list[Cell] = trajectory
        self.pos_idx: int = 0
        self.init_position()

    def move(self) -> None:
        self.pos_idx = (self.pos_idx + 1) % len(self.trajectory)
        next_cell = self.trajectory[self.pos_idx]
        self.r = next_cell.r
        self.c = next_cell.c

    def get_trajectory_length(self) -> float:
        distance = 0
        l = len(self.trajectory)
        for i in range(l):
            distance += self.trajectory[i].distance(self.trajectory[(i + 1) % l])
        return distance

    def set_trajectory(self, trajectory: list[Cell]) -> None:
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
            raise ValueError("Initial position not found in trajectory")

    def __str__(self):
        return f"UAV {self.name}"
