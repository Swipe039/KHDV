import pytest
from dataclasses import FrozenInstanceError
from solver.types import Block, SolveInput, SolveResult

def test_block_valid():
    block = Block("B1", "1234", ("T2-1", "T2-2"))

    assert block.block_id == "B1"
    assert block.student_id == "1234"
    assert block.sessions == ("T2-1", "T2-2")
    assert block.length == 2

def test_block_empty_sessions_raises():
    with pytest.raises(ValueError):
        Block("B2", "1234", ())


def test_block_immutable():
    block = Block("B3", "1234", ("T2-1",))

    with pytest.raises(FrozenInstanceError):
        block.student_id = "1235"


def test_solve_input_valid():
    block = Block("B4", "1234", ("T2-1",))
    solve_input = SolveInput(blocks=(block,), capacity=10)

    assert solve_input.capacity == 10
    assert solve_input.seed == 0


def test_solve_input_negative_capacity_raises():
    with pytest.raises(ValueError):
        SolveInput(blocks=(), capacity=-5)


def test_solve_input_duplicate_block_id_raises():
    block_a = Block("B5", "1234", ("T2-1",))
    block_b = Block("B5", "1235", ("T2-2",))

    with pytest.raises(ValueError):
        SolveInput(blocks=(block_a, block_b), capacity=5)


def test_solve_result_fairness_levels_default_empty():
    result = SolveResult(status={}, granted_per_student={}, occupancy={})
    
    assert result.fairness_levels == []
