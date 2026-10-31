# Instrucoes
# - No labirinto, cada celula representa um no do grafo
# - Todos os grafos estao conectados com seus vizinhos de cima, de baixo, da direita e da esquerda
# - O que define se uma celula pode chegar a outra celula nao sao as arestas do grafo, mas sim o parametro is_path_free da classe Neighbour
# - Para pegar a lista de vizinhos utilize a funcao Node.get_links(). Ela retornara a lista de Neighbours
# - Utilize a funcao Node.open_passage para abrir o caminho entre duas celulas do labirinto
# - Use o mazebuildres.dead_end_dfs como referencia
# - Para testar seu algoritmo, mude o parametro "builder" do Maze no main.py

# Adaptação do algoritmo de Prim para geração de labirintos.
# - Começa com uma célula aleatória.
# - Adiciona seus vizinhos à lista de fronteira.
# - Escolhe aleatoriamente uma célula da fronteira.
# - Conecta essa célula a uma célula já visitada.
# - Adiciona seus vizinhos à fronteira.
# - Repete até visitar todas as células.

import random

def build(start: Node):
    raise NameError("Function not implemented")