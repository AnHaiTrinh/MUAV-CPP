from abc import abstractmethod, ABC
import random
from typing import Type

from src.core.map import Map
from src.core.uav import UAV

random.seed(42069)


class MultiCoveragePathPlanner(ABC):
    name: str

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        self.num_uavs = len(uavs)

        self.free_cells = _map.free_cells
        self.free_cell_count = len(_map.free_cells)
        self.target_cell_count = self.free_cell_count // self.num_uavs

        self.uavs = uavs
        self.map = _map

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        MultiCoveragePathPlannerFactory.register(cls.name, cls)

    @abstractmethod
    def plan(self) -> None:
        pass


class MultiCoveragePathPlannerFactory:
    _registry: dict[str, Type[MultiCoveragePathPlanner]] = {}

    @classmethod
    def get_planner(
        cls, name: str, uavs: list[UAV], _map: Map, **kwargs
    ) -> MultiCoveragePathPlanner:
        planner_cls = cls._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(uavs, _map, **kwargs)

    @classmethod
    def register(cls, name: str, planner: Type[MultiCoveragePathPlanner]) -> None:
        cls._registry[name] = planner

    @classmethod
    def get_planner_names(cls) -> list[str]:
        return list(cls._registry.keys())
