import math
import sys
from statistics import mean

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from solver.model import build_model
from solver.stages import solve_fairness_stage


def print_report(report):
    print(
        f"level={report.level} count={report.count} bound={report.bound} "
        f"status={report.status} seconds={report.seconds:.1f}",
        flush=True,
    )

def resolve_capacity(demand, spec):
    if spec == "peak":
        return max(demand.values())
    return math.ceil(float(spec) * mean(demand.values()))

def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    time_limit = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
    base_input = load_solve_input(directory, capacity=0)
    demand = session_demand(base_input.blocks)
    capacity = resolve_capacity(demand, spec)
    solve_input = load_solve_input(directory, capacity=capacity)
    print(
        f"blocks={len(solve_input.blocks)} spec={spec} capacity={capacity} "
        f"time_limit={time_limit}",
        flush=True,
    )

    model, y = build_model(solve_input)
    reports = solve_fairness_stage(
        model,
        y,
        solve_input.blocks,
        time_limit_per_level=time_limit,
        on_level=print_report,
    )
    print(f"total_seconds={sum(report.seconds for report in reports):.1f}")


if __name__ == "__main__":
    main()