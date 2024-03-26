from abc import abstractmethod, ABC
from typing import Type


class CPPPlanner(ABC):
    def __init_subclass__(cls, **kwargs):
        CPPPlannerFactory.register(cls.__name__, cls)
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def plan(
        self, area: list[tuple[int, int]], pos: tuple[int, int]
    ) -> list[tuple[int, int]]:
        pass


class CPPPlannerFactory:
    _registry: dict[str, Type[CPPPlanner]] = {}

    @staticmethod
    def get_planner(name: str) -> CPPPlanner:
        planner_cls = CPPPlannerFactory._registry[name]
        if planner_cls is None:
            raise ValueError(f"Planner {name} not found")
        return planner_cls()

    @staticmethod
    def register(name: str, planner: Type[CPPPlanner]):
        CPPPlannerFactory._registry[name] = planner
