import argparse
import importlib
import pkgutil
import random

import pygame

import maze_builders
import maze_solvers
from constants import MAZE_HEIGHT, MAZE_WIDTH, MULTIPLIER
from draw_utils import draw_square, draw_square_filled
from maze import Maze


def available(package):
    return sorted(module.name for module in pkgutil.iter_modules(package.__path__))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gera um labirinto com um builder e o resolve com um solver.",
    )
    parser.add_argument(
        "--builder",
        default="dead_end_dfs",
        choices=available(maze_builders),
        help="algoritmo que constroi o labirinto (default: dead_end_dfs)",
    )
    parser.add_argument(
        "--solver",
        default="dfs",
        choices=available(maze_solvers),
        help="algoritmo que resolve o labirinto (default: dfs)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="semente aleatoria para reproduzir o mesmo labirinto (default: 0)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=MAZE_WIDTH,
        help=f"largura em celulas (default: {MAZE_WIDTH})",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=MAZE_HEIGHT,
        help=f"altura em celulas (default: {MAZE_HEIGHT})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    builder = importlib.import_module(f"maze_builders.{args.builder}").build
    solver = importlib.import_module(f"maze_solvers.{args.solver}").solve

    # Maze build
    maze = Maze(args.width, args.height, builder=builder, solver=solver)
    maze.open_entrance_and_exit()

    # Maze solve
    path = []
    maze.solve(lambda node: path.append(node))

    # Screen setup
    pygame.init()
    screen = pygame.display.set_mode((args.width * MULTIPLIER, args.height * MULTIPLIER))
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


if __name__ == "__main__":
    main()
