from collections.abc import Callable

import pygame

from src.render.base import Component, ComposableComponent, BorderedComponent
from src.render.state import StateEnum, State
from src.core import colors


class Button(Component):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        text: str,
        background_color: colors.Color = colors.WHITE,
        text_color: colors.Color = colors.BLACK,
        font_ratio: float = 0.5,
        align: str = "center",
    ):
        super().__init__(surface, translation)

        self.text = text
        self.background_color = background_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, int(self.rect.height * font_ratio))
        self.align = align

    def render(self) -> None:
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, self.rect.width, self.rect.height),
        )
        text = self.font.render(self.text, True, self.text_color)
        self.surface.blit(text, self.get_text_rect(text))

    def add_click_handler(self, handler: Callable[[pygame.event.Event], None]) -> None:
        def click_handler(e: pygame.event.Event):
            if self.is_clicked(e):
                handler(e)

        self.add_event_handler(click_handler)

    def get_text_rect(self, text_surface: pygame.Surface) -> pygame.Rect:
        if self.align == "center":
            return text_surface.get_rect(
                center=(self.rect.width // 2, self.rect.height // 2)
            )
        elif self.align == "left":
            return text_surface.get_rect(left=0, centery=self.rect.height // 2)
        return text_surface.get_rect()


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

    def get_state(self) -> StateEnum:
        return self.state.state

    def set_state(self, state: StateEnum):
        self.state.state = state

    def handle_button_click(
        self, button_name: str
    ) -> Callable[[pygame.event.Event], None]:
        def handler(_: pygame.event.Event):
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
        text_alignment: str = "left",
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
            font_ratio=0.8,
            align=text_alignment,
        )

        self.add_component("annotation", annotation_button)
        self.add_component("component", component)
