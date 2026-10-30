import pytest
from collections import Counter
from tests.helpers import build_input, load_cases

CASES = load_cases()
CASE_IDS = [case["name"] for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_fixture_case_builds_valid_input(case):
    solve_input = build_input(case)

    assert solve_input.capacity == case["capacity"]

    block_ids = {block.block_id for block in solve_input.blocks}
    expected = case["expected"]

    if "granted" in expected:
        granted = set(expected["granted"])
        denied = set(expected["denied"])

        assert granted | denied == block_ids
        assert not granted & denied
    else:
        assert 0 <= expected["granted_count"] <= len(block_ids)


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_fixture_expected_granted_fits_capacity(case):
    expected = case["expected"]
    if "granted" not in expected:
        pytest.skip("no explicit granted list")
    sessions_by_block = {item["block_id"]: item["sessions"] for item in case["blocks"]}
    occupancy = Counter(
        session
        for block_id in expected["granted"]
        for session in sessions_by_block[block_id]
    )

    assert all(count <= case["capacity"] for count in occupancy.values())