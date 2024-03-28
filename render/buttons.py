from collections.abc import Callable
from tkinter.filedialog import askopenfilename, asksaveasfilename

import pygame

from core.utils import load_map_from_file, save_map_to_file
from render.base import Component, ComposableComponent, BorderedComponent, StateEnum
from render import colors
from render.base import State
from render.map_component import MapComponent


class Button(Component):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        text: str,
        background_color: colors.Color = colors.WHITE,
        text_color: colors.Color = colors.BLACK,
        font_ratio: float = 0.5,
    ):
        super().__init__(surface, translation)

        self.text = text
        self.background_color = background_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, int(self.rect.height * font_ratio))
        self.handlers: list[Callable[tuple[int, int], None]] = []

    def update(self, event: pygame.event.Event):
        if (not self.is_disabled) and self.is_clicked(event):
            for handler in self.handlers:
                handler(event.pos)

    def add_click_handler(self, handler: Callable[[tuple[int, int]], None]):
        self.handlers.append(handler)

    def render(self):
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, self.rect.width, self.rect.height),
        )
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.surface.blit(text, text_rect)


class ButtonTray(ComposableComponent):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        background_color: colors.Color = colors.WHITE,
    ):
        super().__init__(surface, translation, background_color)
        self.state = State()

        button_labels = ["Run", "Pause", "Reset"]
        num_buttons = len(button_labels)
        button_vertical_pad = self.rect.height // 10
        button_horizontal_pad = self.rect.width // 10
        button_pad_width_to_button_width = 0.5
        button_width = (
            self.rect.width - (num_buttons - 1) * button_horizontal_pad
        ) // int(num_buttons + button_pad_width_to_button_width * (num_buttons - 1))
        button_height = self.rect.height - 2 * button_vertical_pad
        button_border = 3

        for i, label in enumerate(button_labels):
            button = Button(
                pygame.Surface((button_width, button_height)),
                (
                    self.rect.x
                    + int(
                        button_horizontal_pad
                        + i * (1 + button_pad_width_to_button_width) * button_width
                    ),
                    self.rect.y + button_vertical_pad,
                ),
                label,
            )
            button.add_click_handler(self.handle_button_click(label))

            self.add_component(
                label.lower(),
                BorderedComponent(button, button_border),
            )

    def get_state(self):
        return self.state.state

    def set_state(self, state: StateEnum):
        self.state.state = state

    def handle_button_click(
        self, button_name: str
    ) -> Callable[[tuple[int, int]], None]:
        def handler(_):
            self.set_state(StateEnum[button_name.upper()])
            print(f"{button_name} button clicked")

        return handler


class AnnotatedComponent(ComposableComponent):
    def __init__(
        self,
        component: Component,
        annotation: str,
        annotation_height: int = 25,
        annotation_color: colors.Color = colors.BLACK,
        annotation_background_color: colors.Color = colors.WHITE,
    ):
        new_translation = (component.rect.x, component.rect.y - annotation_height)
        new_surface = pygame.Surface(
            (
                component.rect.width,
                component.rect.height + annotation_height,
            )
        )
        super().__init__(new_surface, new_translation)

        annotation_surface = pygame.Surface((self.rect.width, annotation_height))
        annotation_translation = (self.rect.x, self.rect.y)
        annotation_button = Button(
            surface=annotation_surface,
            translation=annotation_translation,
            text=annotation,
            background_color=annotation_background_color,
            text_color=annotation_color,
            font_ratio=1.0,
        )

        self.add_component("annotation", annotation_button)
        self.add_component("component", component)

    def update(self, event: pygame.event.Event):
        if self.is_disabled:
            return
        self.components["component"].update(event)
