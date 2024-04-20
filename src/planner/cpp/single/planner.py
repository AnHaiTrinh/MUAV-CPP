from abc import abstractmethod, ABC
from typing import Type

from src.core.uav import UAV
from src.core.map import Map


class SingleCoveragePathPlanner(ABC):
    name: str

    def __init__(self, area: Map, uav: UAV, **kwargs):
        self.area = area
        self.uav = uav

    def __init_subclass__(cls, **kwargs):
        SingleCoveragePathPlannerFactory.register(cls.name, cls)
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def plan(self) -> None:
        pass


class SingleCoveragePathPlannerFactory:
    _registry: dict[str, Type[SingleCoveragePathPlanner]] = {}

    @classmethod
    def get_planner(
        cls, name: str, area: Map, uav: UAV, **kwargs
    ) -> SingleCoveragePathPlanner:
        planner_cls = cls._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(area, uav, **kwargs)

    @classmethod
    def register(cls, name: str, planner: Type[SingleCoveragePathPlanner]):
        cls._registry[name] = planner
