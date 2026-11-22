import pytest

from solver.solve import solve
from solver.types import Block, SolveConfig, SolveInput
from tests.helpers import build_input, expected_granted_count, load_cases

CASES = load_cases()
CASE_IDS = [case["name"] for case in CASES]


def granted_ids(result):
    return {block_id for block_id, state in result.status.items() if state == "granted"}


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_solve_matches_fixture(case):
    result = solve(build_input(case))
    expected = case["expected"]
    if "granted" in expected:
        assert granted_ids(result) == set(expected["granted"])
    else:
        assert len(granted_ids(result)) == expected_granted_count(expected)


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_occupancy_never_exceeds_capacity(case):
    result = solve(build_input(case))
    assert all(count <= case["capacity"] for count in result.occupancy.values())


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_every_block_has_status(case):
    solve_input = build_input(case)
    result = solve(solve_input)
    assert set(result.status) == {block.block_id for block in solve_input.blocks}
    assert set(result.status.values()) <= {"granted", "denied"}


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_granted_per_student_matches_status(case):
    solve_input = build_input(case)
    result = solve(solve_input)
    for student_id, total in result.granted_per_student.items():
        expected = sum(
            1
            for block in solve_input.blocks
            if block.student_id == student_id and result.status[block.block_id] == "granted"
        )
        assert total == expected


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_small_cases_are_fully_certified(case):
    result = solve(build_input(case))
    assert result.all_optimal
    assert result.proven_prefix == result.levels_total
    assert result.deviation is None
    assert [stage.name for stage in result.stages] == ["fairness", "length", "random"]


def test_same_seed_same_result():
    case = next(item for item in CASES if item["name"] == "random_tie_same_length")
    first = solve(build_input(case, seed=5))
    second = solve(build_input(case, seed=5))
    assert first.status == second.status


def test_fairness_levels_are_reported():
    blocks = (
        Block("X1", "X", ("S1",)),
        Block("X2", "X", ("S2",)),
        Block("Y1", "Y", ("S1",)),
        Block("Y2", "Y", ("S2",)),
    )
    result = solve(SolveInput(blocks=blocks, capacity=1))
    assert result.fairness_levels == [2, 0]
    assert result.granted_per_student == {"X": 1, "Y": 1}


def test_empty_input():
    result = solve(SolveInput(blocks=(), capacity=3))
    assert result.status == {}
    assert result.occupancy == {}
    assert result.all_optimal
    assert result.levels_total == 0


def test_config_rejects_bad_values():
    with pytest.raises(ValueError):
        SolveConfig(total_time_limit=0)
    with pytest.raises(ValueError):
        SolveConfig(fairness_share=0)
    with pytest.raises(ValueError):
        SolveConfig(fairness_share=1.5)
    with pytest.raises(ValueError):
        SolveConfig(base=1)
    with pytest.raises(ValueError):
        SolveConfig(num_workers=-1)