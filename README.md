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
| `--random-end` | desligado | sorteia a célula de saída (marcada em verde) em vez de usar o canto inferior direito; a entrada continua no canto superior esquerdo |

Os valores de `--builder` e `--solver` saem dos arquivos nas pastas `maze_builders/` e `maze_solvers/`. Rode `python3 main.py --help` para ver a lista atual.

Exemplo com labirinto menor e outra semente:

```bash
python3 main.py --builder randomized_prim --solver a_star --width 30 --height 30 --seed 42
```

## Comparar os solvers

O `benchmark.py` resolve os mesmos labirintos com todos os solvers, para cada builder, e mede quantas células cada um visita até achar a saída e quanto tempo leva. A entrada é sempre o canto superior esquerdo e a saída é sorteada com o mesmo mecanismo do `Maze.solve(random_end=True)`, várias vezes por labirinto. Para cada saída ele registra a distância até ela (em passos, relativa à célula mais distante da entrada e comparada com a distância de Manhattan), para estudar como a distância afeta cada busca. Não abre janela nem precisa de pygame (os gráficos usam matplotlib).

```bash
python3 benchmark.py --output ../BENCHMARK.md --plots ../docs/benchmark \
  --json ../docs/benchmark/results.json --raw ../docs/benchmark/points.json
```

Para escolher a saída em código, passe `random_end` ao `Maze.solve`; a célula escolhida fica em `maze.end`:

```python
maze.solve(draw_node)                    # saída no canto inferior direito
maze.solve(draw_node, random_end=True)   # saída sorteada
```

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `--sizes` | `20 50 100 200 300 400 500` | lados dos labirintos quadrados (500×500 = 250.000 células) |
| `--seeds` | `10` | quantidade de labirintos por builder e tamanho (a mesma em todos os tamanhos) |
| `--ends` | `20` | saídas sorteadas por labirinto |
| `--repeats` | `3` | repetições de cada solve para medir o tempo (usa a mediana) |
| `--output` | — | arquivo Markdown para salvar o relatório |
| `--plots` | — | pasta para salvar os gráficos em PNG |
| `--json` | — | arquivo JSON com os números agregados |
| `--raw` | — | arquivo JSON com cada amostra (distância até a saída, células visitadas e tempo) |

Para redesenhar os gráficos sem rodar o benchmark de novo: `python3 benchmark_plots.py --json ../docs/benchmark/results.json --raw ../docs/benchmark/points.json --out ../docs/benchmark`.

O resultado mais recente está em [BENCHMARK.md](BENCHMARK.md). Os tempos variam conforme a máquina; as células visitadas não, porque as sementes são fixas. A rodada completa leva uns 40 minutos, quase todos nos labirintos de 300×300 a 500×500. Para um teste rápido: `python3 benchmark.py --sizes 20 50 100 --seeds 5 --repeats 2`.

Além das médias, o relatório traz o **desvio padrão**, os quartis e os percentis 5 e 95 de cada busca, porque o custo varia muito conforme a distância até a saída: `visited_spread.png` e `time_spread.png` mostram a distribuição inteira, e os gráficos de distância têm uma faixa de ± 1 desvio padrão.

## Slides

A apresentação em [slides/index.html](slides/index.html) explica a modelagem, anima os seis algoritmos e mostra os resultados do benchmark. Abra o arquivo no navegador; use as setas para navegar, `P` para rodar ou pausar a animação, `R` para reiniciar e `F` para tela cheia.

Os gráficos leem `slides/results.js`. Para atualizar depois de rodar o benchmark com `--json`:

```bash
(printf 'window.BENCHMARK = '; cat ../docs/benchmark/results.json; printf ';\n') > ../slides/results.js
```

## Estrutura

```
src/
  main.py            # CLI e loop de desenho
  benchmark.py       # comparativo dos solvers por builder
  benchmark_plots.py # gráficos do benchmark (matplotlib)
  maze.py            # Node, Neighbor, Maze
  draw_utils.py      # desenho das células com pygame
  constants.py       # tamanho padrão e escala
  maze_builders/     # um arquivo por algoritmo de construção
  maze_solvers/      # um arquivo por algoritmo de resolução
slides/              # apresentação com animações e resultados
docs/benchmark/      # gráficos e números do benchmark
```

## Contribuir com um algoritmo

Cada builder vive em `maze_builders/<nome>.py` e expõe `build(start)`. Cada solver vive em `maze_solvers/<nome>.py` e expõe `solve(start, end, draw_node)`. A função `draw_node` só serve para desenhar o nó na tela; chame-a sempre que quiser desenhar um nó. O `main.py` descobre o arquivo pelo nome, então nenhum registro manual é necessário.

Cada placeholder traz um cabeçalho com o modelo do labirinto, as funções disponíveis e a flag `visited`. Use `maze_builders/dead_end_dfs.py` e `maze_solvers/dfs.py` como referência pronta.

