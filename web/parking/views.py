from django.shortcuts import render

from .sample_data import load_sample_data


def sample_data_view(request):
    """Hiển thị thời khóa biểu và đăng ký từ hai file CSV mẫu."""
    data = load_sample_data()
    tables = [
        {
            "name": "timetable",
            "title": "Thời khóa biểu",
            "source": "timetable.csv",
            "columns": ["student_id", "day", "order"],
            "rows": [
                (row["student_id"], row["day"], row["order"])
                for row in data["timetable"]
            ],
            "count": len(data["timetable"]),
        },
        {
            "name": "requests",
            "title": "Đăng ký đi xe máy",
            "source": "requests.csv",
            "columns": ["block_id", "registration"],
            "rows": [
                (row["block_id"], int(row["registration"]))
                for row in data["requests"]
            ],
            "count": len(data["requests"]),
        },
    ]
    return render(request, "parking/samples.html", {
        "tables": tables,
        "student_count": len(data["students"]),
        "registered_count": sum(row["registration"] for row in data["requests"]),
    })


def student_list(request):
    return render(request, "parking/students.html", {
        "students": load_sample_data()["students"],
    })
