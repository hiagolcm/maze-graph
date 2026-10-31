# Descricao do algoritmo
# - Escolhe uma célula inicial.
# - Visita vizinhos ainda não visitados.
# - Remove paredes entre as células.
# - Quando chega a um beco sem saída, retorna (backtracking).
# - Continua até visitar todas as células.

import random

from maze import Node


def build(start: Node):
    ref_visited_num = start.visited + 1

    stack = [start]
    start.visited = ref_visited_num

    while stack:
        node = stack[-1]

        if node.is_dead_end(ref_visited_num):
            stack.pop()
            continue

        links = node.get_links()

        for link in links:
            neighbor = link.node
            if neighbor is not None and neighbor.visited != ref_visited_num:
                node.open_passage(link)
                neighbor.visited = ref_visited_num
                stack.append(neighbor)
                break