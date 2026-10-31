"""Tạo dữ liệu MẪU giả lập, tái lập được cho đồ án (không phải dữ liệu sinh viên thật)."""
import csv
import random
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'parking.sqlite3'
CAPACITY = 28
SEED = 42
N_STUDENTS = 150


def create_demo():
    rng = random.Random(SEED)
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.executescript((BASE / 'schema.sql').read_text(encoding='utf-8'))
    conn.execute('INSERT INTO config (id, capacity, registration_deadline, random_seed) VALUES (1, ?, ?, ?)',
                 (CAPACITY, '2026-11-15 23:59:59', SEED))
    # 6 ngày, 5 ca/ngày; liền nhau xác định bằng order_in_day.
    times = [('07:00','08:30'), ('08:35','10:05'), ('10:10','11:40'),
             ('12:45','14:15'), ('14:20','15:50')]
    session_lookup = {}
    for day in range(1, 7):
        for order, (start, end) in enumerate(times, 1):
            cur = conn.execute('INSERT INTO session (weekday, order_in_day, start_time, end_time) VALUES (?,?,?,?)',
                               (day, order, start, end))
            session_lookup[(day, order)] = cur.lastrowid

    families = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Phan','Vũ','Võ','Đặng','Bùi','Đỗ','Ngô']
    middle = ['Văn','Thị','Minh','Quang','Hoài','Đức','Gia','Khánh','Thanh','Hữu']
    given = ['An','Bình','Châu','Dũng','Giang','Hà','Hải','Hân','Huy','Khôi','Lan','Linh','Long','Mai','Nam','Ngọc','Phong','Phúc','Quân','Trang','Tú','Vy']
    blocks = []
    for n in range(1, N_STUDENTS + 1):
        code = f'SV{n:04d}'
        name = f'{rng.choice(families)} {rng.choice(middle)} {rng.choice(given)}'
        conn.execute('INSERT INTO student (student_code, full_name) VALUES (?,?)', (code, name))
        study_days = rng.sample(range(1, 7), k=rng.randint(2, 4))
        for day in study_days:
            # Mỗi ngày 1-2 block, chỉ sinh từ các ca thực sự học.
            orders = sorted(rng.sample(range(1, 6), k=rng.randint(1, 4)))
            for order in orders:
                conn.execute('INSERT INTO timetable_entry (student_code, session_id) VALUES (?,?)',
                             (code, session_lookup[(day, order)]))
            group = [orders[0]]
            groups = []
            for order in orders[1:]:
                if order == group[-1] + 1:
                    group.append(order)
                else:
                    groups.append(group)
                    group = [order]
            groups.append(group)
            for g in groups:
                cur = conn.execute('''INSERT INTO session_block
                   (student_code, start_session_id, end_session_id, length)
                   VALUES (?,?,?,?)''',
                   (code, session_lookup[(day, g[0])], session_lookup[(day, g[-1])], len(g)))
                block_id = cur.lastrowid
                wants = int(rng.random() < 0.78)
                at = datetime(2026, 10, 10, 8) + timedelta(minutes=rng.randint(0, 18000))
                conn.execute('''INSERT INTO parking_request
                   (session_block_id, wants_motorbike, permit_status, reason, submitted_at)
                   VALUES (?,?,?,?,?)''',
                   (block_id, wants, 'pending', '', at.strftime('%Y-%m-%d %H:%M:%S')))
                blocks.append((block_id, code, tuple(session_lookup[(day, o)] for o in g), wants))

    # Trạng thái minh họa bằng heuristic công bằng (KHÔNG phải nghiệm leximin/ILP).
    counts = defaultdict(int)
    occupied = defaultdict(int)
    candidates = [b for b in blocks if b[3] == 1]
    # Mỗi vòng chọn nhiều nhất 1 block / sinh viên đang có số block được duyệt thấp nhất.
    unprocessed = list(candidates)
    while unprocessed:
        minimum = min(counts[b[1]] for b in unprocessed)
        layer = [b for b in unprocessed if counts[b[1]] == minimum]
        rng.shuffle(layer)
        layer.sort(key=lambda b: -len(b[2]))
        for block in layer:
            bid, student, ids, _ = block
            status = 'granted' if all(occupied[s] < CAPACITY for s in ids) else 'denied'
            reason = '' if status == 'granted' else 'Đã đủ chỗ tại ít nhất một ca trong block'
            conn.execute('UPDATE parking_request SET permit_status = ?, reason = ? WHERE session_block_id = ?',
                         (status, reason, bid))
            if status == 'granted':
                counts[student] += 1
                for sid in ids:
                    occupied[sid] += 1
        processed = {b[0] for b in layer}
        unprocessed = [b for b in unprocessed if b[0] not in processed]
    # Không đăng ký thì để pending, không chuyển thành granted.
    conn.commit()
    assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert max(occupied.values(), default=0) <= CAPACITY

    exports = {
        'students.csv': 'SELECT * FROM student ORDER BY student_code',
        'sessions.csv': 'SELECT * FROM session ORDER BY weekday, order_in_day',
        'timetable_entries.csv': 'SELECT * FROM timetable_entry ORDER BY student_code, session_id',
        'session_blocks.csv': 'SELECT * FROM session_block ORDER BY student_code, id',
        'parking_requests.csv': 'SELECT * FROM parking_request ORDER BY id',
        'config.csv': 'SELECT * FROM config',
        'report_session_occupancy.csv': '''SELECT s.id, s.weekday, s.order_in_day, COUNT(pr.id) AS granted_count,
          (SELECT capacity FROM config WHERE id=1) AS capacity
          FROM session s LEFT JOIN session_block b ON
             s.weekday = (SELECT weekday FROM session WHERE id=b.start_session_id)
             AND s.order_in_day BETWEEN
             (SELECT order_in_day FROM session WHERE id=b.start_session_id) AND
             (SELECT order_in_day FROM session WHERE id=b.end_session_id)
          LEFT JOIN parking_request pr ON pr.session_block_id=b.id AND pr.permit_status='granted'
          GROUP BY s.id ORDER BY s.weekday, s.order_in_day''',
    }
    for filename, sql in exports.items():
        cur = conn.execute(sql)
        with (BASE / filename).open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([x[0] for x in cur.description])
            writer.writerows(cur.fetchall())
    print('Generated DB:', DB)
    for table in ['student', 'session', 'timetable_entry', 'session_block', 'parking_request', 'config']:
        print(f'{table}:', conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])
    print('Status:', conn.execute('SELECT permit_status, COUNT(*) FROM parking_request GROUP BY permit_status').fetchall())
    print('Maximum occupancy:', max(occupied.values(), default=0), '/', CAPACITY)
    conn.close()


if __name__ == '__main__':
    create_demo()
