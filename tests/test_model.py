import pytest
from ortools.sat.python import cp_model

from solver.model import build_model, extract_values, group_block_ids_by_session
from solver.types import Block, SolveInput
from tests.helpers import build_input, load_cases, expected_granted_count

CASES = load_cases()
CASE_IDS = [case["name"] for case in CASES]

def solve_max_granted(solve_input):
    model, y = build_model(solve_input)
    model.maximize(cp_model.LinearExpr.sum(list(y.values())))
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    assert status == cp_model.OPTIMAL
    return extract_values(solver, y)

@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_capacity_is_guaranteed(case):
    solve_input = build_input(case)
    values = solve_max_granted(solve_input)
    block_ids_by_session = group_block_ids_by_session(solve_input.blocks)

    for block_ids in block_ids_by_session.values():
        occupancy = sum(values[block_id] for block_id in block_ids)

        assert occupancy <= solve_input.capacity

@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_max_granted_count_matches_fixture(case):
    values = solve_max_granted(build_input(case))

    assert sum(values.values()) == expected_granted_count(case["expected"])


def test_capacity_zero_grants_nothing():
    block = Block("B1", "1234", ("T2-1", "T2-2"))
    values = solve_max_granted(SolveInput(blocks=(block,), capacity=0))

    assert values == {"B1": 0}


def test_empty_blocks_build_empty_model():
    _model, y = build_model(SolveInput(blocks=(), capacity=5))

    assert y == {}
    assert group_block_ids_by_session(()) == {}
