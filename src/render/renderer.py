from tkinter.filedialog import askopenfilename, asksaveasfilename

import pygame

from src.core.map import Map
from src.core.uav import UAV
from src.core.utils import load_map_from_file, save_map_to_file
from src.planner.cpp.continuous.planner import (
    ContinuousCoveragePathPlanner,
    ContinuousCoveragePathPlannerFactory,
)
from src.render.base import BorderedComponent, ComposableComponent
from src.render.colors import ColorManager
from src.render.events import UAV_COUNT_CHANGE_EVENT
from src.render.panel import UAVPanel
from src.render.state import StateEnum
from src.render import colors
from src.render.buttons import ButtonTray, AnnotatedComponent, Button
from src.render.dropdown import DropDown
from src.render.map_component import MapComponent
from src.render.slider import Slider


class Renderer(ComposableComponent):
    def __init__(
        self,
        num_uavs: int = 5,
        map_size: tuple[int, int] = (128, 128),
        size: tuple[int, int] = (800, 800),
        background_color: colors.Color = colors.WHITE,
    ):
        pygame.init()
        self.surface = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("MUAV-CPP")
        super().__init__(self.surface, (0, 0), background_color)

        self.map_component = MapComponent(
            Map.create_empty_map(*map_size),
            pygame.Surface((512, 512)),
            (30, 250),
            cell_width=512 // map_size[0],
            cell_height=512 // map_size[1],
        )

        self.add_component(
            "map",
            BorderedComponent(self.map_component),
        )

        self.state_button_tray = ButtonTray(pygame.Surface((200, 50)), (20, 20))
        self.add_component("state", self.state_button_tray)

        self.load_button = Button(pygame.Surface((60, 50)), (300, 20), "Load")
        self.load_button.add_click_handler(self._load_handler)
        self.add_component("load", BorderedComponent(self.load_button, 5))

        self.save_button = Button(pygame.Surface((60, 50)), (400, 20), "Save")
        self.save_button.add_click_handler(self._save_handler)
        self.add_component("save", BorderedComponent(self.save_button, 5))

        self.dropdown = DropDown(
            pygame.Surface((180, 210)),
            (600, 20),
            ["Dummy", "Single", "DARP", "Algo3"],
        )
        self.add_component("dropdown", self.dropdown)

        self.planner: ContinuousCoveragePathPlanner | None = None

        self.new_uav_slider = Slider(
            pygame.Surface((200, 42)),
            (30, 150),
        )
        self.add_component(
            "new_uav_prob",
            AnnotatedComponent(self.new_uav_slider, "New UAV Probability"),
        )

        self.remove_uav_slider = Slider(
            pygame.Surface((200, 42)),
            (330, 150),
        )
        self.add_component(
            "remove_uav_prob",
            AnnotatedComponent(self.remove_uav_slider, "Remove UAV Probability"),
        )

        self.uavs = [UAV() for _ in range(num_uavs)]
        self._create_uav_panel()

        self.add_event_handler(self._handle_uav_change)

        self.not_disabled = ["state", "new_uav_prob", "remove_uav_prob", "uav_panel"]

        self.done = False

    def run(self) -> None:
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                self.update(event)

            if self.state_button_tray.get_state() == StateEnum.RESET:
                self.map_component.set_map(Map.create_empty_map(512, 512))
                self.map_component.set_uavs([])
                self.planner = None
                for uav in self.uavs:
                    uav.reset()
                self._create_uav_panel()
                self.state_button_tray.set_state(StateEnum.EDIT)

            state = self.state_button_tray.get_state()

            if state != StateEnum.EDIT:
                for name, component in self.components.items():
                    if name not in self.not_disabled:
                        component.is_disabled = True

                if state == StateEnum.RUN:
                    self._handle_run()
                elif state == StateEnum.PAUSE:
                    continue

            else:
                for component in self.components.values():
                    component.is_disabled = False

            self.render()
            pygame.display.flip()
            # self.clock.tick(60)
        pygame.quit()

    def _load_handler(self, _: pygame.event.Event) -> None:
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

    def _save_handler(self, _: pygame.event.Event) -> None:
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

    def _create_uav_panel(self):
        uav_panel = self.components.get("uav_panel", None)
        if uav_panel is not None:
            self.remove_component("uav_panel")

        uav_panel = UAVPanel(
            pygame.Surface((180, 512)),
            (600, 250),
            self.uavs,
        )
        self.add_component("uav_panel", uav_panel)

    def _handle_uav_change(self, event: pygame.event.Event) -> None:
        if event.type == UAV_COUNT_CHANGE_EVENT:
            if self.planner is None:
                if self.state_button_tray.get_state() == StateEnum.EDIT:
                    if event.action == "add":
                        self.uavs.append(UAV(event.uav_name))
                    elif event.action == "remove":
                        for i, uav in enumerate(self.uavs):
                            if uav.name == event.uav_name:
                                ColorManager.release_color(uav.color)
                                self.uavs.remove(uav)
                                break
                    self._create_uav_panel()
                    return
                else:
                    raise ValueError("Planner not initialized")

            if event.action == "add":
                self.planner.new_uav_plan(event.uav_name)
            elif event.action == "remove":
                self.planner.remove_uav_plan(event.uav_name)
            self._create_uav_panel()

    def _handle_run(self):
        if not self.planner:
            self.planner = ContinuousCoveragePathPlannerFactory.get_planner(
                self.dropdown.get_selected(),
                self.uavs,
                self.map_component.get_map(),
                single_planner="STC",
            )

        if not self.map_component.uavs:
            self.map_component.set_uavs(self.uavs)
            self._create_uav_panel()

        for uav in self.uavs:
            uav.move()
