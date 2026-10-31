# Instrucoes
# - No labirinto, cada celula representa um no do grafo
# - Todos os grafos estao conectados com seus vizinhos de cima, de baixo, da direita e da esquerda
# - O que define se uma celula pode chegar a outra celula nao sao as arestas do grafo, mas sim o parametro is_path_free da classe Neighbour
# - Para pegar a lista de vizinhos utilize a funcao Node.get_links(). Ela retornara a lista de Neighbours
# - Utilize a funcao Node.open_passage para abrir o caminho entre duas celulas do labirinto
# - Use o mazebuildres.dead_end_dfs como referencia
# - Para testar seu algoritmo, mude o parametro "builder" do Maze no main.py

# Descricao do algoritmo
# Uma adaptação do algoritmo de Kruskal para gerar uma árvore geradora.
# - Inicialmente, cada célula pertence a um conjunto independente.
# - Cria uma lista de todas as paredes entre células vizinhas.
# - Embaralha essa lista.
# - Para cada parede:
#   - Se as células pertencem a conjuntos diferentes, remove a parede.
#   - Une os dois conjuntos usando Union-Find.
#   - Caso contrário, mantém a parede.

import random

def build(start: Node):
    raise NameError("Function not implemented")