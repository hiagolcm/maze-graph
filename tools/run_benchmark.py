#!/usr/bin/env python3
"""Run headless maze benchmarks and write raw CSV results."""

from __future__ import annotations

import argparse
import csv
import importlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from benchmark import MazeData  # noqa: E402
from maze import Maze  # noqa: E402

BUILDERS = ("dead_end_dfs", "randomized_kruskal", "randomized_prim")
SOLVERS = ("dfs", "bfs", "a_star")
DEFAULT_SIZES = (20, 40, 60, 80, 100)
DEFAULT_SEEDS = tuple(range(10))


def noop_draw(_node, _status):
    return None


def run_one(builder_name: str, solver_name: str, size: int, seed: int) -> dict:
    random.seed(seed)
    builder = importlib.import_module(f"maze_builders.{builder_name}").build
    solver = importlib.import_module(f"maze_solvers.{solver_name}").solve

    maze = Maze(size, size, builder=builder, solver=solver)
    maze.open_entrance_and_exit()
    maze.solve(noop_draw)

    data = MazeData()
    data.collect_from(maze)
    row = data.as_dict()
    row.update(
        {
            "builder": builder_name,
            "solver": solver_name,
            "width": size,
            "height": size,
            "dimension": size,
            "seed": seed,
        }
    )
    return row


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=list(DEFAULT_SIZES),
        help="square maze dimensions to benchmark",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="random seeds to average over",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "data" / "raw_results.csv",
        help="CSV output path",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "builder",
        "solver",
        "width",
        "height",
        "dimension",
        "seed",
        "build_time_ms",
        "solve_time_ms",
        "total_nodes",
        "expanded_nodes",
        "discovered_nodes",
        "total_edges",
        "average_degree",
        "average_corridor_length",
        "dead_ends",
        "junctions",
        "degree_0",
        "degree_1",
        "degree_2",
        "degree_3",
        "degree_4",
    ]

    total = len(BUILDERS) * len(SOLVERS) * len(args.sizes) * len(args.seeds)
    done = 0
    rows = []

    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for size in args.sizes:
            for seed in args.seeds:
                for builder_name in BUILDERS:
                    for solver_name in SOLVERS:
                        row = run_one(builder_name, solver_name, size, seed)
                        writer.writerow(row)
                        rows.append(row)
                        done += 1
                        if done % 25 == 0 or done == total:
                            print(f"[{done}/{total}] size={size} seed={seed} "
                                  f"{builder_name}/{solver_name}", flush=True)

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
