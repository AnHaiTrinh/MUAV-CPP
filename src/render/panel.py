import pygame

from src.core.uav import UAV, uav_name_generator
from src.core import colors
from src.render.base import ComposableComponent, BorderedComponent
from src.render.buttons import Button
from src.render.events import remove_uav_event, add_uav_event


class UAVSection(ComposableComponent):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        uav: UAV,
        uav_color: colors.Color,
        background_color: colors.Color = colors.WHITE,
    ):
        super().__init__(surface, translation, background_color)
        self.uav = uav

        self.close_button = Button(
            pygame.Surface((self.rect.height // 2, self.rect.height // 2)),
            (self.rect.x + self.rect.width - self.rect.height // 2, self.rect.y),
            "X",
            background_color=colors.RED,
            text_color=colors.WHITE,
            font_ratio=1,
        )
        self.close_button.add_click_handler(self._close_button_click_handler)
        self.add_component("close_button", BorderedComponent(self.close_button))

        self.add_component(
            "name_button",
            Button(
                pygame.Surface(
                    (self.rect.width - self.rect.height // 2, self.rect.height // 2)
                ),
                (self.rect.x, self.rect.y),
                f"Name: {self.uav.name}",
                background_color=colors.WHITE,
                text_color=uav_color,
                font_ratio=0.6,
                align="left",
            ),
        )

        self.add_component(
            "length_button",
            Button(
                pygame.Surface((self.rect.width, self.rect.height // 2)),
                (self.rect.x, self.rect.y + self.rect.height // 2),
                f"Path length: {self.uav.trajectory_length:.2f}",
                background_color=colors.WHITE,
                text_color=uav_color,
                font_ratio=0.6,
                align="left",
            ),
        )

    def _close_button_click_handler(self, _: pygame.event.Event) -> None:
        pygame.event.post(remove_uav_event(self.uav.name))


class UAVPanel(ComposableComponent):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        uavs: list[UAV],
        section_height: int = 45,
        section_border: int = 2,
        background_color: colors.Color = colors.WHITE,
    ):
        super().__init__(surface, translation, background_color)

        # Create UAVs
        for idx, uav in enumerate(uavs):
            section = BorderedComponent(
                UAVSection(
                    pygame.Surface(
                        (
                            self.rect.width - 2 * section_border,
                            section_height - 2 * section_border,
                        )
                    ),
                    (
                        self.rect.x + section_border,
                        self.rect.y + idx * section_height + section_border,
                    ),
                    uav,
                    uav.color,
                ),
                border_width=section_border,
            )
            self.add_component(f"{uav.name}_section", section)

        # Create add button
        add_uav_button = Button(
            surface=pygame.Surface((self.rect.width, section_height)),
            translation=(self.rect.x, self.rect.y + self.rect.height - section_height),
            text="+",
            background_color=colors.GREEN,
            text_color=colors.WHITE,
            font_ratio=1,
        )
        add_uav_button.add_click_handler(self._add_uav_button_click_handler)
        self.add_component("add_uav_button", add_uav_button)

    @staticmethod
    def _add_uav_button_click_handler(_: pygame.event.Event) -> None:
        pygame.event.post(add_uav_event(uav_name_generator()))
