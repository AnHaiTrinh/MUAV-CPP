from typing import TypeAlias

Color: TypeAlias = tuple[int, int, int]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 139, 0)
DARK_BLUE = (0, 0, 139)
DARK_YELLOW = (139, 139, 0)
DARK_MAGENTA = (139, 0, 139)
DARK_ORANGE = (255, 140, 0)
DARK_PURPLE = (128, 0, 128)
DARK_PINK = (139, 0, 139)
DARK_BROWN = (139, 69, 19)

_UAV_COLORS = [
    DARK_ORANGE,
    DARK_PURPLE,
    DARK_PINK,
    DARK_BROWN,
    DARK_RED,
    DARK_GREEN,
    DARK_BLUE,
    DARK_YELLOW,
]


class ColorManager:
    colors: list[Color] = _UAV_COLORS

    @classmethod
    def get_color(cls) -> Color:
        try:
            color = cls.colors.pop()
            return color
        except IndexError:
            raise ValueError("No more colors available")

    @classmethod
    def release_color(cls, color: Color) -> None:
        cls.colors.append(color)