from ortools.sat.python import cp_model

def group_block_ids_by_session(blocks):
    """
    Kiểm tra các sessions đang ở trong block nào
    """
    block_ids_by_session = {}
    for block in blocks:
        for session in block.sessions:
            block_ids_by_session.setdefault(session, []).append(block.block_id)
    return block_ids_by_session

def build_model(solve_input):
    """
    Hàm để tạo các ràng buộc cần thiết cho model
    """
    model = cp_model.CpModel()
    y = {
        block.block_id: model.new_bool_var(block.block_id) for block in solve_input.blocks
    }
    block_ids_by_session = group_block_ids_by_session(solve_input.blocks)
    for block_ids in block_ids_by_session.values():
        model.add(sum(y[block_id] for block_id in block_ids) <= solve_input.capacity)

    return model, y

def extract_values(solver, y):
    """
    Hàm lấy kết quả, trả ra 0/1 cho mỗi block_id
    """
    return {block_id: solver.value(var) for block_id, var in y.items()}