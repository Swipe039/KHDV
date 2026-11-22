from solver.blocks import build_blocks


def block_sessions(entries):
    return sorted(block.sessions for block in build_blocks(entries))


def test_consecutive_sessions_from_one_block():
    entries = [("1234", "T2", 1), ("1234", "T2", 2), ("1234", "T2", 3)]

    assert block_sessions(entries) == [("T2-1", "T2-2", "T2-3")]

def test_non_consecutive_sessions_from_one_block():
    entries = [("1234", "T2", 1), ("1234", "T2", 2), ("1234", "T2", 4)]

    assert block_sessions(entries) == [("T2-1", "T2-2",), ("T2-4",)]


def test_unsorted_entries_are_handled():
    entries = [("1234", "T2", 3), ("1234", "T2", 1), ("1234", "T2", 2)]
    
    assert block_sessions(entries) == [("T2-1", "T2-2", "T2-3")]


def test_block_does_not_cross_days():
    entries = [("1234", "T2", 4), ("1234", "T3", 1)]
    assert block_sessions(entries) == [("T2-4",), ("T3-1",)]


def test_students_are_independent():
    entries = [("1234", "T2", 1), ("1235", "T2", 2)]
    blocks = build_blocks(entries)

    assert len(blocks) == 2 # Tách thành 2 block do khác student_id
    assert {block.student_id for block in blocks} == {"1234", "1235"}


def test_duplicate_entries_are_ignored():
    entries = [("1234", "T2", 1), ("1234", "T2", 1)]
    assert block_sessions(entries) == [("T2-1",)]

def test_empty_entries_give_no_blocks():
    assert build_blocks([]) == ()

def test_block_ids_are_unique():
    entries = [
        ("1234", "T2", 1),
        ("1234", "T2", 3),
        ("1234", "T3", 1),
        ("1235", "T2", 1),
    ]
    blocks = build_blocks(entries)
    block_ids = [block.block_id for block in blocks]

    assert len(block_ids) == len(set(block_ids)) == 4

def test_block_id_contains_start_and_end():
    entries = [
        ("0001", "T2", 1),
        ("0001", "T2", 2),
        ("0001", "T2", 3),
        ("0001", "T2", 5),
    ]
    block_ids = sorted(block.block_id for block in build_blocks(entries))
    
    assert block_ids == ["0001:T2:1-3", "0001:T2:5-5"]
