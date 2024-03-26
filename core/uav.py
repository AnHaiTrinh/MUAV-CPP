class UAV:
    def __init__(self, name: str, r: int, c: int, trajectory: list[tuple[int, int]]):
        self.name = name
        self.pos = (r, c)
        self.trajectory = trajectory
        self.pos_idx = self.trajectory.index(self.pos)
        if self.pos_idx == -1:
            raise ValueError("Invalid initial position")

    def move(self) -> None:
        self.pos_idx = (self.pos_idx + 1) % len(self.trajectory)
        self.pos = self.trajectory[self.pos_idx]

    def __str__(self):
        return f"UAV {self.name}"
