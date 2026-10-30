import pygame

from maze import Maze, Node, navigate, break_walls_dfs

MAZE_WIDTH = 50
MAZE_HEIGHT = 50
MULTIPLIER = 15
THICKNESS = 4


def draw_square(node: Node, screen):
    x = node.x * MULTIPLIER
    y = node.y * MULTIPLIER

    if not node.left_node.is_path_free:
        pygame.draw.line(screen, 'black', (x, y),
                         (x, y + MULTIPLIER), THICKNESS)

    if not node.up_node.is_path_free:
        pygame.draw.line(screen, 'black', (x, y),
                         (x + MULTIPLIER, y), THICKNESS)

    if not node.right_node.is_path_free:
        pygame.draw.line(
            screen, 'black',
            (x + MULTIPLIER, y),
            (x + MULTIPLIER, y + MULTIPLIER),
            THICKNESS,
        )

    if not node.down_node.is_path_free:
        pygame.draw.line(
            screen, 'black',
            (x, y + MULTIPLIER),
            (x + MULTIPLIER, y + MULTIPLIER),
            THICKNESS,
        )


maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
break_walls_dfs(maze.first)

# pygame setup
pygame.init()
screen = pygame.display.set_mode(
    (MAZE_WIDTH * MULTIPLIER + THICKNESS, MAZE_HEIGHT * MULTIPLIER + THICKNESS))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

screen.fill("white")
navigate(maze.first, lambda node: draw_square(node, screen))


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
