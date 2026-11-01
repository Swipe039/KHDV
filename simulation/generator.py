import random
from solver.blocks import build_blocks

DEFAULT_DAYS = ("T2", "T3", "T4", "T5", "T6", "T7")

def generate_timetable(num_students, days, sessions_per_day, attend_prob, rng):
    """
    Khởi tạo TKB ngẫu nhiên cho SV
    """
    entries = []
    for i in range(1, num_students + 1):
        student_id = f"{i:04d}"

        for day in days:
            if rng.random() >= attend_prob:
                continue
            count = rng.randint(1, sessions_per_day)
            orders = rng.sample(range(1, sessions_per_day + 1), count)

            for order in sorted(orders):
                entries.append((student_id, day, order))

    return entries

def generate_requests(blocks, wants_prob, rng):
    """
    Khởi tạo lịch muốn dky đi xe máy ngẫu nhiên từ TKB
    """
    return [(block.block_id, rng.random() < wants_prob) for block in blocks]

def generate_dataset(
    num_students,
    days=DEFAULT_DAYS,
    sessions_per_day=4,
    attend_prob=0.6,
    wants_prob=0.8,
    seed=0
):
    rng = random.Random(seed)
    entries = generate_timetable(num_students, days, sessions_per_day, attend_prob, rng)
    blocks = build_blocks(entries)
    requests = generate_requests(blocks, wants_prob, rng)

    return requests