import pygame

from core.environment import Map, CellType
from core.utils import resize_map
from render import colors
from render.base import Component


class MapComponent(Component):
    def __init__(
        self,
        _map: Map,
        surface: pygame.Surface,
        translation: tuple[int, int],
        cell_height: int = 4,
        cell_width: int = 4,
    ):
        super().__init__(surface, translation)
        self.cell_width = cell_width
        self.cell_height = cell_height
        self._map = resize_map(
            _map, self.rect.width // cell_width, self.rect.height // cell_height
        )

    def render(self):
        for i in range(self._map.width):
            for j in range(self._map.height):
                cell_type = self._map.get_cell(i, j).cell_type
                color = colors.WHITE if cell_type == CellType.FREE else colors.BLACK
                pygame.draw.rect(
                    self.surface,
                    color,
                    pygame.Rect(
                        j * self.cell_width,
                        i * self.cell_height,
                        self.cell_width,
                        self.cell_height,
                    ),
                )

    def handleMouseClick(self, absolute_mouse_pos: tuple[int, int]):
        absolute_mouse_pos_x, absolute_mouse_pos_y = absolute_mouse_pos
        mouse_pos_x = absolute_mouse_pos_x - self.rect.x
        mouse_pos_y = absolute_mouse_pos_y - self.rect.y
        cell_x = mouse_pos_x // self.cell_width
        cell_y = mouse_pos_y // self.cell_height
        cell_type = self._map.get_cell(cell_y, cell_x).cell_type
        if cell_type == CellType.FREE:
            self._map.set_cell(cell_y, cell_x, CellType.OCCUPIED)
        elif cell_type == CellType.OCCUPIED:
            self._map.set_cell(cell_y, cell_x, CellType.FREE)

    def set_map(self, _map: Map) -> None:
        self._map = resize_map(
            _map,
            self.rect.width // self.cell_width,
            self.rect.height // self.cell_height,
        )

    def get_map(self):
        return self._map
