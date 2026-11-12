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
#       python3 main.py --builder randomized_prim
# - O nome passado e o nome deste arquivo .py (sem extensao). O main.py
#   descobre os algoritmos sozinho; nao precisa editar nada la.
# - Veja a lista atual com: python3 main.py --help
# - Use maze_builders.dead_end_dfs como referencia pronta.
#
# ============================================================
# Algoritmo: Prim aleatorizado
# ============================================================
# - Comeca por uma celula qualquer e a marca como visitada.
# - Mantem uma lista de "fronteira": paredes entre uma celula visitada e uma
#   nao visitada.
# - Repete ate a fronteira esvaziar:
#     - Escolhe uma parede aleatoria da fronteira.
#     - Se a celula do outro lado ainda nao foi visitada, abre a parede,
#       marca a celula como visitada e adiciona as novas paredes de fronteira.
#     - Caso contrario, descarta a parede.


def add_frontier(node: Node, frontier):
    for link in node.get_links():
        if link.node is not None and not link.node.visited:
            frontier.append((node, link))


def build(start: Node):
    start.visited = True
    frontier = []
    add_frontier(start, frontier)

    while frontier:
        # Troca o escolhido com o ultimo para remover em O(1)
        i = random.randrange(len(frontier))
        frontier[i], frontier[-1] = frontier[-1], frontier[i]
        node, link = frontier.pop()

        neighbor = link.node
        if neighbor.visited:
            continue

        node.open_passage(link)
        neighbor.visited = True
        add_frontier(neighbor, frontier)
