#!/usr/bin/env python3
"""Generate benchmark charts from raw_results.csv."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

BUILDER_LABELS = {
    "dead_end_dfs": "DFS (dead-end)",
    "randomized_kruskal": "Kruskal",
    "randomized_prim": "Prim",
}
SOLVER_LABELS = {
    "dfs": "DFS",
    "bfs": "BFS",
    "a_star": "A*",
}
BUILDER_ORDER = list(BUILDER_LABELS)
SOLVER_ORDER = list(SOLVER_LABELS)

# Closely related shades: darker = expanded, lighter = discovered remainder
SOLVER_COLORS = {
    "dfs": ("#2F5F8A", "#7FA8C9"),
    "bfs": ("#2E7D32", "#81C784"),
    "a_star": ("#C62828", "#E57373"),
}


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = []
        for raw in csv.DictReader(handle):
            row = dict(raw)
            for key in (
                "width",
                "height",
                "dimension",
                "seed",
                "total_nodes",
                "expanded_nodes",
                "discovered_nodes",
                "total_edges",
                "dead_ends",
                "junctions",
                "degree_0",
                "degree_1",
                "degree_2",
                "degree_3",
                "degree_4",
            ):
                row[key] = int(float(row[key]))
            for key in (
                "build_time_ms",
                "solve_time_ms",
                "average_degree",
                "average_corridor_length",
            ):
                row[key] = float(row[key])
            rows.append(row)
    return rows


def mean(values):
    return statistics.fmean(values) if values else math.nan


def style_axes(ax, title, xlabel, ylabel):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)


def chart_generation_time(rows, out_dir: Path):
    buckets = defaultdict(list)
    for row in rows:
        key = (row["builder"], row["dimension"], row["seed"])
        buckets[key].append(row["build_time_ms"])

    by_builder_dim = defaultdict(list)
    for (builder, dim, _), times in buckets.items():
        by_builder_dim[(builder, dim)].append(mean(times))

    dims = sorted({d for _, d in by_builder_dim})
    fig, ax = plt.subplots(figsize=(9, 5))
    for builder in BUILDER_ORDER:
        means = [mean(by_builder_dim.get((builder, dim), [])) for dim in dims]
        ax.plot(dims, means, marker="o", label=BUILDER_LABELS[builder])

    style_axes(
        ax,
        "Generation time by builder and maze dimension",
        "Maze dimension (N×N cells)",
        "Mean generation time (ms)",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "01_generation_time.png", dpi=160)
    plt.close(fig)


def chart_solve_time(rows, out_dir: Path):
    dims = sorted({r["dimension"] for r in rows})
    fig, axes = plt.subplots(1, len(BUILDER_ORDER), figsize=(14, 4.5), sharey=True)

    for ax, builder in zip(axes, BUILDER_ORDER):
        for solver in SOLVER_ORDER:
            means = [
                mean(
                    [
                        r["solve_time_ms"]
                        for r in rows
                        if r["builder"] == builder
                        and r["solver"] == solver
                        and r["dimension"] == dim
                    ]
                )
                for dim in dims
            ]
            ax.plot(dims, means, marker="o", label=SOLVER_LABELS[solver])
        ax.set_title(BUILDER_LABELS[builder])
        ax.set_xlabel("Maze dimension (N×N)")
        ax.grid(True, alpha=0.3)
        ax.legend()

    axes[0].set_ylabel("Mean solve time (ms)")
    fig.suptitle("Solve time by solver, maze dimension, and builder")
    fig.tight_layout()
    fig.savefig(out_dir / "02_solve_time.png", dpi=160)
    plt.close(fig)


def chart_nodes(rows, out_dir: Path):
    """One stacked bar per solver: expanded + (discovered - expanded)."""
    dims = sorted({r["dimension"] for r in rows})
    x = np.arange(len(dims))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5.5))

    for i, solver in enumerate(SOLVER_ORDER):
        expanded = []
        frontier = []
        for dim in dims:
            exp_vals = [
                r["expanded_nodes"]
                for r in rows
                if r["solver"] == solver and r["dimension"] == dim
            ]
            disc_vals = [
                r["discovered_nodes"]
                for r in rows
                if r["solver"] == solver and r["dimension"] == dim
            ]
            exp_mean = mean(exp_vals)
            disc_mean = mean(disc_vals)
            expanded.append(exp_mean)
            frontier.append(max(disc_mean - exp_mean, 0.0))

        offset = (i - (len(SOLVER_ORDER) - 1) / 2) * width
        dark, light = SOLVER_COLORS[solver]
        label = SOLVER_LABELS[solver]
        ax.bar(
            x + offset,
            expanded,
            width,
            label=f"{label} expanded",
            color=dark,
        )
        ax.bar(
            x + offset,
            frontier,
            width,
            bottom=expanded,
            label=f"{label} discovered",
            color=light,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in dims])
    style_axes(
        ax,
        "Expanded and discovered nodes by solver and maze dimension",
        "Maze dimension (N×N cells)",
        "Mean node count",
    )
    ax.legend(ncols=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "03_expanded_discovered_nodes.png", dpi=160)
    plt.close(fig)


def chart_corridor_length(rows, out_dir: Path):
    samples = {}
    for row in rows:
        key = (row["builder"], row["dimension"], row["seed"])
        samples[key] = row["average_corridor_length"]

    data = [
        [v for (b, _, _), v in samples.items() if b == builder]
        for builder in BUILDER_ORDER
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(data, tick_labels=[BUILDER_LABELS[b] for b in BUILDER_ORDER], showmeans=True)
    style_axes(
        ax,
        "Average corridor length by generator",
        "Generator",
        "Average corridor length (cells)",
    )
    fig.tight_layout()
    fig.savefig(out_dir / "04_avg_corridor_length.png", dpi=160)
    plt.close(fig)


def chart_dead_ends_junctions(rows, out_dir: Path):
    samples = {}
    for row in rows:
        key = (row["builder"], row["dimension"], row["seed"])
        samples[key] = (row["dead_ends"], row["junctions"])

    dead_means = []
    junc_means = []
    for builder in BUILDER_ORDER:
        dead = [v[0] for (b, _, _), v in samples.items() if b == builder]
        junc = [v[1] for (b, _, _), v in samples.items() if b == builder]
        dead_means.append(mean(dead))
        junc_means.append(mean(junc))

    x = np.arange(len(BUILDER_ORDER))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, dead_means, width, label="Dead ends")
    ax.bar(x + width / 2, junc_means, width, label="Junctions")
    ax.set_xticks(x)
    ax.set_xticklabels([BUILDER_LABELS[b] for b in BUILDER_ORDER])
    style_axes(
        ax,
        "Dead ends and junctions by generator",
        "Generator",
        "Mean cell count (all sizes/seeds)",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "05_dead_ends_junctions.png", dpi=160)
    plt.close(fig)


def chart_generation_time_box(rows, out_dir: Path):
    samples = defaultdict(list)
    for row in rows:
        key = (row["builder"], row["dimension"], row["seed"])
        samples[key].append(row["build_time_ms"])
    flat = {k: mean(v) for k, v in samples.items()}

    dims = sorted({d for _, d, _ in flat})
    fig, ax = plt.subplots(figsize=(10, 5))
    positions = []
    data = []
    tick_pos = []
    tick_labels = []
    pos = 1
    for dim in dims:
        for builder in BUILDER_ORDER:
            data.append(
                [v for (b, d, _), v in flat.items() if b == builder and d == dim]
            )
            positions.append(pos)
            pos += 1
        tick_pos.append(pos - 2)
        tick_labels.append(str(dim))
        pos += 1

    bp = ax.boxplot(data, positions=positions, widths=0.6, showmeans=True)
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for i, box in enumerate(bp["boxes"]):
        box.set_color(colors[i % 3])

    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labels)
    style_axes(
        ax,
        "Generation time distribution by dimension (colored by builder)",
        "Maze dimension (N×N cells)",
        "Generation time (ms)",
    )
    handles = [
        plt.Line2D([0], [0], color=colors[i], lw=3, label=BUILDER_LABELS[b])
        for i, b in enumerate(BUILDER_ORDER)
    ]
    ax.legend(handles=handles)
    fig.tight_layout()
    fig.savefig(out_dir / "06_generation_time_box.png", dpi=160)
    plt.close(fig)


def chart_degree_distribution(rows, out_dir: Path):
    """Mean share of cells by degree for each generator."""
    samples = {}
    for row in rows:
        key = (row["builder"], row["dimension"], row["seed"])
        samples[key] = row

    degrees = (1, 2, 3, 4)
    shares = {builder: {d: [] for d in degrees} for builder in BUILDER_ORDER}

    for (builder, _, _), row in samples.items():
        total = row["total_nodes"] or 1
        for d in degrees:
            shares[builder][d].append(100.0 * row[f"degree_{d}"] / total)

    x = np.arange(len(degrees))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#4C78A8", "#F58518", "#54A24B"]

    for i, builder in enumerate(BUILDER_ORDER):
        values = [mean(shares[builder][d]) for d in degrees]
        ax.bar(
            x + (i - 1) * width,
            values,
            width,
            label=BUILDER_LABELS[builder],
            color=colors[i],
        )

    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in degrees])
    style_axes(
        ax,
        "Degree distribution by generator",
        "Node degree",
        "Mean share of cells (%)",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "07_degree_distribution.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "reports" / "data" / "raw_results.csv",
    )
    parser.add_argument(
        "--charts-dir",
        type=Path,
        default=ROOT / "reports" / "charts",
    )
    args = parser.parse_args()

    rows = load_rows(args.input)
    if not rows:
        raise SystemExit(f"No rows in {args.input}")

    args.charts_dir.mkdir(parents=True, exist_ok=True)

    chart_generation_time(rows, args.charts_dir)
    chart_solve_time(rows, args.charts_dir)
    chart_nodes(rows, args.charts_dir)
    chart_corridor_length(rows, args.charts_dir)
    chart_dead_ends_junctions(rows, args.charts_dir)
    chart_generation_time_box(rows, args.charts_dir)
    chart_degree_distribution(rows, args.charts_dir)
    print(f"Wrote charts to {args.charts_dir}")


if __name__ == "__main__":
    main()
