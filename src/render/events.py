import pygame

UAV_COUNT_CHANGE_EVENT = pygame.USEREVENT + 1


def add_uav_event(uav_name: str) -> pygame.event.Event:
    return pygame.event.Event(
        UAV_COUNT_CHANGE_EVENT,
        {
            "action": "add",
            "uav_name": uav_name,
        },
    )


def remove_uav_event(uav_name: str) -> pygame.event.Event:
    return pygame.event.Event(
        UAV_COUNT_CHANGE_EVENT,
        {
            "action": "remove",
            "uav_name": uav_name,
        },
    )
