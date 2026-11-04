import random
from itertools import combinations, pairwise

from simulation.config import SimulatorConfig
from solver.blocks import build_blocks

DEFAULT_DAYS = ("T2", "T3", "T4", "T5", "T6", "T7")

def is_continguous(orders):
    return all(later - earlier == 1 for earlier, later in pairwise(orders))

def sparse_patterns(sessions_per_day):
    """
    Tạo các nhóm gồm tổ hợp các ca học đứt quãng
    """
    orders = range(1, sessions_per_day + 1)
    return [
        subset
        for size in range(2, sessions_per_day)
        for subset in combinations(orders, size)
        if not is_continguous(subset)
    ]

def continguous_orders(sessions_per_day, rng):
    """
    Tạo nhóm các ca học liền nhau
    """
    num_sessions = rng.randint(1, sessions_per_day) 
    start = rng.randint(1, sessions_per_day - num_sessions + 1)
    return tuple(range(start, start + num_sessions))

def day_orders(config, patterns, rng):
    if rng.random() < config.sparse_rate:
        return rng.choice(patterns)

    return continguous_orders(config.sessions_per_day, rng)
    
def generate_timetable(num_students, config, rng):
    """
    Khởi tạo TKB ngẫu nhiên cho SV
    """
    patterns = sparse_patterns(config.sessions_per_day)
    day_counts = range(1, len(config.days) + 1)
    entries = []
    for i in range(1, num_students + 1):
        student_id = f"{i:08d}"
        num_days = rng.choices(day_counts, weights=config.days_weight_distribution)[0]
        chosen_days = sorted(rng.sample(config.days, num_days), key = config.day.index)

        for day in chosen_days:
            for order in day_orders(config, patterns, rng):
                entries.append((student_id, day, order))

    return entries

def generate_requests(blocks, config, rng):
    """
    Khởi tạo lịch muốn dky đi xe máy ngẫu nhiên từ TKB
    """
    use_motorbike = {}
    requests = []
    for block in blocks:
        if block.student_id not in use_motorbike:
            use_motorbike[block.student_id] = rng.random() < config.motorbike_usage_rate
        wants = use_motorbike[block.student_id] and rng.random() < config.register_rate
        requests.append((block.block_id, wants))
    return requests

def generate_dataset(num_students, config=None, seed=0):
    if config is None:
        config = SimulatorConfig()
    rng = random.Random(seed)
    entries = generate_timetable(num_students, config, rng)
    blocks = build_blocks(entries)
    requests = generate_requests(blocks, config, rng)

    return entries, requests