from abc import abstractmethod, ABC
from typing import Type

from src.core.uav import UAV
from src.core.map import Map


class SingleCPPPlanner(ABC):
    name: str

    def __init__(self, area: Map, uav: UAV, **kwargs):
        self.area = area
        self.uav = uav

    def __init_subclass__(cls, **kwargs):
        SingleCPPPlannerFactory.register(cls.name, cls)
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def plan(self) -> None:
        pass


class SingleCPPPlannerFactory:
    _registry: dict[str, Type[SingleCPPPlanner]] = {}

    @staticmethod
    def get_planner(name: str, area: Map, uav: UAV, **kwargs) -> SingleCPPPlanner:
        planner_cls = SingleCPPPlannerFactory._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(area, uav, **kwargs)

    @staticmethod
    def register(name: str, planner: Type[SingleCPPPlanner]):
        SingleCPPPlannerFactory._registry[name] = planner
