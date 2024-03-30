from abc import ABC, abstractmethod
from collections.abc import Callable

from render import colors
import pygame


class Component(ABC):
    def __init__(self, surface: pygame.Surface, translation: tuple[int, int]):
        self.surface = surface
        self.rect = self.surface.get_rect(topleft=translation)
        self.is_disabled = False
        self.handlers: list[Callable[[pygame.event.Event], None]] = []

    @abstractmethod
    def render(self) -> None:
        pass

    def update(self, event: pygame.event.Event) -> None:
        if not self.is_disabled:
            for handler in self.handlers:
                handler(event)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self._collide(event.pos)
        )

    def add_event_handler(self, handler: Callable[[pygame.event.Event], None]) -> None:
        self.handlers.append(handler)

    def _collide(self, point: tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)


class BorderedComponent(Component):
    def __init__(
        self,
        component: Component,
        border_width: int = 5,
        border_color: colors.Color = colors.BLACK,
    ):
        self.component = component
        self.border_width = border_width
        self.border_color = border_color
        translation = (component.rect.x - border_width, component.rect.y - border_width)
        new_surface = pygame.Surface(
            (
                component.rect.width + 2 * border_width,
                component.rect.height + 2 * border_width,
            )
        )
        super().__init__(new_surface, translation)
        self.add_event_handler(self.component.update)

    def render(self) -> None:
        self.surface.fill(self.border_color)
        self.component.render()
        self.surface.blit(
            self.component.surface, (self.border_width, self.border_width)
        )


class ComposableComponent(Component):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        background_color: colors.Color = colors.WHITE,
    ):

        super().__init__(surface, translation)
        self.components: dict[str, Component] = {}
        self.background_color = background_color

    def add_component(self, name: str, component: Component) -> None:
        self.components[name] = component
        self.add_event_handler(component.update)

    def remove_component(self, name: str) -> None:
        component = self.components.pop(name, None)
        if component is not None:
            self.handlers.remove(component.update)

    def render(self) -> None:
        self.surface.fill(self.background_color)
        for component in self.components.values():
            component.render()
            self.surface.blit(
                component.surface,
                (component.rect.x - self.rect.x, component.rect.y - self.rect.y),
            )
