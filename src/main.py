import pygame

from maze import Maze, Node, navigate, break_walls_dfs, solve_dfs

MAZE_WIDTH = 40
MAZE_HEIGHT = 40
MULTIPLIER = 20
THICKNESS = 4


def draw_square(node: Node, screen):
    x = node.x * MULTIPLIER
    y = node.y * MULTIPLIER

    if not node.left_node.is_path_free:
        pygame.draw.line(screen, "black", (x, y), (x, y + MULTIPLIER), THICKNESS)

    if not node.up_node.is_path_free:
        pygame.draw.line(screen, "black", (x, y), (x + MULTIPLIER, y), THICKNESS)

    if not node.right_node.is_path_free:
        pygame.draw.line(
            screen,
            "black",
            (x + MULTIPLIER, y),
            (x + MULTIPLIER, y + MULTIPLIER),
            THICKNESS,
        )

    if not node.down_node.is_path_free:
        pygame.draw.line(
            screen,
            "black",
            (x, y + MULTIPLIER),
            (x + MULTIPLIER, y + MULTIPLIER),
            THICKNESS,
        )


def draw_square_filled(node: Node, screen):
    x = node.x * MULTIPLIER
    y = node.y * MULTIPLIER
    border = THICKNESS

    pygame.draw.rect(
        screen,
        "red",
        (x + border, y + border, MULTIPLIER - border * 2, MULTIPLIER - border * 2),
    )

def add_to_drawing_buffer(node: Node, buffer):
    buffer.append(node)


maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
break_walls_dfs(maze.first)
# maze.open_entrance_and_exit()

# pygame setup
pygame.init()
screen = pygame.display.set_mode(
    (MAZE_WIDTH * MULTIPLIER + THICKNESS, MAZE_HEIGHT * MULTIPLIER + THICKNESS)
)
clock = pygame.time.Clock()
running = True
dt = 0

# printing
screen.fill("white")
navigate(maze.first, lambda node: draw_square(node, screen))

buffer = []
solve_dfs(maze.first, maze.last, lambda node: add_to_drawing_buffer(node, buffer))


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if len(buffer) > 0:
        current_node = buffer.pop(0)
        draw_square_filled(current_node, screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(10) / 1000

pygame.quit()
