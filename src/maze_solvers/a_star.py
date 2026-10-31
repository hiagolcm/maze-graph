# Instrucoes
# - No labirinto, cada celula representa um no do grafo
# - Todos os grafos estao conectados com seus vizinhos de cima, de baixo, da direita e da esquerda
# - O que define se uma celula pode chegar a outra celula nao sao as arestas do grafo, mas sim o parametro is_path_free da classe Neighbour
# - Para pegar a lista de vizinhos utilize a funcao Node.get_reachable_neighbors(). Ele retorna a lista de vizinhos que possuem caminho livre
# - Toda vez que o seu agoritmo visitar um node novo, chame a funcao "visit" passando o node como parametro (eg: visit(no_visitado)). Essa funcao sera responsavel por printar o caminho na tela
# - Para testar seu algoritmo, mude o parametro "solver" do Maze no main.py
# - Use o maze_solvers.dfs como referencia


import random


def solve(start: Node, visit):
    raise NameError("Function not implemented")
