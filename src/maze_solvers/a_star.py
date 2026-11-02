import heapq

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
# - Cada Node tem coordenadas node.x (coluna) e node.y (linha).
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
#       python3 main.py --solver a_star
# - O nome passado e o nome deste arquivo .py (sem extensao). O main.py
#   descobre os algoritmos sozinho; nao precisa editar nada la.
# - Combine com qualquer builder, ex.: python3 main.py --builder dead_end_dfs --solver a_star
# - Veja a lista atual com: python3 main.py --help
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

def heuristic (node:Node, end: Node) -> int: 
    return abs(node.x - end.x) + abs(node.y - end.y)


def solve(start: Node, end: Node, draw_node):
    open_set = [] 
    counter = 0
    
    
    heapq.heappush(
        open_set,
        (heuristic(start,end), counter, start)
    )
    g = {start: 0}
    closed_set = set()
    
    while open_set:
        _,_, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        if current == end:
            current.state = "EXPANDED"
            draw_node(current, "EXPANDED")
            return True
        
        closed_set.add(current)
        current.visited = True
        current.state = "EXPANDED"
        draw_node(current, "EXPANDED")
        
        for neighbor in current.get_reachable_neighbors():
            possible_g = g[current] + 1
            
            if possible_g >= g.get(neighbor,float("inf")):
                continue
            
            g[neighbor] = possible_g
            
            f = possible_g + heuristic(neighbor, end)
            
            counter += 1
            
            heapq.heappush(
                open_set,
                (f, counter, neighbor)
            )

            neighbor.state = "DISCOVERED"
            draw_node(neighbor, "DISCOVERED")

    return False
    
