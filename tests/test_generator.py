import pytest

from simulation.config import SimulationConfig
from simulation.csv_io import (
    load_solve_input,
    read_requests,
    read_timetable,
    write_dataset,
)
from simulation.generator import generate_dataset
from solver.blocks import build_blocks


def blocks_per_student_day(entries):
    counts = {}
    for block in build_blocks(entries):
        day = block.sessions[0].split("-")[0]
        key = (block.student_id, day)
        counts[key] = counts.get(key, 0) + 1
    return counts


def student_of(block_id):
    return block_id.split(":")[0]


def test_same_seed_same_dataset():
    assert generate_dataset(30, seed=1) == generate_dataset(30, seed=1)


def test_different_seed_different_dataset():
    assert generate_dataset(30, seed=1) != generate_dataset(30, seed=2)


def test_entries_are_within_bounds():
    config = SimulationConfig(
        days=("T2", "T3"),
        sessions_per_day=3,
        days_weights_distribution=(50, 50),
    )
    entries, _ = generate_dataset(50, config=config, seed=3)
    assert entries
    for _, day, order in entries:
        assert day in ("T2", "T3")
        assert 1 <= order <= 3
    assert len(entries) == len(set(entries))


def test_requests_cover_every_block():
    entries, requests = generate_dataset(40, seed=4)
    block_ids = {block.block_id for block in build_blocks(entries)}
    assert {block_id for block_id, _ in requests} == block_ids
    assert len(requests) == len(block_ids)


@pytest.mark.parametrize("index, expected_days", [(0, 1), (5, 6)])
def test_days_weights_fix_number_of_days(index, expected_days):
    weights = [0] * 6
    weights[index] = 100
    config = SimulationConfig(days_weights_distribution=tuple(weights))
    entries, _ = generate_dataset(20, config=config, seed=1)
    days_by_student = {}
    for student_id, day, _ in entries:
        days_by_student.setdefault(student_id, set()).add(day)
    assert len(days_by_student) == 20
    assert all(len(days) == expected_days for days in days_by_student.values())


def test_sparse_rate_zero_gives_one_block_per_day():
    config = SimulationConfig(sparse_rate=0.0)
    entries, _ = generate_dataset(100, config=config, seed=2)
    assert set(blocks_per_student_day(entries).values()) == {1}


def test_sparse_rate_one_gives_two_blocks_per_day():
    config = SimulationConfig(sparse_rate=1.0)
    entries, _ = generate_dataset(100, config=config, seed=2)
    assert set(blocks_per_student_day(entries).values()) == {2}


def test_usage_rate_zero_means_nobody_register():
    config = SimulationConfig(motorbike_usage_rate=0.0)
    _, requests = generate_dataset(50, config=config, seed=3)
    assert requests
    assert not any(registration for _, registration in requests)


def test_register_rate_zero_means_nobody_register():
    config = SimulationConfig(register_rate=0.0)
    _, requests = generate_dataset(50, config=config, seed=3)
    assert requests
    assert not any(registration for _, registration in requests)


def test_full_rates_mean_everybody_register():
    config = SimulationConfig(motorbike_usage_rate=1.0, register_rate=1.0)
    _, requests = generate_dataset(50, config=config, seed=3)
    assert requests
    assert all(registration for _, registration in requests)


def test_motorbike_usage_is_decided_per_student():
    config = SimulationConfig(register_rate=1.0)
    _, requests = generate_dataset(200, config=config, seed=4)
    registration_by_student = {}
    for block_id, registration in requests:
        registration_by_student.setdefault(student_of(block_id), set()).add(registration)
    assert all(len(values) == 1 for values in registration_by_student.values())
    outcomes = {next(iter(values)) for values in registration_by_student.values()}
    assert outcomes == {True, False}


def test_default_distributions_match_config():
    entries, requests = generate_dataset(2000, seed=5)
    student_days = blocks_per_student_day(entries)
    sparse_share = sum(1 for count in student_days.values() if count == 2) / len(student_days)
    assert abs(sparse_share - 0.15) < 0.02
    assert abs(len(student_days) / 2000 - 4.03) < 0.1
    wanting = {student_of(block_id) for block_id, registration in requests if registration}
    assert abs(len(wanting) / 2000 - 0.8) < 0.03


def test_csv_round_trip(tmp_path):
    entries, requests = generate_dataset(25, seed=5)
    write_dataset(tmp_path, entries, requests)
    assert read_timetable(tmp_path) == entries
    assert read_requests(tmp_path) == dict(requests)


def test_load_solve_input_keeps_only_wanted_blocks(tmp_path):
    config = SimulationConfig(motorbike_usage_rate=0.5)
    entries, requests = generate_dataset(25, config=config, seed=6)
    write_dataset(tmp_path, entries, requests)
    solve_input = load_solve_input(tmp_path, capacity=7, seed=9)
    wanted_ids = {block_id for block_id, registration in requests if registration}
    assert {block.block_id for block in solve_input.blocks} == wanted_ids
    assert solve_input.capacity == 7
    assert solve_input.seed == 9


def test_load_solve_input_rejects_mismatched_requests(tmp_path):
    entries, requests = generate_dataset(25, seed=7)
    stale_requests = [(f"old:{block_id}", registration) for block_id, registration in requests]
    write_dataset(tmp_path, entries, stale_requests)
    with pytest.raises(ValueError):
        load_solve_input(tmp_path, capacity=5)

def test_student_id_is_eight_digits():
    entries, _ = generate_dataset(12, seed=8)
    student_ids = {student_id for student_id, _, _ in entries}
    assert all(len(student_id) == 8 and student_id.isdigit() for student_id in student_ids)