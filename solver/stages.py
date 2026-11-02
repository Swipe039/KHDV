from ortools.sat.python import cp_model

def group_block_ids_by_student(blocks):
    """
    Gom các block_ids theo mã SV
    """
    block_ids_by_student = {}

    for block in blocks:
        block_ids_by_student.setdefault(block.student_id, []).append(block.block_id)

    return block_ids_by_student

def solve_fairness_stage(model, y, blocks):
    """
    Tìm số SV nhiều nhất có thể mà đã dc granted ít nhất một lượng block ở từng mức
    """
    block_ids_by_student = group_block_ids_by_student(blocks)
    granted_count = {
        student_id: sum(y[block_id] for block_id in block_ids)
        for student_id, block_ids in block_ids_by_student.items()
    }
    max_requested = max((len(ids) for ids in block_ids_by_student.values()), default=0)

    level_counts = []
    for level in range(1, max_requested + 1):
        reached = {}
        for student_id, blocks_ids in block_ids_by_student.items():
            if len(blocks_ids) < level:
                continue

            reached[student_id] = model.new_bool_var(f"reached_{student_id}_{level}")
            model.add(granted_count[student_id] >= level * reached[student_id])

        model.maximize(cp_model.LinearExpr.sum(list(reached.values())))
        solver = cp_model.CpSolver()
        status = solver.solve(model)
        if status != cp_model.OPTIMAL:
            raise RuntimeError(f"fairness level {level} not solved to optimality")

        count = round(solver.objective_value)
        if count == 0:
            break
        model.add(cp_model.LinearExpr.sum(list(reached.values())) >= count)
        level_counts.append(count)
    return level_counts