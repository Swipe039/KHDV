import sys
import time

from ortools.linear_solver import pywraplp

from simulation.csv_io import load_solve_input
from simulation.experiments.demand_stats import session_demand
from simulation.experiments.measure_fairness import resolve_capacity
from solver.model import group_block_ids_by_session
from solver.stages import group_block_ids_by_student


def level_weights(max_level, rho):
    return [rho ** (level - 1) for level in range(1, max_level + 1)]


def build_lp(solve_input, rho):
    solver = pywraplp.Solver.CreateSolver("GLOP")
    y = {
        block.block_id: solver.NumVar(0.0, 1.0, block.block_id)
        for block in solve_input.blocks
    }
    block_ids_by_student = group_block_ids_by_student(solve_input.blocks)
    block_ids_by_session = group_block_ids_by_session(solve_input.blocks)
    max_level = max((len(ids) for ids in block_ids_by_student.values()), default=0)
    weights = level_weights(max_level, rho)

    capacity_constraints = {}
    for session in sorted(block_ids_by_session):
        constraint = solver.Constraint(-solver.infinity(), solve_input.capacity, session)
        for block_id in block_ids_by_session[session]:
            constraint.SetCoefficient(y[block_id], 1)
        capacity_constraints[session] = constraint

    z = {}
    objective = solver.Objective()
    for student_id, block_ids in block_ids_by_student.items():
        link = solver.Constraint(-solver.infinity(), 0.0, f"link_{student_id}")
        for level in range(1, len(block_ids) + 1):
            var = solver.NumVar(0.0, 1.0, f"z_{student_id}_{level}")
            z[(student_id, level)] = var
            link.SetCoefficient(var, 1)
            objective.SetCoefficient(var, weights[level - 1])
        for block_id in block_ids:
            link.SetCoefficient(y[block_id], -1)
    objective.SetMaximization()
    return solver, y, z, capacity_constraints


def count_fractional(y, tolerance=1e-6):
    return sum(
        1 for var in y.values() if tolerance < var.solution_value() < 1 - tolerance
    )


def level_totals(z):
    totals = {}
    for (_, level), var in z.items():
        totals[level] = totals.get(level, 0.0) + var.solution_value()
    return totals


def trivial_caps(blocks):
    sizes = [len(ids) for ids in group_block_ids_by_student(blocks).values()]
    top = max(sizes, default=0)
    return {level: sum(1 for size in sizes if size >= level) for level in range(1, top + 1)}


def main():
    directory = sys.argv[1]
    spec = sys.argv[2]
    rho = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    base_input = load_solve_input(directory, capacity=0)
    capacity = resolve_capacity(session_demand(base_input.blocks), spec)
    solve_input = load_solve_input(directory, capacity=capacity)
    print(f"blocks={len(solve_input.blocks)} spec={spec} capacity={capacity} rho={rho}")

    solver, y, z, capacity_constraints = build_lp(solve_input, rho)
    started = time.perf_counter()
    status = solver.Solve()
    seconds = time.perf_counter() - started
    if status != pywraplp.Solver.OPTIMAL:
        print(f"status={status} seconds={seconds:.2f}")
        return

    print(f"status=OPTIMAL objective={solver.Objective().Value():.4f} seconds={seconds:.2f}")
    print(f"fractional_y={count_fractional(y)} of {len(y)}")

    totals = level_totals(z)
    caps = trivial_caps(solve_input.blocks)
    for level in sorted(totals):
        print(f"level={level} lp_m={totals[level]:.1f} trivial_cap={caps[level]}")

    duals = sorted(
        ((constraint.dual_value(), session) for session, constraint in capacity_constraints.items()),
        reverse=True,
    )
    positive = sum(1 for value, _ in duals if value > 1e-9)
    print(f"sessions_with_positive_price={positive} of {len(duals)}")
    for value, session in duals[:5]:
        print(f"price {session}={value:.5f}")


if __name__ == "__main__":
    main()