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
# Flag "visited" (IMPORTANTE):
# - Node.visited e um booleano simples: True se o no ja foi visitado, False
#   se ainda nao.
# - O Maze chama self.clear_visited() depois do builder terminar, zerando
#   todos os nos. Seu algoritmo pode assumir que comeca com visited = False
#   em toda celula.
# - Marque um no como visitado assim que entrar nele:
#       node.visited = True
# - Um no ainda NAO foi visitado quando:
#       not node.visited
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


def find(parent, node: Node):
    while parent[node] is not node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node


def build(start: Node):
    # Lista todas as paredes. So right e down, para nao repetir cada parede.
    walls = []
    start.visited = True
    stack = [start]

    while stack:
        node = stack.pop()

        for link in (node.right_node, node.down_node):
            if link.node is not None:
                walls.append((node, link))

        for link in (node.left_node, node.up_node, node.right_node, node.down_node):
            if link.node is not None and not link.node.visited:
                link.node.visited = True
                stack.append(link.node)

    random.shuffle(walls)

    parent = {}
    for node, link in walls:
        parent.setdefault(node, node)
        parent.setdefault(link.node, link.node)

    for node, link in walls:
        a = find(parent, node)
        b = find(parent, link.node)

        if a is not b:
            node.open_passage(link)
            parent[a] = b
