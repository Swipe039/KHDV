import pytest
from dataclasses import FrozenInstanceError
from solver.types import Block

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