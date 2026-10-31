# SQLite – Hệ thống xếp lịch xe máy sinh viên

Theo PlanSystem.docx, bảng cốt lõi gồm: student, session, timetable_entry, session_block, parking_request, config.

## Kiểm tra kết nối ngay

```bash
python3 test_connection.py
```

`parking.sqlite3` là CSDL SQLite được khởi tạo theo `schema.sql` (chưa có dữ liệu sinh viên).

## Tạo mới với SQLite độc lập

```bash
python3 -c "import sqlite3; c=sqlite3.connect('parking.sqlite3'); c.executescript(open('schema.sql').read()); c.close()"
python3 test_connection.py
```

## Dùng với Django (khuyến nghị cho ứng dụng web)

1. Tạo dự án Django và một app, ví dụ `parking`.
2. Đưa nội dung `models.py` vào app `parking/models.py` và khai báo `parking` trong `INSTALLED_APPS`.
3. Trong `settings.py`, cấu hình `DATABASES['default']` là SQLite, tên file `BASE_DIR / 'db.sqlite3'`.
4. Chạy `python manage.py makemigrations parking` và `python manage.py migrate` để **Django tự tạo database** (không nạp `schema.sql` vào DB này).
5. Chạy `python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"` để kiểm tra.
6. Tạo tài khoản đăng nhập bằng Django auth; đặt `User.username` bằng `Student.student_code`, hoặc mở rộng bằng quan hệ OneToOneField nếu cần liên kết chặt.

**Lưu ý:** `session_block` phải được tự sinh từ `timetable_entry` theo thứ tự ca trong ngày. Logic kiểm tra block hợp lệ, deadline, tính công bằng và không vượt capacity nằm ở tầng ứng dụng/bộ giải, không chỉ dựa vào các ràng buộc SQL. File `schema.sql` cung cấp DB độc lập để kiểm tra; migrations Django là nguồn quản lý schema khi phát triển web.

## Dữ liệu giả lập đi kèm

File `parking.sqlite3` **đã có dữ liệu** (không phải database rỗng):
- 150 sinh viên có mã giả lập `SV0001` đến `SV0150`.
- 30 ca học, từ thứ 2 đến thứ 7, 5 ca/ngày.
- 1107 mục thời khóa biểu và 662 block liên tiếp sinh ra từ thời khóa biểu.
- 662 phiếu đăng ký: 442 granted, 70 denied, 150 pending (không muốn đi xe máy).
- `config.capacity = 28`, `random_seed = 42` và hạn đăng ký mẫu.

Tất cả thông tin sinh viên đều là dữ liệu **giả**, không phải danh sách sinh viên thật.
Trạng thái granted/denied chỉ nhằm thử giao diện và báo cáo, được sinh theo
heuristic tham lam xét công bằng; **không phải nghiệm leximin bằng ILP**.

Để tái sinh dữ liệu theo seed cố định từ file `schema.sql`:

```bash
python3 seed_demo.py
```

**Chú ý:** Lệnh này **xóa rồi tạo lại** `parking.sqlite3`, không dùng trên database chứa dữ liệu thật.

Kiểm tra:

```bash
python3 test_connection.py
```

Các file CSV UTF-8-BOM xuất từ database: `students.csv`, `sessions.csv`,
`timetable_entries.csv`, `session_blocks.csv`, `parking_requests.csv`, `config.csv`,
`report_session_occupancy.csv`.

Các bảng được tạo bằng SQL thuần. Nếu tích hợp Django, nên chọn một cách quản lý
schema nhất quán (migrations do Django quản lý hoặc SQL thủ công), tránh tạo trùng bảng.
