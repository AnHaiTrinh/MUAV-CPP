import pygame

from render import colors
from render.base import Component


class Slider(Component):
    def __init__(
        self,
        surface: pygame.Surface,
        translation: tuple[int, int],
        min_value: float = 0.0,
        max_value: float = 1.0,
        background_color: colors.Color = colors.WHITE,
        line_color: colors.Color = colors.BLACK,
        slider_color: colors.Color = colors.RED,
    ):
        super().__init__(surface, translation)
        self.min_value = min_value
        self.max_value = max_value

        self.slider_radius = self.rect.height >> 1
        self.line_length = self.rect.width - 2 * self.slider_radius
        self.line_begin = self.slider_radius
        self.line_end = self.rect.width - self.slider_radius
        self.slider_pos = self.line_begin
        self.dragging = False

        self.background_color = background_color
        self.slider_color = slider_color
        self.line_color = line_color

    def render(self):
        self.surface.fill(self.background_color)
        pygame.draw.line(
            self.surface,
            self.line_color,
            (self.line_begin, self.rect.height >> 1),
            (self.line_end, self.rect.height >> 1),
            5,
        )
        pygame.draw.circle(
            self.surface,
            self.slider_color,
            (self.slider_pos, self.rect.height >> 1),
            self.slider_radius,
        )

    def update(self, event: pygame.event.Event):
        if self.is_disabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handleMouseClick(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handleMouseUp()
        elif event.type == pygame.MOUSEMOTION:
            self.handleMouseMotion(event.pos)

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        mouse_x, mouse_y = absolute_mouse_pos
        dist = (mouse_x - (self.slider_pos + self.rect.x + self.slider_radius)) ** 2 + (
            mouse_y - (self.rect.y + self.slider_radius)
        ) ** 2
        if dist <= self.slider_radius**2:
            self.dragging = True

    def handleMouseUp(self):
        self.dragging = False

    def handleMouseMotion(self, absolute_mouse_pos: tuple[int, int]):
        if self.dragging:
            mouse_x, _ = absolute_mouse_pos
            mouse_x -= self.rect.x
            self.slider_pos = min(max(mouse_x, self.line_begin), self.line_end)

    def get_value(self):
        return self.min_value + (
            self.slider_pos - self.slider_radius
        ) / self.line_length * (self.max_value - self.min_value)
