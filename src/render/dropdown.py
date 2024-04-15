import pygame

from src.render import colors
from src.render.base import Component


class DropDown(Component):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        values: list[str],
        text_color: colors.Color = colors.BLACK,
        background_color: colors.Color = colors.WHITE,
        main_color: colors.Color = colors.CYAN,
    ):
        super().__init__(surface, translation)
        self.values = values
        self.selected = 0
        self.is_expanded = False

        self.section_width = self.rect.width
        self.section_height = self.rect.height // len(values)

        self.font = pygame.font.Font(None, self.section_height >> 1)
        self.text_color = text_color
        self.background_color = background_color
        self.main_color = main_color

        self.add_event_handler(self.click_handler)

    def render(self) -> None:
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, self.rect.width, self.rect.height),
        )
        self._draw_section(0, self.values[self.selected], self.main_color)
        idx = 1
        if self.is_expanded:
            for value in self.values:
                if value != self.values[self.selected]:
                    self._draw_section(idx, value, self.background_color)
                    idx += 1

    def click_handler(self, event: pygame.event.Event) -> None:
        if self.is_clicked(event):
            _, absolute_mouse_pos_y = event.pos
            mouse_pos_y = absolute_mouse_pos_y - self.rect.y
            section_index = mouse_pos_y // self.section_height
            if section_index == 0:
                self.is_expanded = not self.is_expanded
            else:
                if self.selected >= section_index:
                    section_index -= 1
                self.selected = section_index
                self.is_expanded = False

    def _draw_section(self, section_index: int, text: str, color: colors.Color) -> None:
        width_offset = 0
        height_offset = section_index * self.section_height
        rect = pygame.draw.rect(
            self.surface,
            color,
            (width_offset, height_offset, self.section_width, self.section_height),
        )
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.surface.blit(text_surface, text_rect)

    def get_selected(self) -> str:
        return self.values[self.selected]
