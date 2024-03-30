from enum import Enum


class StateEnum(Enum):
    EDIT = "edit"  # The user is editing the map
    RUN = "run"  # The simulation is running
    PAUSE = "pause"  # The simulation is paused
    RESET = "reset"  # The simulation is being reset


class State:
    def __init__(self):
        self.state: StateEnum = StateEnum.EDIT  # type: ignore
