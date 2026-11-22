import pytest

from solver.model import build_model
from solver.stages import (
    length_weights,
    random_weights,
    solve_fairness_stage,
    solve_weighted_stage,
)
from solver.types import Block, SolveInput
from tests.helpers import build_input, load_cases

CASES = load_cases()
CASE_IDS = [case["name"] for case in CASES]
CASE_BY_NAME = {case["name"]: case for case in CASES}


def run_pipeline(solve_input):
    model, y = build_model(solve_input)
    solve_fairness_stage(model, y, solve_input.blocks)
    solve_weighted_stage(model, y, length_weights(solve_input.blocks))
    weights = random_weights(solve_input.blocks, solve_input.seed)
    _, values = solve_weighted_stage(model, y, weights)
    return values


def granted_ids(values):
    return {block_id for block_id, value in values.items() if value == 1}


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_pipeline_matches_fixture(case):
    granted = granted_ids(run_pipeline(build_input(case)))
    expected = case["expected"]
    if "granted" in expected:
        assert granted == set(expected["granted"])
    else:
        assert len(granted) == expected["granted_count"]


def test_length_stage_prefers_longer_block_of_same_student():
    blocks = (
        Block("X1", "X", ("S1", "S2")),
        Block("X2", "X", ("S2",)),
    )
    values = run_pipeline(SolveInput(blocks=blocks, capacity=1))
    assert values == {"X1": 1, "X2": 0}


def test_random_stage_is_reproducible():
    case = CASE_BY_NAME["random_tie_same_length"]
    first = run_pipeline(build_input(case, seed=7))
    second = run_pipeline(build_input(case, seed=7))
    assert first == second


def test_random_stage_depends_on_seed():
    case = CASE_BY_NAME["random_tie_same_length"]
    winners = set()
    for seed in range(20):
        winners |= granted_ids(run_pipeline(build_input(case, seed=seed)))
    assert winners == {"P1", "Q1"}


def test_random_weights_are_reproducible_and_order_independent():
    blocks = (
        Block("B", "S2", ("S1",)),
        Block("A", "S1", ("S1",)),
    )
    first = random_weights(blocks, seed=3)
    second = random_weights(tuple(reversed(blocks)), seed=3)
    assert first == second
    assert set(first) == {"A", "B"}
    assert all(1 <= weight <= 1000 for weight in first.values())


def test_weighted_stage_with_no_weights_returns_zero():
    model, y = build_model(SolveInput(blocks=(), capacity=3))
    report, values = solve_weighted_stage(model, y, {})
    assert report.value == 0
    assert values == {}


def test_locked_value_survives_later_stage():
    blocks = (
        Block("A", "S1", ("T1", "T2")),
        Block("B", "S2", ("T1",)),
    )
    model, y = build_model(SolveInput(blocks=blocks, capacity=1))
    report, _ = solve_weighted_stage(model, y, length_weights(blocks))
    assert report.value == 2
    _, values = solve_weighted_stage(model, y, {"A": 1, "B": 100})
    assert values == {"A": 1, "B": 0}