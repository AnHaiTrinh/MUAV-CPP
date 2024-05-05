from abc import abstractmethod, ABC
import random
from typing import Type

from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV

random.seed(42069)


class ContinuousCoveragePathPlanner(ABC):
    name: str

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        self.num_uavs = len(uavs)
        free_cells = []
        for row in _map.cells:
            for cell in row:
                if cell.cell_type == CellType.FREE:
                    free_cells.append((cell.r, cell.c))

        self.free_cell_count = len(free_cells)
        self.target_cell_count = self.free_cell_count // self.num_uavs

        for uav in uavs:
            free_cell = random.choice(free_cells)
            uav.r = free_cell[0]
            uav.c = free_cell[1]
            print(f"{uav.name} starts at {(uav.r, uav.c)}")
            free_cells.remove(free_cell)

        self.uavs = uavs
        self.map = _map

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ContinuousCoveragePathPlannerFactory.register(cls.name, cls)

    @abstractmethod
    def init_plan(self) -> None:
        pass

    @abstractmethod
    def new_uav_plan(self, uav_name: str) -> None:
        pass

    @abstractmethod
    def remove_uav_plan(self, uav_name: str) -> None:
        pass


class ContinuousCoveragePathPlannerFactory:
    _registry: dict[str, Type[ContinuousCoveragePathPlanner]] = {}

    @classmethod
    def get_planner(
        cls, name: str, uavs: list[UAV], _map: Map, **kwargs
    ) -> ContinuousCoveragePathPlanner:
        planner_cls = cls._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(uavs, _map, **kwargs)

    @classmethod
    def register(cls, name: str, planner: Type[ContinuousCoveragePathPlanner]):
        cls._registry[name] = planner
