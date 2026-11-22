import pytest
from ortools.sat.python import cp_model

from solver.model import build_model, extract_values
from solver.stages import extract_level_counts, solve_fairness_stage
from solver.types import Block, SolveInput
from tests.helpers import build_input, expected_granted_count, load_cases

CASES = load_cases()
CASE_IDS = [case["name"] for case in CASES]

def run_fairness(solve_input):
    model, y = build_model(solve_input)
    reports = solve_fairness_stage(model, y, solve_input.blocks)
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    assert status == cp_model.OPTIMAL
    return extract_level_counts(reports), extract_values(solver, y)

def granted_per_student(blocks, values):
    totals = {}
    for block in blocks:
        totals[block.student_id] = totals.get(block.student_id, 0) + values[block.block_id]

    return totals

@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_level_one_matches_fixture(case):
    level_counts, _ = run_fairness(build_input(case))
    first_level = level_counts[0] if level_counts else 0

    assert first_level == expected_granted_count(case["expected"])

def test_fairness_prefers_more_students_over_longer_block():
    blocks = (
        Block("A1", "A", ("S1", "S2", "S3")),
        Block("B1", "B", ("S1", "S2")),
        Block("C1", "C", ("S3", "S4")),
    )
    level_counts, values = run_fairness(SolveInput(blocks=blocks, capacity=1))

    assert level_counts == [2]
    assert values == {"A1": 0, "B1": 1, "C1": 1}

def test_earlier_level_is_locked_before_later_level():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
        Block("Y1", "Y", ("S1",)),
        Block("Z1", "Z", ("S2",)),
    )
    level_counts, _ = run_fairness(SolveInput(blocks=blocks, capacity=1))

    assert level_counts == [2]

def test_single_student_reaches_two_levels():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
    )
    level_counts, values = run_fairness(SolveInput(blocks=blocks, capacity=1))

    assert level_counts == [1, 1]
    assert values == {"X1": 1, "X2": 1}

def test_two_students_are_equalized():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
        Block("Y1", "Y", ("S1",)),
        Block("Y2", "Y", ("S2",)),
    )
    level_counts, values = run_fairness(SolveInput(blocks=blocks, capacity=1))

    assert level_counts == [2]
    assert granted_per_student(blocks, values) == {"X": 1, "Y": 1}

def test_no_blocks_gives_no_levels():
    model, y = build_model(SolveInput(blocks=(), capacity=3))

    assert solve_fairness_stage(model, y, ()) == []

def test_zero_count_level_is_reported():
    block = Block("A1", "A", ("S1",))
    solve_input = SolveInput(blocks=(block,), capacity=0)
    model, y = build_model(solve_input)
    reports = solve_fairness_stage(model, y, solve_input.blocks)
    assert len(reports) == 1
    assert reports[0].count == 0
    assert extract_level_counts(reports) == []


def test_reports_are_consistent():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
        Block("Y1", "Y", ("S1",)),
        Block("Y2", "Y", ("S2",)),
    )
    model, y = build_model(SolveInput(blocks=blocks, capacity=1))
    reports = solve_fairness_stage(model, y, blocks)
    assert [report.level for report in reports] == [1, 2]
    assert [report.count for report in reports] == [2, 0]
    assert all(report.status == "OPTIMAL" for report in reports)
    assert all(report.bound >= report.count for report in reports)
    assert all(report.seconds >= 0 for report in reports)


def test_on_level_receives_every_report():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
    )
    model, y = build_model(SolveInput(blocks=blocks, capacity=1))
    seen = []
    reports = solve_fairness_stage(model, y, blocks, on_level=seen.append)
    assert seen == reports