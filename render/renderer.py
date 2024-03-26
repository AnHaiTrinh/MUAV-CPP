import pygame

from core.environment import Map
from render.base import BorderedComponent, ComposableComponent, State, StateEnum
from render import colors
from render.buttons import ButtonTray, LoadButton, SaveButton
from render.dropdown import DropDown
from render.map_component import MapComponent


class Renderer(ComposableComponent):
    def __init__(
        self,
        size: tuple[int, int] = (800, 800),
        background_color: colors.Color = colors.WHITE,
    ):
        pygame.init()
        self.surface = pygame.display.set_mode(size)
        pygame.display.set_caption("MUAV-CPP")
        super().__init__(self.surface, (0, 0), background_color)

        self.map_component = MapComponent(
            Map.create_empty_map(512, 512),
            pygame.Surface((512, 512)),
            (30, 250),
        )

        self.add_component(
            "map",
            BorderedComponent(self.map_component),
        )

        self.state = State()
        self.add_component(
            "state", ButtonTray(pygame.Surface((200, 50)), self.state, (30, 50))
        )

        self.load_button = LoadButton(
            pygame.Surface((100, 50)), (600, 50), self.map_component
        )
        self.add_component("load", BorderedComponent(self.load_button))

        self.save_button = SaveButton(
            pygame.Surface((100, 50)), (600, 150), self.map_component
        )
        self.add_component("save", BorderedComponent(self.save_button))

        self.dropdown = DropDown(
            pygame.Surface((150, 210)),
            (350, 20),
            ["Algo1", "Algo2", "Algo3", "Algo4"],
        )
        self.add_component("dropdown", self.dropdown)

        self.not_disabled = ["state"]

        self.done = False

    def run(self):
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                for component in self.components.values():
                    component.update(event)

            if self.state.state == StateEnum.RESET:
                self.map_component.set_map(Map.create_empty_map(512, 512))
                self.state.state = StateEnum.EDIT

            state = self.state.state

            if state != StateEnum.EDIT:
                for name, component in self.components.items():
                    if name not in self.not_disabled:
                        component.is_disabled = True

                if state == StateEnum.RUN:
                    print("running")
                elif state == StateEnum.PAUSE:
                    print("pausing")
                    continue

            else:
                for component in self.components.values():
                    component.is_disabled = False

            self.render()
            pygame.display.flip()
        pygame.quit()
