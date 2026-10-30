import json
from pathlib import Path
from solver.types import Block, SolveInput

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "small_cases.json"


def load_cases():
    with open(FIXTURE_PATH, encoding="utf-8") as file:
        return json.load(file)["cases"]

def build_input(case, seed=0):
    blocks = tuple(
        Block(item["block_id"], item["student_id"], tuple(item["sessions"])) for item in case["blocks"]
    )

    return SolveInput(blocks=blocks, capacity=case["capacity"], seed=seed)