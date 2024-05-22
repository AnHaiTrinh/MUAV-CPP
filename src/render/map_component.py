import pygame

from src.core.cell import CellType
from src.core.map import Map
from src.core.uav import UAV
from src.core.utils import resize_map
from src.core import colors
from src.render.base import Component


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
        self.add_event_handler(self.click_handler)

        self.uavs: list[UAV] = []

    def render(self) -> None:
        self._draw_map()
        self._draw_uav_trajectories()

    def click_handler(self, event: pygame.event.Event) -> None:
        if self.is_clicked(event):
            absolute_mouse_pos_x, absolute_mouse_pos_y = event.pos
            mouse_pos_x = absolute_mouse_pos_x - self.rect.x
            mouse_pos_y = absolute_mouse_pos_y - self.rect.y
            cell_x = mouse_pos_x // self.cell_width
            cell_y = mouse_pos_y // self.cell_height
            cell_type = self._map.get_cell(cell_y, cell_x).cell_type
            if cell_type == CellType.FREE:
                self._map.get_cell(cell_y, cell_x).cell_type = CellType.OCCUPIED
            elif cell_type == CellType.OCCUPIED:
                self._map.get_cell(cell_y, cell_x).cell_type = CellType.FREE

    def set_map(self, _map: Map) -> None:
        self._map = resize_map(
            _map,
            self.rect.width // self.cell_width,
            self.rect.height // self.cell_height,
        )

    def get_map(self) -> Map:
        return self._map

    def _draw_map(self):
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

    def set_uavs(self, uavs: list[UAV]) -> None:
        self.uavs = uavs

    def _draw_uav_trajectories(self):
        for uav in self.uavs:
            # Draw movement
            movement = uav.movement
            if movement is None:
                raise ValueError("UAV movement is None")

            for j in range(len(movement) - 1):
                pygame.draw.line(
                    self.surface,
                    uav.color,
                    (
                        (movement[j][1] + 0.5) * self.cell_width,
                        (movement[j][0] + 0.5) * self.cell_height,
                    ),
                    (
                        (movement[(j + 1)][1] + 0.5) * self.cell_width,
                        (movement[(j + 1)][0] + 0.5) * self.cell_height,
                    ),
                )

            # Draw UAV
            if uav.r is None or uav.c is None:
                raise ValueError("UAV position is None")

            pygame.draw.circle(
                self.surface,
                colors.RED,
                (
                    int((uav.c + 0.5) * self.cell_width),
                    int((uav.r + 0.5) * self.cell_height),
                ),
                min(self.cell_width, self.cell_height),
            )
