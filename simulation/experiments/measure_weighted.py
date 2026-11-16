import sys

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from simulation.experiments.measure_fairness import resolve_capacity
from solver.fairness import *
from solver.model import build_model

def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    base = int(sys.argv[3] if len(sys.argv) > 4 else 4)
    time_limit = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0
    base_input = load_solve_input(directory, capacity=0)
    capacity = resolve_capacity(session_demand(base_input.blocks), spec)
    solve_input = load_solve_input(directory, capacity=capacity)
    print(f"blocks={len(solve_input.blocks)} spec={spec} capacity={capacity} base={base}")
    
    model, y = build_model(solve_input)
    report, _ = solve_weighted_fairness(model, y, solve_input.blocks, base=base, time_limit=time_limit)
    caps = trivial_level_caps(solve_input.blocks)
    weights = integer_level_weights(len(caps), base)
    flags = lexicographic_flags(report.level_counts, caps, weights)
    gap = report.bound - report.value
    print(
        f"status={report.status} value={report.value} bound={report.bound} "
        f"gap={gap} seconds={report.seconds:.1f}"
    )
    for level, (count, cap, flag) in enumerate(zip(report.level_counts, caps, flags), start=1):
        print(f"level={level} count={count} trivial_cap={cap} certified={flag}")
    print(f"certified_prefix={certified_prefix(flags)} of {len(caps)}")


if __name__ == "__main__":
    main()