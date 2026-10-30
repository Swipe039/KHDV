from collections import defaultdict
from solver.types import Block


def make_session_id(day, order):
    return f"{day}-{order}"


def split_into_runs(sorted_orders):
    """
    Tách các session_id thành các đoạn liên tiếp trong ngày
    """
    runs = [[sorted_orders[0]]]
    for order in sorted_orders[1:]:
        if order == runs[-1][-1] + 1:
            runs[-1].append(order)
        else:
            runs.append([order])
    return runs


def build_blocks(entries):
    """
    Tạo các blocks đã tách riêng biệt cho theo ngày cho từng SV
    """
    orders_by_student_day = defaultdict(set)
    for student_id, day, order in entries:
        orders_by_student_day[(student_id, day)].add(order)

    blocks = []
    for key in sorted(orders_by_student_day):
        student_id, day = key
        for run in split_into_runs(sorted(orders_by_student_day[key])):
            blocks.append(
                Block(
                    block_id=f"{student_id}:{day}:{run[0]}",
                    student_id=student_id,
                    sessions=tuple(make_session_id(day, order) for order in run),
                )
            )

    return tuple(blocks)