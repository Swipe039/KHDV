
import csv
from collections import Counter
from pathlib import Path

from django.conf import settings


def _read_rows(directory, filename, columns):
    path = directory / filename
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if (
            reader.fieldnames is None
            or len(reader.fieldnames) != len(columns)
            or set(reader.fieldnames) != set(columns)
        ):
            raise ValueError(f"{filename}: cần các cột {', '.join(columns)}")
        rows = []
        for row in reader:
            if None in row or any(row[column] is None for column in columns):
                raise ValueError(f"{filename}, dòng {reader.line_num}: sai số cột")
            rows.append(row)
        return rows


def load_sample_data():
    directory = Path(settings.SAMPLE_DATA_DIR)
    timetable = []
    requests = []
    session_counts = Counter()
    block_counts = Counter()
    registered_counts = Counter()

    for row in _read_rows(directory, "timetable.csv", ("student_id", "day", "order")):
        student_id = row["student_id"].strip()
        day = row["day"].strip()
        try:
            order = int(row["order"])
        except ValueError as exc:
            raise ValueError("timetable.csv: order phải là số nguyên dương") from exc
        if not student_id or not day or order < 1:
            raise ValueError("timetable.csv: cần student_id, day và order dương")
        timetable.append({"student_id": student_id, "day": day, "order": order})
        session_counts[student_id] += 1

    for row in _read_rows(directory, "requests.csv", ("block_id", "registration")):
        block_id = row["block_id"].strip()
        student_id, separator, block = block_id.partition(":")
        if not student_id or not separator or not block:
            raise ValueError("requests.csv: block_id phải bắt đầu bằng student_id:")
        if row["registration"] not in ("0", "1"):
            raise ValueError("requests.csv: registration chỉ nhận 0 hoặc 1")
        registration = row["registration"] == "1"
        requests.append({"block_id": block_id, "registration": registration})
        block_counts[student_id] += 1
        registered_counts[student_id] += registration

    students = [
        {
            "student_id": student_id,
            "session_count": session_counts[student_id],
            "block_count": block_counts[student_id],
            "registered_count": registered_counts[student_id],
        }
        for student_id in sorted(session_counts.keys() | block_counts.keys())
    ]
    return {"timetable": timetable, "requests": requests, "students": students}
