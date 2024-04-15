from abc import abstractmethod, ABC
from typing import Type

from core.map import Map
from core.uav import UAV


class ContinuousCPPPlanner(ABC):
    name: str

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        self.uavs = uavs
        self.map = _map
        self.init_plan()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ContinuousCPPPlannerFactory.register(cls.name, cls)

    @abstractmethod
    def init_plan(self) -> None:
        pass

    @abstractmethod
    def new_uav_plan(self, uav_name: str) -> None:
        pass

    @abstractmethod
    def remove_uav_plan(self, uav_name: str) -> None:
        pass


class ContinuousCPPPlannerFactory:
    _registry: dict[str, Type[ContinuousCPPPlanner]] = {}

    @classmethod
    def get_planner(
        cls, name: str, uavs: list[UAV], _map: Map, **kwargs
    ) -> ContinuousCPPPlanner:
        planner_cls = cls._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(uavs, _map, **kwargs)

    @classmethod
    def register(cls, name: str, planner: Type[ContinuousCPPPlanner]):
        cls._registry[name] = planner
