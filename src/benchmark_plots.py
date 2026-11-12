"""Graficos do benchmark (precisa de matplotlib).

Uso direto, a partir dos arquivos gerados pelo benchmark.py:

    python3 benchmark_plots.py --json ../docs/benchmark/results.json \
        --raw ../docs/benchmark/points.json --out ../docs/benchmark

O benchmark.py tambem chama make_plots() quando recebe --plots.
"""

import argparse
import json
import os
import statistics

SOLVER_ORDER = ["dfs", "bfs", "a_star"]
SOLVER_LABEL = {"dfs": "DFS", "bfs": "BFS", "a_star": "A*"}
SOLVER_COLOR = {"dfs": "#2a78d6", "bfs": "#eb6834", "a_star": "#1baf7a"}

BUILDER_ORDER = ["dead_end_dfs", "randomized_prim", "randomized_kruskal"]
BUILDER_LABEL = {
    "dead_end_dfs": "DFS com dead-end",
    "randomized_prim": "Prim",
    "randomized_kruskal": "Kruskal",
}
BUILDER_COLOR = {
    "dead_end_dfs": "#6250d6",
    "randomized_prim": "#e87ba4",
    "randomized_kruskal": "#008300",
}

SURFACE, INK, MUTED, GRID = "#ffffff", "#1b2333", "#4a5263", "#e4e7ec"


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
            "axes.edgecolor": GRID,
            "text.color": INK,
        }
    )
    return plt


def _num(x, digits=1):
    return f"{x:.{digits}f}".replace(".", ",")


def _pct(x, digits=0):
    return f"{_num(x, digits)}%"


def _style(ax, grid="y"):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)


def _title(fig, text, sub=None, sub_y=0.915):
    fig.suptitle(text, color=INK, fontsize=14, fontweight="bold", x=0.01, ha="left", y=0.99)
    if sub:
        fig.text(0.01, sub_y, sub, color=MUTED, fontsize=10, ha="left", va="top")


def _save(fig, folder, name):
    import matplotlib.pyplot as plt

    fig.patch.set_facecolor(SURFACE)
    fig.savefig(os.path.join(folder, name), dpi=160, facecolor=SURFACE)
    plt.close(fig)
    return name


def _order(data):
    builders = [b for b in BUILDER_ORDER if b in data["builders"]]
    solvers = [s for s in SOLVER_ORDER if s in data["solvers"]]
    return builders, solvers


def _spread(data, key, title, subtitle, name, ylabel, pct, note, folder):
    """Distribuicao por gerador e busca: caixa (quartis), tracos (5% a 95%), mediana e media ± desvio padrao."""
    plt = _plt()
    builders, solvers = _order(data)
    f = 100 if pct else 1

    fig, axes = plt.subplots(1, len(builders), figsize=(13, 4.9), sharey=True)
    _title(fig, title, subtitle)
    top = 0
    for ax, b in zip(axes, builders):
        boxes = []
        for s in solvers:
            st = data["solves"][b][s][key]
            boxes.append({"med": st["median"] * f, "q1": st["q1"] * f, "q3": st["q3"] * f,
                          "whislo": st["p5"] * f, "whishi": st["p95"] * f, "fliers": []})
            top = max(top, st["p95"] * f, (st["mean"] + st["sd"]) * f)
        bp = ax.bxp(boxes, positions=range(len(solvers)), widths=0.42, showfliers=False, patch_artist=True,
                    boxprops={"linewidth": 1.4}, whiskerprops={"linewidth": 1.4},
                    capprops={"linewidth": 1.4}, medianprops={"color": INK, "linewidth": 2.4})
        labels = []
        for i, s in enumerate(solvers):
            col = SOLVER_COLOR[s]
            bp["boxes"][i].set(facecolor=col, alpha=0.35, edgecolor=col)
            for k in (2 * i, 2 * i + 1):
                bp["whiskers"][k].set_color(col)
                bp["caps"][k].set_color(col)
            st = data["solves"][b][s][key]
            ax.errorbar(i + 0.36, st["mean"] * f, yerr=st["sd"] * f, fmt="D", color=INK, markersize=6.5,
                        ecolor=INK, elinewidth=1.6, capsize=4)
            labels.append(f"{SOLVER_LABEL[s]}\n{_num(st['mean'] * f, 0 if pct else 1)}{'%' if pct else ' ms'}"
                          f" ± {_num(st['sd'] * f, 0 if pct else 1)}")
        ax.set_xticks(range(len(solvers)), labels, fontsize=10)
        ax.set_title(BUILDER_LABEL[b], loc="left", fontsize=12, color=BUILDER_COLOR[b], fontweight="bold")
        _style(ax)
    for ax in axes:
        if pct:
            ax.set_ylim(-3, 103)
            ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        else:
            ax.set_ylim(-0.03 * top, top * 1.08)
            ax.yaxis.set_major_formatter(lambda v, _: _num(v, 0))
    axes[0].set_ylabel(ylabel, color=MUTED, fontsize=9)
    fig.text(0.01, 0.01, note, color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.86))
    return _save(fig, folder, name)


def visited_spread(data, folder):
    return _spread(
        data, "visited_stats", "Quanto cada busca explora, e o quanto isso varia",
        "células visitadas até a saída sorteada · caixa = quartis (25% a 75%), traços = 5% a 95%, linha = mediana",
        "visited_spread.png", "células visitadas", True,
        "Losango com barra = média ± desvio padrão (também no nome de cada busca) · todos os tamanhos", folder)


def time_spread(data, folder):
    size = data["config"]["sizes"][-1]
    return _spread(
        data, "ms_stats_largest", "Quanto tempo cada busca leva, e o quanto isso varia",
        f"tempo em milissegundos nos labirintos {size}×{size} · caixa = quartis (25% a 75%), traços = 5% a 95%, linha = mediana",
        "time_spread.png", "ms", False,
        "Losango com barra = média ± desvio padrão (também no nome de cada busca)", folder)


def wins(data, folder, key="wins", title="Quem visita menos células",
         subtitle="% dos casos em que a busca explorou menos que as outras duas",
         name="wins.png"):
    plt = _plt()
    builders, solvers = _order(data)

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    _title(fig, title, subtitle)
    h = 0.24
    for gi, b in enumerate(builders):
        for si, s in enumerate(solvers):
            p = data["solves"][b][s][key]
            n = data["solves"][b][s]["n"]
            v = 100 * p
            ci = 196 * (p * (1 - p) / n) ** 0.5  # IC 95% da proporcao (binomial), em pontos percentuais
            y = gi + (si - 1) * h
            ax.barh(y, v, height=h * 0.9, color=SOLVER_COLOR[s], label=SOLVER_LABEL[s] if gi == 0 else None)
            ax.errorbar(v, y, xerr=ci, fmt="none", ecolor=INK, elinewidth=1.2, capsize=3)
            ax.text(min(v + ci, 100) + 1.2, y, _pct(v), va="center", fontsize=11, color=INK)
    ax.set_yticks(range(len(builders)), [BUILDER_LABEL[b] for b in builders], fontsize=12)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    _style(ax, grid="x")
    ax.legend(frameon=False, fontsize=11, loc="lower right")
    fig.text(0.01, 0.01, "Mesmo labirinto e mesma saída para as três buscas · empate divide o ponto · "
             "barra de erro = intervalo de confiança de 95%", color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.86))
    return _save(fig, folder, name)


def visited_by_size(data, folder):
    plt = _plt()
    sizes = data["config"]["sizes"]
    builders, solvers = _order(data)

    fig, axes = plt.subplots(1, len(builders), figsize=(13, 4.4), sharey=True)
    _title(fig, "Células visitadas por tamanho", "faixa = intervalo de confiança de 95%")
    for ax, b in zip(axes, builders):
        for s in solvers:
            pts = data["solves"][b][s]["visited_by_size"]
            y = [m * 100 for m, _ in pts]
            ci = [c * 100 for _, c in pts]
            ax.fill_between(sizes, [a - c for a, c in zip(y, ci)], [a + c for a, c in zip(y, ci)],
                            color=SOLVER_COLOR[s], alpha=0.14, linewidth=0)
            ax.plot(sizes, y, color=SOLVER_COLOR[s], linewidth=2.2, marker="o", markersize=4.5, label=SOLVER_LABEL[s])
        ax.set_title(BUILDER_LABEL[b], loc="left", fontsize=12, color=BUILDER_COLOR[b], fontweight="bold")
        ax.set_xlabel("lado do labirinto (células)", color=MUTED, fontsize=9)
        ax.set_ylim(0, 105)
        ax.set_xticks(sizes)
        ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        _style(ax)
    axes[-1].legend(frameon=False, fontsize=10, loc="lower right")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return _save(fig, folder, "visited_by_size.png")


def time_growth(data, folder):
    plt = _plt()
    sizes = data["config"]["sizes"]
    builders, solvers = _order(data)
    top = max(v for b in builders for s in solvers for v in data["solves"][b][s]["ms_by_size"]) * 1.08

    fig, axes = plt.subplots(1, len(builders), figsize=(13, 4.4), sharey=True)
    _title(fig, "Como o tempo cresce com o tamanho do labirinto",
           "tempo médio em milissegundos · cresce de forma quase linear com o número de células")
    for ax, b in zip(axes, builders):
        for s in solvers:
            ax.plot(sizes, data["solves"][b][s]["ms_by_size"], color=SOLVER_COLOR[s], linewidth=2.2,
                    marker="o", markersize=4.5, label=SOLVER_LABEL[s])
        ax.set_title(BUILDER_LABEL[b], loc="left", fontsize=12, color=BUILDER_COLOR[b], fontweight="bold")
        ax.set_xlabel("lado do labirinto (células)", color=MUTED, fontsize=9)
        ax.set_xticks(sizes)
        ax.set_ylim(0, top)
        _style(ax)
    axes[0].set_ylabel("ms", color=MUTED, fontsize=9)
    axes[0].legend(frameon=False, fontsize=10, loc="upper left")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return _save(fig, folder, "time_growth.png")


def cost_per_cell(data, folder):
    plt = _plt()
    builders, solvers = _order(data)
    vals = {s: statistics.mean(data["solves"][b][s]["us_per_cell"] for b in builders) for s in solvers}
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    _title(fig, "Custo de cada célula visitada", "microssegundos, mediana · média dos geradores")
    bars = ax.bar([SOLVER_LABEL[s] for s in solvers], [vals[s] for s in solvers],
                  color=[SOLVER_COLOR[s] for s in solvers], width=0.55)
    for bar, s in zip(bars, solvers):
        ax.text(bar.get_x() + bar.get_width() / 2, vals[s] + 0.02, _num(vals[s], 2),
                ha="center", fontsize=12, fontweight="bold", color=INK)
    if "a_star" in vals and "dfs" in vals and "bfs" in vals:
        simple = (vals["dfs"] + vals["bfs"]) / 2
        ax.text(0.99, 0.95, f"A* custa ~{_num(vals['a_star'] / simple)}× mais por célula",
                transform=ax.transAxes, ha="right", va="top", fontsize=10, color=MUTED)
    ax.set_ylim(0, max(vals.values()) * 1.25)
    ax.yaxis.set_major_formatter(lambda v, _: _num(v))
    _style(ax)
    ax.tick_params(axis="x", labelsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    return _save(fig, folder, "cost.png")


def mazes(data, folder):
    plt = _plt()
    sizes = data["config"]["sizes"]
    builders, _ = _order(data)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1.5, 1]})
    _title(fig, "Como são os labirintos de cada gerador",
           "esquerda: maior distância a partir da entrada · direita: becos sem saída")
    for b in builders:
        pts = data["mazes"][b]["depth"]
        y = [m * 100 for m, _ in pts]
        ci = [c * 100 for _, c in pts]
        ax1.fill_between(sizes, [a - c for a, c in zip(y, ci)], [a + c for a, c in zip(y, ci)],
                         color=BUILDER_COLOR[b], alpha=0.14, linewidth=0)
        ax1.plot(sizes, y, color=BUILDER_COLOR[b], linewidth=2.2, marker="o", markersize=4.5, label=BUILDER_LABEL[b])
    ax1.set_xticks(sizes)
    ax1.set_xlabel("lado do labirinto (células)", color=MUTED, fontsize=9)
    ax1.set_ylabel("célula mais distante da entrada (% das células)", color=MUTED, fontsize=9)
    ax1.set_ylim(bottom=0)
    ax1.legend(frameon=False, fontsize=10, loc="upper right")
    _style(ax1)

    vals = [data["mazes"][b]["dead_ends"][0] * 100 for b in builders]
    ax2.bar([BUILDER_LABEL[b] for b in builders], vals, color=[BUILDER_COLOR[b] for b in builders], width=0.55)
    for i, v in enumerate(vals):
        ax2.text(i, v + 0.8, _pct(v), ha="center", fontsize=12, fontweight="bold", color=INK)
    ax2.set_ylim(0, max(vals) * 1.2)
    ax2.set_ylabel("células que são becos", color=MUTED, fontsize=9)
    _style(ax2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return _save(fig, folder, "mazes.png")


def _by_distance(data, folder, key, title, subtitle, ylabel, name, pct, note):
    plt = _plt()
    builders, solvers = _order(data)
    bins = data["config"]["bins"]
    xs = [100 * (i + 0.5) / bins for i in range(bins)]

    fig, axes = plt.subplots(1, len(builders), figsize=(13, 4.4), sharey=True)
    _title(fig, title, subtitle)
    top = 0
    for ax, b in zip(axes, builders):
        for s in solvers:
            pts = [(x, v, sd) for x, (n, v, sd) in zip(xs, data["distance"][b][key][s]) if n >= 5 and v is not None]
            f = 100 if pct else 1
            ys = [v * f for _, v, _ in pts]
            lo = [max((v - sd) * f, 0) for _, v, sd in pts]
            hi = [(v + sd) * f for _, v, sd in pts]
            if pct:
                hi = [min(h, 100) for h in hi]
            top = max([top] + hi)
            ax.fill_between([x for x, _, _ in pts], lo, hi, color=SOLVER_COLOR[s], alpha=0.12, linewidth=0)
            ax.plot([x for x, _, _ in pts], ys, color=SOLVER_COLOR[s], linewidth=2.2, marker="o", markersize=4.5,
                    label=SOLVER_LABEL[s])
        ax.set_title(BUILDER_LABEL[b], loc="left", fontsize=12, color=BUILDER_COLOR[b], fontweight="bold")
        ax.set_xlabel("distância até a saída (% da maior distância possível)", color=MUTED, fontsize=9)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        _style(ax)
    for ax in axes:
        if pct:
            ax.set_ylim(0, 105)
            ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        else:
            ax.set_ylim(0, top * 1.1)
            ax.yaxis.set_major_formatter(lambda v, _: _num(v))
    axes[0].set_ylabel(ylabel, color=MUTED, fontsize=9)
    axes[0].legend(frameon=False, fontsize=10, loc="upper left")
    fig.text(0.01, 0.01, note, color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.88))
    return _save(fig, folder, name)


def distance(data, folder):
    return _by_distance(
        data, folder, "visited_by_bin",
        "Quanto mais longe a saída, mais cada busca explora",
        "média de células visitadas por faixa de distância até a saída · todos os tamanhos",
        "células visitadas", "distance.png", True,
        "linha = média · faixa = ± 1 desvio padrão · 0% = saída colada na entrada, 100% = a célula mais distante")


def time_distance(data, folder):
    size = data["config"]["sizes"][-1]
    return _by_distance(
        data, folder, "ms_by_bin_largest",
        "Quanto mais longe a saída, mais tempo cada busca leva",
        f"tempo médio em milissegundos por faixa de distância até a saída · labirintos {size}×{size}",
        "ms", "time_distance.png", False,
        "linha = média · faixa = ± 1 desvio padrão · 0% = saída colada na entrada, 100% = a célula mais distante")


def make_plots(data, raw, folder):
    """Gera todos os graficos em folder e devolve {chave: nome do arquivo}."""
    os.makedirs(folder, exist_ok=True)
    return {
        "visited_spread": visited_spread(data, folder),
        "wins": wins(data, folder),
        "visited_by_size": visited_by_size(data, folder),
        "distance": distance(data, folder),
        "mazes": mazes(data, folder),
        "cost": cost_per_cell(data, folder),
        "time_spread": time_spread(data, folder),
        "time_wins": wins(data, folder, key="time_wins", title="Quem termina primeiro",
                          subtitle="% dos casos em que a busca foi a mais rápida das três",
                          name="time_wins.png"),
        "time_growth": time_growth(data, folder),
        "time_distance": time_distance(data, folder),
    }


def main():
    parser = argparse.ArgumentParser(description="Redesenha os graficos a partir dos JSONs do benchmark.")
    parser.add_argument("--json", required=True, help="results.json gerado por benchmark.py --json")
    parser.add_argument("--raw", help="points.json gerado por benchmark.py --raw (opcional)")
    parser.add_argument("--out", required=True, help="pasta de saida dos PNGs")
    args = parser.parse_args()

    with open(args.json) as f:
        data = json.load(f)
    raw = None
    if args.raw:
        with open(args.raw) as f:
            raw = json.load(f)

    for name in make_plots(data, raw, args.out).values():
        print(os.path.join(args.out, name))


if __name__ == "__main__":
    main()
