from abc import abstractmethod
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
    ):
        super().__init__(surface, translation)

        self.text = text
        self.background_color = background_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, self.rect.height >> 1)

    def update(self, event: pygame.event.Event):
        if (not self.is_disabled) and self.is_clicked(event):
            self.handleMouseClick(event.pos)

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        print(f"{self.text} button clicked")

    def render(self):
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, self.rect.width, self.rect.height),
        )
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.surface.blit(text, text_rect)


class RunButton(Button):
    def __init__(self, surface: pygame.Surface, translation: tuple[int, int]):
        super().__init__(surface, translation, "Run")

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        print("Run button clicked")


class PauseButton(Button):
    def __init__(self, surface: pygame.Surface, translation: tuple[int, int]):
        super().__init__(surface, translation, "Pause")

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        print("Pause button clicked")


class ResetButton(Button):
    def __init__(self, surface: pygame.Surface, translation: tuple[int, int]):
        super().__init__(surface, translation, "Reset")

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        print("Reset button clicked")


class ButtonTray(ComposableComponent):
    def __init__(
        self,
        surface: pygame.Surface,
        state: State,
        translation: tuple[int, int],
        background_color: colors.Color = colors.WHITE,
    ):
        super().__init__(surface, translation, background_color)
        self.state = state

        num_buttons = 3
        button_vertical_pad = self.rect.height // 10
        button_horizontal_pad = self.rect.width // 10
        button_pad_width_to_button_width = 0.5
        button_width = (
            self.rect.width - (num_buttons - 1) * button_horizontal_pad
        ) // int(num_buttons + button_pad_width_to_button_width * (num_buttons - 1))
        button_height = self.rect.height - 2 * button_vertical_pad
        button_border = 3
        self.add_component(
            "run",
            BorderedComponent(
                RunButton(
                    pygame.Surface((button_width, button_height)),
                    (
                        self.rect.x + button_horizontal_pad,
                        self.rect.y + button_vertical_pad,
                    ),
                ),
                button_border,
            ),
        )
        self.add_component(
            "pause",
            BorderedComponent(
                PauseButton(
                    pygame.Surface((button_width, button_height)),
                    (
                        self.rect.x
                        + int(
                            button_horizontal_pad
                            + button_width * (1 + button_pad_width_to_button_width)
                        ),
                        self.rect.y + button_vertical_pad,
                    ),
                ),
                button_border,
            ),
        )
        self.add_component(
            "reset",
            BorderedComponent(
                ResetButton(
                    pygame.Surface((button_width, button_height)),
                    (
                        self.rect.x
                        + int(
                            button_horizontal_pad
                            + 2 * button_width * (1 + button_pad_width_to_button_width)
                        ),
                        self.rect.y + button_vertical_pad,
                    ),
                ),
                button_border,
            ),
        )

    def update(self, event: pygame.event.Event):
        if (not self.is_disabled) and self.is_clicked(event):
            for name, component in self.components.items():
                if component.collide(event.pos):
                    component.update(event)
                    self.state.state = StateEnum[name.upper()]
                    break


class LoadButton(Button):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        map_component: MapComponent,
    ):
        super().__init__(surface, translation, "Load")
        self.map_component = map_component

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        # open file chooser
        filename = askopenfilename(
            initialdir=".",
            title="Open File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.ico"),
                ("Text files", "*.txt"),
            ],
        )
        if not filename:
            return

        new_map = load_map_from_file(filename)
        self.map_component.set_map(new_map)


class SaveButton(Button):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        map_component: MapComponent,
    ):
        super().__init__(surface, translation, "Save")
        self.map_component = map_component

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        # open file chooser
        filename = asksaveasfilename(
            initialdir=".",
            title="Save File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.ico"),
                ("Text files", "*.txt"),
            ],
        )
        if not filename:
            return

        save_map_to_file(self.map_component.get_map(), filename)
        print(f"Map saved to {filename}")


class AnnotatedComponent(ComposableComponent):
    def __init__(
        self,
        component: Component,
        annotation: str,
        annotation_height: int = 30,
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
            annotation_surface,
            annotation_translation,
            annotation,
            annotation_background_color,
            annotation_color,
        )

        self.add_component("annotation", annotation_button)
        self.add_component("component", component)

    def update(self, event: pygame.event.Event):
        if self.is_disabled:
            return
        self.components["component"].update(event)
