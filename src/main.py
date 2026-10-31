import pygame
import random

import maze_builders.dead_end_dfs as dead_end_dfs
import maze_solvers.dfs as dfs
from draw_utils import (
    draw_square,
    draw_square_filled,
)
from maze import Maze, Node
from constants import MAZE_HEIGHT, MAZE_WIDTH, MULTIPLIER

# Set seed
random.seed(0)

# Maze build
maze = Maze(MAZE_WIDTH, MAZE_HEIGHT, builder=dead_end_dfs.build, solver=dfs.solve) # <- MODIFIQUE AQUI PARA TESTAR SEU ALGORITMO
maze.open_entrance_and_exit()

# Maze solve
path = []
maze.solve(lambda node: path.append(node))

# Screen setup
pygame.init()
screen = pygame.display.set_mode((MAZE_WIDTH * MULTIPLIER, MAZE_HEIGHT * MULTIPLIER))
clock = pygame.time.Clock()
running = True
screen.fill("white")


# Maze related printing
maze.apply_for_each_node(lambda node: draw_square(node, screen))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if len(path) > 0:
        current_node = path.pop(0)
        draw_square_filled(current_node, screen)

    pygame.display.flip()

    clock.tick(200)

pygame.quit()
