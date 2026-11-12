import argparse
import importlib
import json
import math
import os
import pkgutil
import random
import statistics
import time
from collections import deque

import maze_builders
import maze_solvers
from maze import Maze

# Faixas de distancia relativa ate a saida: 0-10%, 10-20%, ..., 90-100%
BINS = 10


def available(package):
    return sorted(module.name for module in pkgutil.iter_modules(package.__path__))


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compara a performance dos solvers em labirintos de cada builder. "
            "A entrada e sempre o canto superior esquerdo e a saida e sorteada "
            "(Maze.solve(random_end=True))."
        ),
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[20, 50, 100, 200, 300, 400, 500],
        help="lados dos labirintos quadrados (default: 20 50 100 200 300 400 500)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=10,
        help="quantidade de labirintos por builder e tamanho (default: 10)",
    )
    parser.add_argument(
        "--ends",
        type=int,
        default=20,
        help="saidas sorteadas por labirinto (default: 20)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="repeticoes de cada solve para medir o tempo; usa a mediana (default: 3)",
    )
    parser.add_argument(
        "--output",
        help="arquivo Markdown para salvar o relatorio (default: so imprime)",
    )
    parser.add_argument(
        "--json",
        help="arquivo JSON para salvar os numeros agregados",
    )
    parser.add_argument(
        "--raw",
        help="arquivo JSON para salvar cada amostra (distancia ate a saida, celulas visitadas, tempo)",
    )
    parser.add_argument(
        "--plots",
        help="pasta para salvar os graficos em PNG (precisa de matplotlib)",
    )
    return parser.parse_args()


def all_nodes(first):
    nodes = []
    stack = [first]
    seen = {first}

    while stack:
        node = stack.pop()
        nodes.append(node)

        for link in (node.left_node, node.right_node, node.up_node, node.down_node):
            if link.node is not None and link.node not in seen:
                seen.add(link.node)
                stack.append(link.node)

    return nodes


def steps_from(start):
    # Numero de passos de start ate cada celula, andando so por passagens abertas
    dist = {start: 0}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for n in node.get_reachable_neighbors():
            if n not in dist:
                dist[n] = dist[node] + 1
                queue.append(n)

    return dist


def degree(node):
    # Numero de passagens abertas da celula
    return sum(
        1
        for link in (node.left_node, node.right_node, node.up_node, node.down_node)
        if link.node is not None and link.is_path_free
    )


def dead_ends(nodes):
    return sum(1 for node in nodes if degree(node) == 1)


def mean_corridor(nodes):
    """Tamanho medio dos corredores: sequencias de celulas com exatamente duas passagens,
    entre bifurcacoes ou becos."""
    middle = {node for node in nodes if degree(node) == 2}
    seen, lengths = set(), []

    for node in middle:
        if node in seen:
            continue

        seen.add(node)
        stack, size = [node], 0
        while stack:
            current = stack.pop()
            size += 1
            for link in (current.left_node, current.right_node, current.up_node, current.down_node):
                n = link.node
                if n is not None and link.is_path_free and n in middle and n not in seen:
                    seen.add(n)
                    stack.append(n)
        lengths.append(size)

    return statistics.mean(lengths) if lengths else 0.0


def measure(maze, solve, start, end, seed, repeats):
    # Celulas visitadas nao dependem da repeticao (mesma semente); o tempo sim
    times = []
    visited = None

    for _ in range(repeats):
        maze.clear_visited()
        random.seed(seed)
        drawn = []

        begin = time.perf_counter()
        found = solve(start, end, drawn.append)
        times.append(time.perf_counter() - begin)

        assert found, "o solver nao achou a saida"
        visited = len(set(drawn))

    return visited, statistics.median(times) * 1000


def run(builders, solvers, size, args):
    """Gera os labirintos de um tamanho e mede cada solver em cada saida sorteada.

    Devolve (mazes, samples):
    - mazes[b]: becos e profundidade (maior distancia a partir da entrada) de cada labirinto
    - samples[b]: uma entrada por (labirinto, saida), com a distancia ate a saida e,
      para cada solver, as celulas visitadas e o tempo
    """
    cells = size * size
    mazes = {b: {"dead_ends": [], "depth": [], "corridor": []} for b in builders}
    samples = {b: [] for b in builders}
    solve_fns = {s: importlib.import_module(f"maze_solvers.{s}").solve for s in solvers}

    for b in builders:
        build = importlib.import_module(f"maze_builders.{b}").build

        for seed in range(args.seeds):
            random.seed(seed)
            maze = Maze(size, size, builder=build, solver=None)

            nodes = all_nodes(maze.first)
            start = maze.first
            steps = steps_from(start)
            depth = max(steps.values())
            mazes[b]["dead_ends"].append(dead_ends(nodes) / cells)
            mazes[b]["depth"].append(depth / cells)
            mazes[b]["corridor"].append(mean_corridor(nodes))

            # Mesmo sorteio do Maze.solve(random_end=True); rng proprio para nao
            # depender da semente global, que o measure() reinicia
            rng = random.Random(seed)
            for _ in range(args.ends):
                end = maze.pick_end(random_end=True, rng=rng)
                manhattan = abs(end.x - start.x) + abs(end.y - start.y)
                sample = {
                    "size": size,
                    "steps": steps[end],
                    # 0 = colado na entrada, 1 = a celula mais distante da entrada
                    "rel": steps[end] / depth,
                    "dist": steps[end] / cells,
                    # quanto o caminho real e maior que a distancia de Manhattan
                    "ratio": steps[end] / manhattan,
                    "visited": {},
                    "ms": {},
                }

                # Todos os solvers resolvem o mesmo labirinto, com a mesma saida
                for s in solvers:
                    v, ms = measure(maze, solve_fns[s], start, end, seed, args.repeats)
                    sample["visited"][s] = v / cells
                    sample["ms"][s] = ms
                    sample.setdefault("us_per_cell", {})[s] = ms * 1000 / v

                samples[b].append(sample)

    return mazes, samples


def mean_ci(values):
    # Media e meia-largura do intervalo de confianca de 95%
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, 0.0
    return mean, 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def fmt_pct(values):
    mean, ci = mean_ci(values)
    return f"{mean * 100:.1f}% ±{ci * 100:.1f}"


def percentile(sorted_values, p):
    # Interpolacao linear entre os dois valores vizinhos (p entre 0 e 100)
    k = (len(sorted_values) - 1) * p / 100
    lo = math.floor(k)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def stats(values):
    # Media, desvio padrao e os percentis usados nos graficos de distribuicao
    v = sorted(values)
    return {
        "n": len(v),
        "mean": statistics.mean(v),
        "sd": statistics.stdev(v) if len(v) > 1 else 0.0,
        "p5": percentile(v, 5),
        "q1": percentile(v, 25),
        "median": percentile(v, 50),
        "q3": percentile(v, 75),
        "p95": percentile(v, 95),
    }


def bin_stats(groups, solver, key):
    # [n, media, desvio padrao] de cada faixa de distancia (media e desvio ficam None se n < 2)
    out = []
    for g in groups:
        vals = [x[key][solver] for x in g]
        if len(vals) >= 2:
            out.append([len(vals), statistics.mean(vals), statistics.stdev(vals)])
        else:
            out.append([len(vals), None, None])
    return out


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines + [""]


def win_share(samples, solvers, key):
    # Vence quem tem o menor valor; empate divide o ponto
    wins = {s: 0.0 for s in solvers}
    for sample in samples:
        best = min(sample[key][s] for s in solvers)
        winners = [s for s in solvers if sample[key][s] == best]
        for s in winners:
            wins[s] += 1 / len(winners)
    return {s: wins[s] / len(samples) for s in solvers}


def by_bin(samples):
    # Agrupa as amostras pela faixa de distancia relativa (0-10%, ..., 90-100%)
    groups = [[] for _ in range(BINS)]
    for sample in samples:
        groups[min(int(sample["rel"] * BINS), BINS - 1)].append(sample)
    return groups


def summary(builders, solvers, sizes, args, results):
    every = {b: [x for size in sizes for x in results[size][1][b]] for b in builders}
    largest = sizes[-1]

    data = {
        "config": {
            "sizes": sizes,
            "seeds": args.seeds,
            "ends": args.ends,
            "repeats": args.repeats,
            "bins": BINS,
        },
        "builders": builders,
        "solvers": solvers,
        "mazes": {
            b: {
                "dead_ends": mean_ci([v for size in sizes for v in results[size][0][b]["dead_ends"]]),
                "corridor": mean_ci([v for size in sizes for v in results[size][0][b]["corridor"]]),
                "depth": [mean_ci(results[size][0][b]["depth"]) for size in sizes],
            }
            for b in builders
        },
        "solves": {},
        "distance": {},
    }

    for b in builders:
        biggest = results[largest][1][b]
        data["solves"][b] = {
            s: {
                "visited": statistics.mean(x["visited"][s] for x in every[b]),
                "visited_by_size": [
                    mean_ci([x["visited"][s] for x in results[size][1][b]]) for size in sizes
                ],
                "ms_by_size": [
                    statistics.mean(x["ms"][s] for x in results[size][1][b]) for size in sizes
                ],
                "ms_largest": statistics.mean(x["ms"][s] for x in biggest),
                "us_per_cell": statistics.median(x["us_per_cell"][s] for x in every[b]),
                "wins": win_share(every[b], solvers, "visited")[s],
                "time_wins": win_share(every[b], solvers, "ms")[s],
                "n": len(every[b]),
                "visited_stats": stats([x["visited"][s] for x in every[b]]),
                "ms_stats_largest": stats([x["ms"][s] for x in biggest]),
            }
            for s in solvers
        }

        groups = by_bin(every[b])
        groups_big = by_bin(biggest)
        data["distance"][b] = {
            "ratio_median": statistics.median(x["ratio"] for x in every[b]),
            "ratio_median_largest": statistics.median(x["ratio"] for x in biggest),
            # por faixa de distancia relativa: [n, media, desvio] de visitadas com todos os tamanhos,
            # e de ms so no maior tamanho
            "visited_by_bin": {s: bin_stats(groups, s, "visited") for s in solvers},
            "ms_by_bin_largest": {s: bin_stats(groups_big, s, "ms") for s in solvers},
        }

    return data


def raw_points(builders, solvers, sizes, results):
    raw = {}
    for b in builders:
        every = [x for size in sizes for x in results[size][1][b]]
        raw[b] = {
            "size": [x["size"] for x in every],
            "rel": [round(x["rel"], 5) for x in every],
            "dist": [round(x["dist"], 5) for x in every],
            "ratio": [round(x["ratio"], 4) for x in every],
            "visited": {s: [round(x["visited"][s], 5) for x in every] for s in solvers},
            "ms": {s: [round(x["ms"][s], 5) for x in every] for s in solvers},
        }
    return raw


def report(builders, solvers, sizes, args, data, plots):
    total = args.seeds * args.ends
    lines = [
        "# Comparativo de solvers por builder",
        "",
        "Gerado por `python3 benchmark.py`. Configuracao desta rodada:",
        "",
        f"- Tamanhos: {', '.join(f'{s}x{s}' for s in sizes)}",
        f"- {args.seeds} labirintos por builder e tamanho "
        f"({args.seeds * len(sizes) * len(builders)} labirintos no total)",
        "- Entrada sempre no canto superior esquerdo; saida sorteada em qualquer celula, "
        f"via `Maze.solve(random_end=True)`: {args.ends} saidas por labirinto "
        f"({total} amostras por builder e tamanho)",
        f"- Tempo: mediana de {args.repeats} repeticoes de cada solve",
        "",
        "Como ler:",
        "",
        "- **Celulas visitadas**: fracao do labirinto que o solver visitou ate "
        "achar a saida. Quanto menor, melhor. O `±` e a meia-largura do "
        "intervalo de confianca de 95% da media.",
        "- **Vitorias**: em quantos % dos casos o solver visitou menos celulas (ou foi "
        "mais rapido) que os outros dois, no mesmo labirinto e com a mesma saida. "
        "Empates dividem o ponto.",
        "- **Distancia relativa ate a saida**: passos da entrada ate a saida divididos pela "
        "maior distancia possivel a partir da entrada naquele labirinto (0% = colada na "
        "entrada, 100% = a celula mais distante).",
        "- Os labirintos sao perfeitos (so existe um caminho), entao os tres "
        "solvers acham o mesmo caminho. O que muda e quanto exploram ate acha-lo.",
        "",
    ]

    def img(key, alt):
        return [f"![{alt}]({plots[key]})", ""] if plots else []

    lines += ["## Labirintos gerados", ""]
    lines += img("mazes", "Profundidade e becos")
    lines += ["Becos sem saida, em % das celulas (media de todos os tamanhos):", ""]
    lines += table(builders, [[f"{data['mazes'][b]['dead_ends'][0] * 100:.1f}%" for b in builders]])
    lines += ["Tamanho medio dos corredores, em celulas (media de todos os tamanhos):", ""]
    lines += table(builders, [[f"{data['mazes'][b]['corridor'][0]:.1f} ±{data['mazes'][b]['corridor'][1]:.1f}" for b in builders]])
    lines += ["Maior distancia a partir da entrada, em % das celulas:", ""]
    rows = [
        [f"{size}x{size}"]
        + [f"{data['mazes'][b]['depth'][i][0] * 100:.1f}%" for b in builders]
        for i, size in enumerate(sizes)
    ]
    lines += table(["Tamanho"] + builders, rows)
    lines += ["Caminho ate a saida dividido pela distancia de Manhattan (mediana):", ""]
    lines += table(
        ["Escopo"] + builders,
        [
            ["todos os tamanhos"] + [f"{data['distance'][b]['ratio_median']:.2f}" for b in builders],
            [f"{sizes[-1]}x{sizes[-1]}"] + [f"{data['distance'][b]['ratio_median_largest']:.2f}" for b in builders],
        ],
    )

    lines += ["## Celulas visitadas", ""]
    lines += img("visited_spread", "Distribuicao de celulas visitadas")
    rows = []
    for b in builders:
        for s in solvers:
            st = data["solves"][b][s]["visited_stats"]
            rows.append(
                [b, s, f"{st['mean'] * 100:.1f}%", f"{st['sd'] * 100:.1f}", f"{st['median'] * 100:.1f}%",
                 f"{st['q1'] * 100:.1f}% a {st['q3'] * 100:.1f}%", f"{st['p5'] * 100:.1f}% a {st['p95'] * 100:.1f}%"]
            )
    lines += ["Celulas visitadas (todos os tamanhos): media, desvio padrao, mediana, quartis (25% a 75%) e extremos (5% a 95%):", ""]
    lines += table(["Builder", "Busca", "Media", "Desvio", "Mediana", "Quartis", "Extremos"], rows)
    lines += img("wins", "Vitorias em celulas visitadas")
    rows = []
    for b in builders:
        w = {s: data["solves"][b][s]["wins"] for s in solvers}
        top = max(w.values())
        best = " / ".join(s for s in solvers if math.isclose(w[s], top))
        rows.append([b] + [f"{w[s] * 100:.0f}%" for s in solvers] + [f"**{best}**"])
    lines += ["Vitorias (visitou menos celulas):", ""]
    lines += table(["Builder"] + solvers + ["Melhor"], rows)

    lines += img("visited_by_size", "Celulas visitadas por tamanho")
    for b in builders:
        lines += [f"**{b}**", ""]
        rows = [
            [f"{size}x{size}"]
            + [
                f"{data['solves'][b][s]['visited_by_size'][i][0] * 100:.1f}% "
                f"±{data['solves'][b][s]['visited_by_size'][i][1] * 100:.1f}"
                for s in solvers
            ]
            for i, size in enumerate(sizes)
        ]
        lines += table(["Tamanho"] + solvers, rows)

    lines += ["## Distancia ate a saida e celulas visitadas", ""]
    lines += img("distance", "Visitadas por distancia")
    for b in builders:
        lines += [f"**{b}** (media ± desvio padrao de celulas visitadas por faixa de distancia relativa; n = amostras)", ""]
        bins = data["distance"][b]["visited_by_bin"]
        rows = []
        for i in range(BINS):
            n = bins[solvers[0]][i][0]
            label = f"{i * 100 // BINS}-{(i + 1) * 100 // BINS}%"
            rows.append(
                [label, str(n)]
                + [
                    f"{bins[s][i][1] * 100:.1f}% ±{bins[s][i][2] * 100:.1f}" if bins[s][i][1] is not None else "-"
                    for s in solvers
                ]
            )
        lines += table(["Distancia", "n"] + solvers, rows)

    lines += ["## Tempo de execucao", ""]
    lines += img("cost", "Custo por celula")
    lines += img("time_spread", "Distribuicao do tempo")
    rows = []
    for b in builders:
        for s in solvers:
            st = data["solves"][b][s]["ms_stats_largest"]
            rows.append(
                [b, s, f"{st['mean']:.1f}", f"{st['sd']:.1f}", f"{st['median']:.1f}",
                 f"{st['q1']:.1f} a {st['q3']:.1f}", f"{st['p5']:.1f} a {st['p95']:.1f}"]
            )
    lines += [f"Tempo em ms nos labirintos {sizes[-1]}x{sizes[-1]}: media, desvio padrao, mediana, quartis e extremos:", ""]
    lines += table(["Builder", "Busca", "Media", "Desvio", "Mediana", "Quartis", "Extremos"], rows)
    lines += img("time_wins", "Vitorias em tempo")
    rows = []
    for b in builders:
        w = {s: data["solves"][b][s]["time_wins"] for s in solvers}
        top = max(w.values())
        best = " / ".join(s for s in solvers if math.isclose(w[s], top))
        rows.append([b] + [f"{w[s] * 100:.0f}%" for s in solvers] + [f"**{best}**"])
    lines += ["Vitorias por tempo (foi a mais rapida):", ""]
    lines += table(["Builder"] + solvers + ["Mais rapida"], rows)

    rows = [[b] + [f"{data['solves'][b][s]['us_per_cell']:.2f}" for s in solvers] for b in builders]
    lines += ["Custo por celula visitada (µs, mediana):", ""]
    lines += table(["Builder"] + solvers, rows)

    lines += img("time_growth", "Crescimento do tempo")
    for b in builders:
        lines += [f"**{b}** (tempo medio, ms)", ""]
        rows = [
            [f"{size}x{size}"] + [f"{data['solves'][b][s]['ms_by_size'][i]:.2f}" for s in solvers]
            for i, size in enumerate(sizes)
        ]
        lines += table(["Tamanho"] + solvers, rows)

    lines += [f"## Distancia ate a saida e tempo ({sizes[-1]}x{sizes[-1]})", ""]
    lines += img("time_distance", "Tempo por distancia")
    for b in builders:
        lines += [f"**{b}** (tempo medio ± desvio padrao, em ms, por faixa de distancia relativa)", ""]
        bins = data["distance"][b]["ms_by_bin_largest"]
        rows = []
        for i in range(BINS):
            n = bins[solvers[0]][i][0]
            label = f"{i * 100 // BINS}-{(i + 1) * 100 // BINS}%"
            rows.append(
                [label, str(n)]
                + [
                    f"{bins[s][i][1]:.2f} ±{bins[s][i][2]:.2f}" if bins[s][i][1] is not None else "-"
                    for s in solvers
                ]
            )
        lines += table(["Distancia", "n"] + solvers, rows)

    return "\n".join(lines)


def main():
    args = parse_args()
    builders = available(maze_builders)
    solvers = available(maze_solvers)

    results = {}
    for size in args.sizes:
        print(f"rodando {size}x{size}...", flush=True)
        results[size] = run(builders, solvers, size, args)

    data = summary(builders, solvers, args.sizes, args, results)
    raw = raw_points(builders, solvers, args.sizes, results)

    plots = None
    if args.plots:
        from benchmark_plots import make_plots

        # Caminho dos PNGs relativo ao relatorio, para o Markdown achar as imagens
        base = os.path.dirname(os.path.abspath(args.output)) if args.output else os.getcwd()
        names = make_plots(data, raw, args.plots)
        plots = {k: os.path.relpath(os.path.join(args.plots, v), base) for k, v in names.items()}

    text = report(builders, solvers, args.sizes, args, data, plots)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(data, f, indent=1)
        print(f"numeros salvos em {args.json}")

    if args.raw:
        with open(args.raw, "w") as f:
            json.dump(raw, f)
        print(f"amostras salvas em {args.raw}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(text + "\n")
        print(f"relatorio salvo em {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
