import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Custom Event Example")

# Define custom event type
CUSTOM_EVENT_TYPE = pygame.USEREVENT + 1

# Define custom event data (optional)
custom_event_data = {
    'message': 'Custom event triggered!'
}

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Trigger custom event when a key is pressed
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Create custom event instance
                custom_event = pygame.event.Event(CUSTOM_EVENT_TYPE, custom_event_data)
                # Post custom event to the event queue
                pygame.event.post(custom_event)

        # Handle custom event
        elif event.type == CUSTOM_EVENT_TYPE:
            print("Custom event received:", event.message)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
