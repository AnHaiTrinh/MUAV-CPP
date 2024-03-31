from abc import abstractmethod, ABC
from typing import Type

from core.environment import Cell


class SingleCPPPlanner(ABC):
    name: str

    def __init__(self, **kwargs):
        pass

    def __init_subclass__(cls, **kwargs):
        SingleCPPPlannerFactory.register(cls.name, cls)
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def plan(self, area: list[Cell], pos: Cell) -> list[Cell]:
        pass


class SingleCPPPlannerFactory:
    _registry: dict[str, Type[SingleCPPPlanner]] = {}

    @staticmethod
    def get_planner(name: str, **kwargs) -> SingleCPPPlanner:
        planner_cls = SingleCPPPlannerFactory._registry.get(name, None)
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls(**kwargs)

    @staticmethod
    def register(name: str, planner: Type[SingleCPPPlanner]):
        SingleCPPPlannerFactory._registry[name] = planner
