from abc import abstractmethod, ABC
from typing import Type

from src.core.map import Map
from src.core.uav import UAV


class ContinuousCoveragePathPlanner(ABC):
    name: str

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
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
