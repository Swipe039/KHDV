import hashlib
import sys

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from simulation.experiments.measure_fairness import resolve_capacity
from solver.solve import solve
from solver.types import SolveConfig


def fingerprint(status):
    granted = sorted(block_id for block_id, state in status.items() if state == "granted")
    return hashlib.sha256("\n".join(granted).encode()).hexdigest()[:12]


def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    seed = int(sys.argv[3])
    total_time = float(sys.argv[4])
    num_workers = int(sys.argv[5])
    random_max_weight = int(sys.argv[6])
    base_input = load_solve_input(directory, capacity=0)
    capacity = resolve_capacity(session_demand(base_input.blocks), spec)
    solve_input = load_solve_input(directory, capacity=capacity, seed=seed)
    config = SolveConfig(
        total_time_limit=total_time,
        num_workers=num_workers,
        random_max_weight=random_max_weight,
    )
    print(
        f"capacity={capacity} seed={seed} workers={num_workers} "
        f"random_max_weight={random_max_weight}",
        flush=True,
    )
    result = solve(solve_input, config)
    for stage in result.stages:
        print(
            f"{stage.name}: status={stage.status} value={stage.value} "
            f"gap={stage.bound - stage.value} seconds={stage.seconds:.1f}"
        )
    print(
        f"all_optimal={result.all_optimal} proven_prefix={result.proven_prefix}/{result.levels_total} "
        f"deviation={result.deviation} total_seconds={result.total_seconds:.1f}"
    )
    print(
        f"fairness_levels={result.fairness_levels} "
        f"max_occupancy={max(result.occupancy.values())} "
        f"granted={sum(1 for state in result.status.values() if state == 'granted')} "
        f"fingerprint={fingerprint(result.status)}"
    )


if __name__ == "__main__":
    main()