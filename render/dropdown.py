import pygame

from render import colors
from render.base import Component


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

    def render(self):
        pygame.draw.rect(
            self.surface,
            self.background_color,
            (0, 0, self.rect.width, self.rect.height),
        )
        self.draw_section(0, self.values[self.selected], self.main_color)
        idx = 1
        if self.is_expanded:
            for value in self.values:
                if value != self.values[self.selected]:
                    self.draw_section(idx, value, self.background_color)
                    idx += 1

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        _, absolute_mouse_pos_y = absolute_mouse_pos
        mouse_pos_y = absolute_mouse_pos_y - self.rect.y
        section_index = mouse_pos_y // self.section_height
        if section_index == 0:
            self.is_expanded = not self.is_expanded
        else:
            self.selected = section_index
            self.is_expanded = False

    def draw_section(self, section_index: int, text: str, color: colors.Color):
        width_offset = 0
        height_offset = section_index * self.section_height
        rect = pygame.draw.rect(
            self.surface,
            color,
            (width_offset, height_offset, self.section_width, self.section_height),
        )
        text = self.font.render(text, True, self.text_color)
        text_rect = text.get_rect(center=rect.center)
        self.surface.blit(text, text_rect)
