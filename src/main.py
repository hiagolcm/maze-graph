import pygame

import maze_builders.dfs_builder as dfs_builder
import maze_solvers.dfs_solver as dfs_solver
from maze import Maze, Node

MAZE_WIDTH = 100
MAZE_HEIGHT = 100
MULTIPLIER = 10
THICKNESS = 1


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


def draw_square_filled(node: Node, screen, gap=0, color="red"):
    x = node.x * MULTIPLIER
    y = node.y * MULTIPLIER

    size = MULTIPLIER - THICKNESS - 2 * gap

    square = pygame.Rect(0, 0, size, size)

    square.center = (
        x + MULTIPLIER // 2,
        y + MULTIPLIER // 2,
    )

    pygame.draw.rect(screen, color, square)


def add_to_drawing_buffer(node: Node, buffer):
    buffer.append(node)


maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
dfs_builder.build(maze.first)
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
maze.apply_for_each_node(lambda node: draw_square(node, screen))

buffer = []
dfs_solver.solve(maze.first, maze.last, lambda node: add_to_drawing_buffer(node, buffer))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if len(buffer) > 0:
        current_node = buffer.pop(0)
        draw_square_filled(current_node, screen)

    pygame.display.flip()

    dt = clock.tick(200) / 1000

pygame.quit()
