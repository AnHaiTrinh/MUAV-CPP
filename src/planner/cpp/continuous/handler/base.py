from abc import ABC, abstractmethod
from typing import Type

from src.core.map import Map
from src.core.uav import UAV


class UAVChangeHandler(ABC):
    name: str

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        self.uavs = uavs
        self.map = _map

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        UAVChangeHandlerFactory.register(cls.name, cls)

    @abstractmethod
    def handle_new_uav(self, uav: UAV) -> None:
        pass

    @abstractmethod
    def handle_removed_uav(self, uav: UAV) -> None:
        pass


class UAVChangeHandlerFactory:
    _registry: dict[str, Type[UAVChangeHandler]] = {}

    @classmethod
    def get_handler(
        cls, handler_name: str, uavs: list[UAV], _map: Map, **kwargs
    ) -> UAVChangeHandler:
        handler_cls = cls._registry.get(handler_name, None)
        if handler_cls is None:
            raise ValueError(f"Handler {handler_name} not found")
        return handler_cls(uavs, _map, **kwargs)

    @classmethod
    def register(cls, name: str, handler: Type[UAVChangeHandler]) -> None:
        cls._registry[name] = handler

    @classmethod
    def list_handlers(cls) -> list[str]:
        return list(cls._registry.keys())
