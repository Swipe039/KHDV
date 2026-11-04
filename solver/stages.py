import math
import random
import time
from dataclasses import dataclass

from ortools.sat.python import cp_model

from solver.model import extract_values

@dataclass(frozen=True)
class LevelReport:
    level: int
    count: int
    bound: int
    status: str
    seconds: float

def group_block_ids_by_student(blocks):
    """
    Gom các block_ids theo mã SV
    """
    block_ids_by_student = {}
    for block in blocks:
        block_ids_by_student.setdefault(block.student_id, []).append(block.block_id)

    return block_ids_by_student

def extract_level_counts(reports):
    return [reports.count for report in reports if report.count > 0]

def solve_fairness_stage(model, y, blocks, time_limit_per_level=60.0, on_level=None):
    """
    Tìm số SV nhiều nhất có thể mà đã dc granted ít nhất một lượng block ở từng mức
    """
    block_ids_by_student = group_block_ids_by_student(blocks)
    granted_count = {
        student_id: sum(y[block_id] for block_id in block_ids)
        for student_id, block_ids in block_ids_by_student.items()
    }
    max_requested = max((len(ids) for ids in block_ids_by_student.values()), default=0)

    reports = []
    kept_vars = list(y.values())
    previous_solver = None
    for level in range(1, max_requested + 1):
        reached = {}
        for student_id, block_ids in block_ids_by_student.items():
            if len(block_ids) < level:
                continue
            reached[student_id] = model.new_bool_var(f"reached_{student_id}_{level}")
            model.add(granted_count[student_id] >= level * reached[student_id])

        if previous_solver is not None:
            model.clear_hints()
            for var in kept_vars:
                model.add_hint(var, previous_solver.value(var))
            for student_id, var in reached.items():
                previous_total = sum(
                    previous_solver.value(y[block_id])
                    for block_id in block_ids_by_student[student_id]
                )
                model.add_hint(var, int(previous_total >= level))

        model.maximize(cp_model.LinearExpr.sum(list(reached.values())))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_per_level
        started = time.perf_counter()
        status = solver.solve(model)
        seconds = time.perf_counter() - started
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError(f"fairness level {level} found no solution")

        count = round(solver.objective_value)
        bound = math.floor(solver.best_objective_bound + 1e-6)
        report = LevelReport(level, count, bound, solver.status_name(status), seconds)
        reports.append(report)
        if on_level is not None:
            on_level(report)
        if count == 0:
            break
        model.add(cp_model.LinearExpr.sum(list(reached.values())) >= count)
        kept_vars.extend(reached.values())
        previous_solver = solver

    if previous_solver is not None:
        model.clear_hints()
        for var in kept_vars:
            model.add_hint(var, previous_solver.value(var))
    return reports

@dataclass(frozen=True)
class ObjectiveReport:
    value: int
    bound: int
    status: str
    seconds: float


def length_weights(blocks):
    return {block.block_id: block.length for block in blocks}


def random_weights(blocks, seed, max_weight=1000):
    rng = random.Random(seed)
    return {
        block.block_id: rng.randint(1, max_weight)
        for block in sorted(blocks, key=lambda block: block.block_id)
    }


def solve_weighted_stage(model, y, weights, time_limit=60.0):
    if not weights:
        return ObjectiveReport(0, 0, "OPTIMAL", 0.0), {}

    block_ids = sorted(weights)
    expression = cp_model.LinearExpr.weighted_sum(
        [y[block_id] for block_id in block_ids],
        [weights[block_id] for block_id in block_ids],
    )
    model.maximize(expression)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    started = time.perf_counter()
    status = solver.solve(model)
    seconds = time.perf_counter() - started
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("weighted stage found no solution")

    value = round(solver.objective_value)
    bound = math.floor(solver.best_objective_bound + 1e-6)
    values = extract_values(solver, y)
    model.add(expression >= value)
    model.clear_hints()
    for block_id, var in y.items():
        model.add_hint(var, values[block_id])
    return ObjectiveReport(value, bound, solver.status_name(status), seconds), values