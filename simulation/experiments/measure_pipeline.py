import hashlib
import sys
from collections import Counter

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from simulation.experiments.measure_fairness import resolve_capacity
from solver.fairness import (
    integer_level_weights,
    lexicographic_flags,
    proven_prefix,
    solve_weighted_fairness,
    trivial_level_caps,
)
from solver.model import build_model
from solver.stages import length_weights, random_weights, solve_weighted_stage


def occupancy_of(blocks, values):
    return Counter(
        session
        for block in blocks
        if values[block.block_id] == 1
        for session in block.sessions
    )


def fingerprint(values):
    granted = sorted(block_id for block_id, value in values.items() if value == 1)
    return hashlib.sha256("\n".join(granted).encode()).hexdigest()[:12]


def print_objective(name, report):
    print(
        f"{name}: status={report.status} value={report.value} bound={report.bound} "
        f"gap={report.bound - report.value} seconds={report.seconds:.1f}",
        flush=True,
    )


def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    seed = int(sys.argv[3])
    time_limit = float(sys.argv[4])
    base = int(sys.argv[5]) if len(sys.argv) > 5 else 64
    base_input = load_solve_input(directory, capacity=0)
    capacity = resolve_capacity(session_demand(base_input.blocks), spec)
    solve_input = load_solve_input(directory, capacity=capacity, seed=seed)
    print(f"blocks={len(solve_input.blocks)} capacity={capacity} seed={seed} base={base}", flush=True)

    model, y = build_model(solve_input)
    report, _ = solve_weighted_fairness(
        model, y, solve_input.blocks, base=base, time_limit=time_limit
    )
    caps = trivial_level_caps(solve_input.blocks)
    flags = lexicographic_flags(
        report.level_counts, caps, integer_level_weights(len(caps), base)
    )
    print(
        f"fairness: status={report.status} seconds={report.seconds:.1f} "
        f"proven_prefix={proven_prefix(report, flags)} counts={report.level_counts}",
        flush=True,
    )

    length_report, _ = solve_weighted_stage(
        model, y, length_weights(solve_input.blocks), time_limit=time_limit
    )
    print_objective("length", length_report)

    weights = random_weights(solve_input.blocks, solve_input.seed)
    random_report, values = solve_weighted_stage(model, y, weights, time_limit=time_limit)
    print_objective("random", random_report)

    occupancy = occupancy_of(solve_input.blocks, values)
    print(
        f"granted={sum(values.values())} max_occupancy={max(occupancy.values())} "
        f"capacity={capacity} fingerprint={fingerprint(values)}"
    )


if __name__ == "__main__":
    main()