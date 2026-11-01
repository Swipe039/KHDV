from ortools.sat.python import cp_model


def group_block_ids_by_session(blocks):
    block_ids_by_session = {}
    for block in blocks:
        for session in block.sessions:
            block_ids_by_session.setdefault(session, []).append(block.block_id)
    return block_ids_by_session


def build_model(solve_input):
    """
    """
    model = cp_model.CpModel()
    y = {
        block.block_id: model.new_bool_var(block.block_id) for block in solve_input.blocks
    }
    block_ids_by_session = group_block_ids_by_session(solve_input.blocks)
    for block_ids in block_ids_by_session.values():
        model.add(sum(y[block_id] for block_id in block_ids) <= solve_input.capacity)


def extract_values(solver, y):
    """
    """
    return {block_id: solver.value(var) for block_id, var in y.items()}