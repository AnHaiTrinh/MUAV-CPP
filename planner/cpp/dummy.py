from core.environment import Cell, CellType, Map
from core.uav import UAV
from planner.cpp.continuous_planner import ContinuousCPPPlanner


class DummyContinuousCPPPlanner(ContinuousCPPPlanner):
    name = "Dummy"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)

    def init_plan(self) -> None:
        for i, uav in enumerate(self.uavs):
            uav.update_trajectory(
                [Cell(CellType.FREE, i * 20 + j, i * 20 + j) for j in range(20)]
                + [
                    Cell(CellType.FREE, i * 20 + 19, i * 20 + 19 - j)
                    for j in range(1, 20)
                ]
                + [Cell(CellType.FREE, i * 20 + 19 - j, i * 20) for j in range(1, 19)]
            )

    def new_uav_plan(self, uav_name: str) -> None:
        uav = UAV(uav_name)
        n = len(self.uavs)
        uav.update_trajectory(
            [Cell(CellType.FREE, n * 20 + j, n * 20 + j) for j in range(20)]
            + [Cell(CellType.FREE, n * 20 + 19, n * 20 + 19 - j) for j in range(1, 20)]
            + [Cell(CellType.FREE, n * 20 + 19 - j, n * 20) for j in range(1, 19)]
        )
        self.uavs.append(uav)

    def remove_uav_plan(self, uav_name: str) -> None:
        idx = None
        for i, uav in enumerate(self.uavs):
            if uav.name == uav_name:
                idx = i
                break

        if idx is None:
            raise ValueError(f"UAV with name {uav_name} not found")

        update_uav_idx = (idx + 1) % len(self.uavs)
        self.uavs[update_uav_idx].update_trajectory(
            [
                Cell(CellType.FREE, update_uav_idx * 20 + j, update_uav_idx * 20 + j)
                for j in range(20)
            ]
            + [
                Cell(
                    CellType.FREE,
                    update_uav_idx * 20 + 19,
                    update_uav_idx * 20 + 19 - j,
                )
                for j in range(1, 20)
            ]
            + [
                Cell(CellType.FREE, update_uav_idx * 20 + 19 - j, update_uav_idx * 20)
                for j in range(1, 19)
            ]
            + [
                Cell(CellType.FREE, update_uav_idx * 20 + j, update_uav_idx * 20 + j)
                for j in range(20)
            ]
            + [
                Cell(
                    CellType.FREE,
                    update_uav_idx * 20 + 19 - j,
                    update_uav_idx * 20 + 19,
                )
                for j in range(1, 20)
            ]
            + [
                Cell(CellType.FREE, update_uav_idx * 20, update_uav_idx * 20 + 19 - j)
                for j in range(1, 19)
            ]
        )

        self.uavs.pop(idx)
