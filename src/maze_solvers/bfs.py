import random

from maze import Node

# ============================================================
# COMO ESCREVER UM SOLVER
# ============================================================
#
# O que o solver faz:
# - Recebe o no inicial (start), o no final (end) e a funcao visit.
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
# - visit(node) -> chame a cada no que o algoritmo visitar. Ela desenha o
#   caminho na tela.
#
# Contador "visited" (IMPORTANTE):
# - Node.visited NAO e booleano. E um contador (int) compartilhado por todas as
#   passagens (build, solve, desenho). Assim nao precisamos resetar cada no
#   entre uma passagem e outra.
# - No inicio, pegue o numero DESTA passagem a partir do start:
#       ref_visited_num = start.visited + 1
# - Um no ainda NAO foi visitado nesta passagem quando:
#       node.visited != ref_visited_num
# - Para marcar um no como visitado:
#       node.visited = ref_visited_num
# - Nunca compare com 0 nem use True/False. A passagem anterior deixou numeros
#   antigos espalhados pelos nos.
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


def solve(start: Node, end: Node, visit):
    raise NotImplementedError("Implemente a busca em largura (BFS) aqui")
