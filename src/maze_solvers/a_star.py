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
# - Cada Node tem coordenadas node.x (coluna) e node.y (linha).
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
# - No main.py, passe a sua funcao solve no parametro "solver" do Maze.
# - Use maze_solvers.dfs como referencia pronta.
#
# ============================================================
# Algoritmo: A*
# ============================================================
# - Use uma fila de prioridade ordenada por f = g + h.
#     - g = custo real do start ate o no (numero de passos).
#     - h = heuristica, estimativa do no ate o end. Para grade, use a distancia
#       de Manhattan: abs(node.x - end.x) + abs(node.y - end.y).
# - A cada passo, expanda o no de menor f e relaxe os vizinhos alcancaveis.
# - A heuristica de Manhattan nunca superestima, entao o caminho achado e otimo.


def solve(start: Node, end: Node, visit):
    raise NotImplementedError("Implemente o A* aqui")
