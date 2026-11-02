import csv
from pathlib import Path
from solver.blocks import build_blocks
from solver.types import SolveInput

TIMETABLE_FILE = "timetable.csv"
REQUESTS_FILE = "requests.csv"

def write_dataset(directory, entries, requests):
    """
    Viết ra 2 file csv gồm TKB của SV cùng với lịch những block mà SV dky đi xe máy 
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / TIMETABLE_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["student_id", "day", "order"])
        writer.writerows(entries)

    with open(directory / REQUESTS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["block_id", "wants_motorbike"])
        writer.writerows((block_id, int(wants)) for block_id, wants in requests)

def read_timetable(directory):
    """
    Đọc file thời khóa biểu và tách ra mã SV, ngày trong tuần và ca học trong ngày 
    """
    with open(Path(directory) / TIMETABLE_FILE, newline="", encoding="utf-8") as file:
        return [
            (row["student_id"], row["day"], int(row["order"])) for row in csv.DictReader(file)
        ]


def read_requests(directory):
    """
    Đọc file block dky đi xe máy và tách ra block_id được dky
    """
    with open(Path(directory) / REQUESTS_FILE, newline="", encoding="utf-8") as file:
        return {
            row["block_id"]: row["wants_motorbike"] == "1" for row in csv.DictReader(file) 
        }

def load_solve_input(directory, capacity, seed=0):
    """
    Đọc dữ liệu dataset từ file và tạo các blocks, sau đó chỉ giữ lại những block mà SV chọn sẽ đi xe máy
    """
    entries = read_timetable(directory)
    wants = read_requests(directory)
    blocks = build_blocks(entries)
    selected_blocks = tuple(block for block in blocks if wants.get(block.block_id, False))

    return SolveInput(blocks=selected_blocks, capacity=capacity, seed=seed)