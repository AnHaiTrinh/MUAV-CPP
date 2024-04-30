import pygame

from src.core import colors
from src.render.base import Component


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
        ticker_color: colors.Color = colors.BLACK,
    ):
        super().__init__(surface, translation)
        self.min_value = min_value
        self.max_value = max_value

        self.height_offset = 2 * self.rect.height // 3
        self.slider_radius = self.rect.height // 6
        self.line_length = self.rect.width - 2 * self.slider_radius
        self.line_begin = self.slider_radius
        self.line_end = self.rect.width - self.slider_radius
        self.slider_pos = self.line_begin

        self.dragging = False

        self.background_color = background_color
        self.slider_color = slider_color
        self.line_color = line_color
        self.ticker_color = ticker_color

        self.add_event_handler(self.handle_mouse_click)
        self.add_event_handler(self.handle_mouse_up)
        self.add_event_handler(self.handle_mouse_motion)

    def render(self) -> None:
        self.surface.fill(self.background_color)
        pygame.draw.line(
            self.surface,
            self.line_color,
            (self.line_begin, self.height_offset),
            (self.line_end, self.height_offset),
            5,
        )
        pygame.draw.circle(
            self.surface,
            self.slider_color,
            (self.slider_pos, self.height_offset),
            self.slider_radius,
        )
        if self.is_slider_hovered():
            ticker_height = 2 * self.height_offset - self.rect.height
            font = pygame.font.Font(None, ticker_height)
            ticker = font.render(f"{self.get_value():.2f}", True, colors.BLACK)
            ticker_rect = ticker.get_rect(
                center=(
                    min(
                        max(self.slider_pos, ticker.get_width() // 2),
                        self.rect.width - ticker.get_width() // 2,
                    ),
                    ticker_height // 2,
                )
            )
            self.surface.blit(ticker, ticker_rect)

    def handle_mouse_click(self, event: pygame.event.Event) -> None:
        if self.is_clicked(event) and self.is_slider_hovered():
            self.dragging = True

    def handle_mouse_up(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            mouse_x -= self.rect.x
            self.slider_pos = min(max(mouse_x, self.line_begin), self.line_end)

    def get_value(self) -> float:
        return self.min_value + (
            self.slider_pos - self.slider_radius
        ) / self.line_length * (self.max_value - self.min_value)

    def is_slider_hovered(self) -> bool:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dist = (mouse_x - (self.slider_pos + self.rect.x)) ** 2 + (
            mouse_y - (self.rect.y + self.height_offset)
        ) ** 2
        return dist <= self.slider_radius**2
