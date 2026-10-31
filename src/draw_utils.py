import pygame
from constants import MAZE_HEIGHT, MAZE_WIDTH, MULTIPLIER

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

