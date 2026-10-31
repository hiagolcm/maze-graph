# maze-graph

Gera labirintos e os resolve, com visualização em pygame. O labirinto é um grafo: cada célula é um nó com quatro vizinhos. Um `builder` abre as paredes para criar o labirinto. Um `solver` procura o caminho da entrada até a saída.

## Requisitos

- Python 3.11
- pygame 2.6

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
```

## Como rodar

```bash
cd src
python3 main.py
```

Uma janela abre com o labirinto. O solver percorre o caminho em vermelho. Feche a janela para sair.

## Escolher os algoritmos

Passe o builder e o solver por parâmetro:

```bash
python3 main.py --builder dead_end_dfs --solver dfs
```

Opções:

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `--builder` | `dead_end_dfs` | algoritmo que constrói o labirinto |
| `--solver` | `dfs` | algoritmo que resolve o labirinto |
| `--seed` | `0` | semente aleatória; a mesma semente gera o mesmo labirinto |
| `--width` | `100` | largura em células |
| `--height` | `100` | altura em células |

Os valores de `--builder` e `--solver` saem dos arquivos nas pastas `maze_builders/` e `maze_solvers/`. Rode `python3 main.py --help` para ver a lista atual.

Exemplo com labirinto menor e outra semente:

```bash
python3 main.py --builder randomized_prim --solver a_star --width 30 --height 30 --seed 42
```

## Estrutura

```
src/
  main.py            # CLI e loop de desenho
  maze.py            # Node, Neighbor, Maze
  draw_utils.py      # desenho das células com pygame
  constants.py       # tamanho padrão e escala
  maze_builders/     # um arquivo por algoritmo de construção
  maze_solvers/      # um arquivo por algoritmo de resolução
```

## Contribuir com um algoritmo

Cada builder vive em `maze_builders/<nome>.py` e expõe `build(start)`. Cada solver vive em `maze_solvers/<nome>.py` e expõe `solve(start, end, visit)`. O `main.py` descobre o arquivo pelo nome, então nenhum registro manual é necessário.

Cada placeholder traz um cabeçalho com o modelo do labirinto, as funções disponíveis e o contador `visited`. Use `maze_builders/dead_end_dfs.py` e `maze_solvers/dfs.py` como referência pronta.

### O contador `visited`

`Node.visited` é um contador inteiro, não um booleano. Ele é compartilhado pelas três passagens sobre o grafo: construir, resolver e desenhar. Assim nenhum nó precisa ser resetado entre uma passagem e outra.

No início do seu algoritmo, pegue o número desta passagem a partir do `start`:

```python
ref_visited_num = start.visited + 1
```

Um nó ainda não foi visitado nesta passagem quando `node.visited != ref_visited_num`. Para marcar um nó como visitado, use `node.visited = ref_visited_num`. Não compare com `0` nem use `True`/`False`: a passagem anterior deixou números antigos nos nós.
