import time

from solver.fairness import *
from solver.model import build_model
from solver.stages import length_weights, random_weights, solve_weighted_stage
from solver.types import SolveConfig, SolveResult, StageSummary

def remaining_seconds(config, started):
    return max(config.total_time_limit - (time.perf_counter() - started), 1.0)

def build_occupancy(blocks, values):
    occupancy = {session: 0 for block in blocks for session in block.sessions}
    for block in blocks:
        if values[block.block_id] == 1:
            for session in block.sessions:
                occupancy[session] += 1
    return occupancy

def build_granted_per_student(blocks, values):
    granted = {block.student_id: 0 for block in blocks}
    for block in blocks:
        granted[block.student_id] += values[block.block_id]
    return granted

def summarize_objective(name, report):
    return StageSummary(name, report.status, report.value, report.bound, report.seconds)

def solve(solve_input, config=None):
    if config is None:
        config = SolveConfig()
    started = time.perf_counter()
    blocks = solve_input.blocks
    model, y = build_model(solve_input)

    fairness_report, _ = solve_weighted_fairness(
        model,
        y,
        blocks,
        base = config.base,
        time_limit=remaining_seconds(config, started) * config.fairness_share,
        num_workers=config.num_workers,
    )
    caps = trivial_level_caps(blocks)
    weights = integer_level_weights(len(caps), config.base)
    flags = lexicographic_flags(fairness_report.level_counts, caps, weights)
    fairness_optimal = fairness_report.status == "OPTIMAL"

    length_report, _ = solve_weighted_stage(
        model,
        y,
        length_weights(blocks),
        time_limit=remaining_seconds(config, started) * config.length_share,
        num_workers=config.num_workers,
    )

    random_report, values = solve_weighted_stage(
        model,
        y,
        random_weights(blocks, solve_input.seed, max_weight=config.random_max_weight),
        time_limit=remaining_seconds(config, started),
        num_workers=config.num_workers,
    )

    stages = [
        StageSummary(
            "fairness",
            fairness_report.status,
            fairness_report.value,
            fairness_report.bound,
            fairness_report.seconds,
        ),
        summarize_objective("length", length_report),
        summarize_objective("random", random_report),
    ]

    deviation = deviation_bound(fairness_report.level_counts, weights, flags)
    return SolveResult(
        status={
            block.block_id: "granted" if values[block.block_id] == 1 else "denied"
            for block in blocks
        },
        granted_per_student=build_granted_per_student(blocks, values),
        occupancy=build_occupancy(blocks, values),
        fairness_levels=list(fairness_report.level_counts),
        stages=stages,
        proven_prefix=proven_prefix(fairness_report, flags),
        levels_total=len(caps),
        deviation=deviation if fairness_optimal else None,
        all_optimal=all(stage.status == "OPTIMAL" for stage in stages),
        total_seconds=time.perf_counter() - started,
    )