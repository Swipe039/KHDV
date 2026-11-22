import sys

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from simulation.experiments.measure_fairness import resolve_capacity
from solver.fairness import *
from solver.model import build_model


def run_one(solve_input, base, time_limit):
    model, y = build_model(solve_input)
    report, _ = solve_weighted_fairness(
        model, y, solve_input.blocks, base=base, time_limit=time_limit
    )
    caps = trivial_level_caps(solve_input.blocks)
    weights = integer_level_weights(len(caps), base)
    flags = lexicographic_flags(report.level_counts, caps, weights)
    return report, flags, weights


def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    time_limit = float(sys.argv[3])
    bases = [int(text) for text in sys.argv[4:]]
    base_input = load_solve_input(directory, capacity=0)
    capacity = resolve_capacity(session_demand(base_input.blocks), spec)
    solve_input = load_solve_input(directory, capacity=capacity)
    print(f"blocks={len(solve_input.blocks)} spec={spec} capacity={capacity}", flush=True)
    for base in bases:
        report, flags, weights = run_one(solve_input, base, time_limit)
        deviation = deviation_bound(report.level_counts, weights, flags)
        print(
            f"base={base} status={report.status} gap={report.bound - report.value} "
            f"seconds={report.seconds:.1f} certified_prefix={proven_prefix(report, flags)} "
            f"deviation={deviation}",
            flush=True,
        )
        print(f"  counts={report.level_counts}", flush=True)


if __name__ == "__main__":
    main()