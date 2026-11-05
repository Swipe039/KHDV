import math
import sys
from collections import Counter
from statistics import mean

from simulation.csv_io import load_solve_input

def session_demand(blocks):
    return Counter(session for block in blocks for session in block.sessions)

def capacity_levels(demand):
    average = mean(demand.values())
    peak = max(demand.values())
    return {
        "50% mean": math.ceil(0.5 * average),
        "75% mean": math.ceil(0.75 * average),
        "100% mean": math.ceil(average),
        "100% peak": peak,
    }

def main():
    solve_input = load_solve_input(sys.argv[1], capacity=0)
    demand = session_demand(solve_input.blocks)
    for session in sorted(demand):
        print(f"{session} demand={demand[session]}")

    values = list(demand.values())
    print(
        f"sessions={len(values)} mean={mean(values):.1f} "
        f"min={min(values)} max={max(values)}"
    )
    for name, capacity in capacity_levels(demand).items():
        print(f"{name}: capacity={capacity}")

if __name__ == "__main__":
    main()