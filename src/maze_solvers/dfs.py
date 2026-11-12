import random

from maze import Node


def solve(start: Node, end: Node, draw_node):
    start.visited = True

    stack = [start]

    while len(stack) > 0:
        current = stack.pop()
        current.state = "EXPANDED"
        current.visited = True
        draw_node(current, "EXPANDED")

        if current == end:
            return True

        neighbors = current.get_reachable_neighbors()

        for n in neighbors:
            if n is not None and not n.visited:
                n.state = "DISCOVERED"
                stack.append(n)
                draw_node(n, "DISCOVERED")

    return False
