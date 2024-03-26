from abc import ABC, abstractmethod
from enum import Enum

from render import colors
import pygame


class StateEnum(Enum):
    EDIT = "edit"  # The user is editing the map
    RUN = "run"  # The simulation is running
    PAUSE = "pause"  # The simulation is paused
    RESET = "reset"  # The simulation is being reset


class State:
    def __init__(self):
        self.state: StateEnum = StateEnum.EDIT


class Component(ABC):
    def __init__(self, surface: pygame.Surface, translation: tuple[int, int]):
        self.surface = surface
        self.rect = self.surface.get_rect(topleft=translation)
        self.is_disabled = False

    @abstractmethod
    def render(self):
        pass

    def update(self, event: pygame.event.Event):
        if self.is_disabled or not self.is_clicked(event):
            return
        self.handleMouseClick(pygame.mouse.get_pos())

    @abstractmethod
    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        pass

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.collide(pygame.mouse.get_pos())
        return False

    def collide(self, point: tuple[int, int]) -> bool:
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

    def render(self):
        self.surface.fill(self.border_color)
        self.component.render()
        self.surface.blit(
            self.component.surface, (self.border_width, self.border_width)
        )

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        if self.component.collide(absolute_mouse_pos):
            self.component.handleMouseClick(absolute_mouse_pos)


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

    def add_component(self, name: str, component: Component):
        self.components[name] = component

    def render(self):
        self.surface.fill(self.background_color)
        for component in self.components.values():
            component.render()
            self.surface.blit(
                component.surface,
                (component.rect.x - self.rect.x, component.rect.y - self.rect.y),
            )

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        for component in self.components.values():
            if component.collide(absolute_mouse_pos):
                component.handleMouseClick(absolute_mouse_pos)
                break
