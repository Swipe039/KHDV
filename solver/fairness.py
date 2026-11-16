import math
import time
from dataclasses import dataclass

from ortools.sat.python import cp_model

from solver.model import extract_values
from solver.stages import group_block_ids_by_student


@dataclass(frozen=True)
class WeightedFairnessReport:
    value: int
    bound: int
    status: str
    seconds: float
    level_counts: tuple[int, ...]


def integer_level_weights(max_level, base):
    return [base ** (max_level - level) for level in range(1, max_level + 1)]


def trivial_level_caps(blocks):
    sizes = [len(ids) for ids in group_block_ids_by_student(blocks).values()]
    top = max(sizes, default=0)
    return [sum(1 for size in sizes if size >= level) for level in range(1, top + 1)]


def lexicographic_flags(level_counts, caps, weights):
    flags = []
    for index, count in enumerate(level_counts):
        if count == caps[index]:
            flags.append(True)
            continue
        tail = sum(
            weights[later] * level_counts[later]
            for later in range(index + 1, len(level_counts))
        )
        flags.append(weights[index] > tail)
    return flags


def certified_prefix(flags):
    prefix = 0
    for flag in flags:
        if not flag:
            break
        prefix += 1
    return prefix


def solve_weighted_fairness(model, y, blocks, base=4, time_limit=60.0):
    block_ids_by_student = group_block_ids_by_student(blocks)
    max_level = max((len(ids) for ids in block_ids_by_student.values()), default=0)
    if max_level == 0:
        return WeightedFairnessReport(0, 0, "OPTIMAL", 0.0, ()), {}

    weights = integer_level_weights(max_level, base)
    if weights[0] * len(block_ids_by_student) >= 2 ** 62:
        raise ValueError("base is too large for int64 objective")

    x = {}
    terms = []
    coefficients = []
    for student_id, block_ids in block_ids_by_student.items():
        levels = [
            model.new_bool_var(f"x_{student_id}_{level}")
            for level in range(1, len(block_ids) + 1)
        ]
        model.add(sum(levels) == sum(y[block_id] for block_id in block_ids))
        for earlier, later in zip(levels, levels[1:]):
            model.add(earlier >= later)
        for level, var in enumerate(levels, start=1):
            x[(student_id, level)] = var
            terms.append(var)
            coefficients.append(weights[level - 1])

    expression = cp_model.LinearExpr.weighted_sum(terms, coefficients)
    model.maximize(expression)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    started = time.perf_counter()
    status = solver.solve(model)
    seconds = time.perf_counter() - started
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("weighted fairness found no solution")

    value = round(solver.objective_value)
    bound = math.floor(solver.best_objective_bound + 1e-6)
    level_counts = tuple(
        sum(solver.value(var) for (_, level), var in x.items() if level == target)
        for target in range(1, max_level + 1)
    )
    values = extract_values(solver, y)
    model.add(expression >= value)
    model.clear_hints()
    for block_id, var in y.items():
        model.add_hint(var, values[block_id])
    report = WeightedFairnessReport(
        value, bound, solver.status_name(status), seconds, level_counts
    )
    return report, values