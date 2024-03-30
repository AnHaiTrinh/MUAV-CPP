import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Isosceles Triangle in Pygame")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Function to draw an isosceles triangle inside a rectangle with top pointing to a given direction
def draw_isosceles_triangle(rect, direction):
    rect_width, rect_height = rect.size
    rect_center = rect.center

    triangle_height = min(rect_width, rect_height) // 2
    triangle_width = triangle_height * math.sqrt(3)

    if direction == "UP":
        points = [(rect_center[0], rect_center[1] - triangle_height),
                  (rect_center[0] - triangle_width / 2, rect_center[1] + triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] + triangle_height / 2)]
    elif direction == "DOWN":
        points = [(rect_center[0], rect_center[1] + triangle_height),
                  (rect_center[0] - triangle_width / 2, rect_center[1] - triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] - triangle_height / 2)]
    elif direction == "LEFT":
        points = [(rect_center[0] - triangle_height, rect_center[1]),
                  (rect_center[0] + triangle_height / 2, rect_center[1] - triangle_width / 2),
                  (rect_center[0] + triangle_height / 2, rect_center[1] + triangle_width / 2)]
    elif direction == "RIGHT":
        points = [(rect_center[0] + triangle_height, rect_center[1]),
                  (rect_center[0] - triangle_height / 2, rect_center[1] - triangle_width / 2),
                  (rect_center[0] - triangle_height / 2, rect_center[1] + triangle_width / 2)]
    elif direction == "UP_LEFT":
        points = [(rect_center[0] - triangle_width / 2, rect_center[1] - triangle_height / 2),
                  (rect_center[0], rect_center[1] + triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] - triangle_height / 2)]
    elif direction == "UP_RIGHT":
        points = [(rect_center[0] - triangle_width / 2, rect_center[1] - triangle_height / 2),
                  (rect_center[0], rect_center[1] + triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] - triangle_height / 2)]
    elif direction == "DOWN_LEFT":
        points = [(rect_center[0] - triangle_width / 2, rect_center[1] + triangle_height / 2),
                  (rect_center[0], rect_center[1] - triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] + triangle_height / 2)]
    elif direction == "DOWN_RIGHT":
        points = [(rect_center[0] - triangle_width / 2, rect_center[1] + triangle_height / 2),
                  (rect_center[0], rect_center[1] - triangle_height / 2),
                  (rect_center[0] + triangle_width / 2, rect_center[1] + triangle_height / 2)]

    pygame.draw.polygon(screen, BLACK, points, 0)


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Rectangle parameters
    rect_width = 200
    rect_height = 150
    rect_x = (WIDTH - rect_width) // 2
    rect_y = (HEIGHT - rect_height) // 2

    # Draw rectangle
    rectangle = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, BLACK, rectangle, 2)

    # Draw isosceles triangle pointing to different directions
    # draw_isosceles_triangle(rectangle, "UP")
    draw_isosceles_triangle(rectangle, "DOWN")
    # draw_isosceles_triangle(rectangle, "LEFT")
    # draw_isosceles_triangle(rectangle, "RIGHT")
    # draw_isosceles_triangle(rectangle, "UP_LEFT")
    # draw_isosceles_triangle(rectangle, "UP_RIGHT")
    # draw_isosceles_triangle(rectangle, "DOWN_LEFT")
    # draw_isosceles_triangle(rectangle, "DOWN_RIGHT")

    pygame.display.flip()

pygame.quit()
