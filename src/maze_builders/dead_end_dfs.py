# Descricao do algoritmo
# - Escolhe uma célula inicial.
# - Visita vizinhos ainda não visitados.
# - Remove paredes entre as células.
# - Quando chega a um beco sem saída, retorna (backtracking).
# - Continua até visitar todas as células.

import random

from maze import Node


def build(start: Node):
    stack = [start]
    start.visited = True

    while stack:
        node = stack[-1]

        is_dead_end = True

        for link in (node.left_node, node.up_node, node.right_node, node.down_node):
            if link.node is not None and not link.node.visited:
                is_dead_end = False

        if is_dead_end:
            stack.pop()
            continue

        links = node.get_links()

        for link in links:
            neighbor = link.node
            if neighbor is not None and not neighbor.visited:
                node.open_passage(link)
                neighbor.visited = True
                stack.append(neighbor)
                break
