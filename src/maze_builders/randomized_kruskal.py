import random

from maze import Node

# ============================================================
# COMO ESCREVER UM BUILDER
# ============================================================
#
# O que o builder faz:
# - Recebe o no inicial (start) e abre paredes ate formar os caminhos.
# - Todas as paredes comecam fechadas. Abra apenas as que o algoritmo escolher.
# - O resultado deve conectar TODAS as celulas, sem ciclos (labirinto "perfeito").
#
# Modelo do labirinto:
# - Cada celula e um Node. Cada Node tem 4 vizinhos: left_node, up_node,
#   right_node, down_node.
# - Cada vizinho e um Neighbor com dois campos:
#     - node: a celula vizinha, ou None na borda do labirinto.
#     - is_path_free: False = parede fechada, True = caminho aberto.
# - O que liga duas celulas NAO e a aresta do grafo, e o is_path_free.
#   Abrir uma parede = tornar o caminho livre nos dois sentidos.
#
# Funcoes uteis (ver maze.py):
# - node.get_links() -> os 4 Neighbor em ordem aleatoria.
# - node.open_passage(link) -> abre a parede entre node e link.node.
# - Para percorrer a grade inteira (listar todas as celulas/paredes), siga os
#   .node dos vizinhos. Eles existem independente de is_path_free, que ainda
#   esta todo False no comeco da construcao.
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
#       python3 main.py --builder randomized_kruskal
# - O nome passado e o nome deste arquivo .py (sem extensao). O main.py
#   descobre os algoritmos sozinho; nao precisa editar nada la.
# - Veja a lista atual com: python3 main.py --help
# - Use maze_builders.dead_end_dfs como referencia pronta.
#
# ============================================================
# Algoritmo: Kruskal aleatorizado
# ============================================================
# - Cada celula comeca em seu proprio conjunto (use Union-Find).
# - Monte a lista de todas as paredes entre celulas vizinhas e embaralhe.
# - Para cada parede:
#     - Se os dois lados estao em conjuntos diferentes, abre a parede e une os
#       conjuntos.
#     - Se ja estao no mesmo conjunto, mantem a parede (abrir criaria um ciclo).
# - Dica: para listar todas as paredes, percorra a grade seguindo os .node dos
#   vizinhos (is_path_free ainda esta todo False aqui).


def build(start: Node):
    raise NotImplementedError("Implemente o Kruskal aleatorizado aqui")
