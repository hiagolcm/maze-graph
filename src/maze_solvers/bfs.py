import random
from collections import deque

from maze import Node

# ============================================================
# COMO ESCREVER UM SOLVER
# ============================================================
#
# O que o solver faz:
# - Recebe o no inicial (start), o no final (end) e a funcao draw_node.
# - Procura um caminho de start ate end andando SO por paredes abertas.
# - Retorne True se achou o end, ou False se nao achou.
#
# Modelo do labirinto:
# - Cada celula e um Node com 4 vizinhos (left/up/right/down_node).
# - Um vizinho so e passavel quando is_path_free == True.
#
# Funcoes uteis (ver maze.py):
# - node.get_reachable_neighbors() -> lista dos Nodes vizinhos que JA tem
#   caminho aberto. Ja filtra is_path_free e a borda. Ordem aleatoria.
# - draw_node(node) -> so serve para desenhar o no na tela. Chame toda vez
#   que quiser desenhar um no (normalmente, a cada no que o algoritmo visita).
#
# Flag "visited" (IMPORTANTE):
# - Node.visited e um booleano simples: True se o no ja foi visitado, False
#   se ainda nao.
# - O Maze chama self.clear_visited() antes de cada solve(), zerando todos
#   os nos. Seu algoritmo pode assumir que comeca com visited = False em
#   toda celula.
# - Marque um no como visitado assim que entrar nele:
#       node.visited = True
# - Um no ainda NAO foi visitado quando:
#       not node.visited
#
# Como testar:
# - Rode a partir de src/:
#       python3 main.py --solver bfs
# - O nome passado e o nome deste arquivo .py (sem extensao). O main.py
#   descobre os algoritmos sozinho; nao precisa editar nada la.
# - Combine com qualquer builder, ex.: python3 main.py --builder dead_end_dfs --solver bfs
# - Veja a lista atual com: python3 main.py --help
# - Use maze_solvers.dfs como referencia pronta.
#
# ============================================================
# Algoritmo: busca em largura (BFS)
# ============================================================
# - Use uma fila (FIFO). Comece pela celula start.
# - A cada passo, retire a frente da fila, visite e enfileire os vizinhos
#   alcancaveis ainda nao visitados.
# - BFS acha o caminho mais curto em numero de celulas.


def solve(start: Node, end: Node, draw_node):
    start.visited = True

    queue = deque([start])

    while len(queue) > 0:
        current = queue.popleft()
        current.state = "EXPANDED"
        draw_node(current, "EXPANDED")

        if current == end:
            return True

        neighbors = current.get_reachable_neighbors()

        for n in neighbors:
            if not n.visited:
                n.visited = True
                n.visited = True
                n.state = "DISCOVERED"
                draw_node(n, "DISCOVERED")
                queue.append(n)

    return False
