"""Kiểm tra SQLite độc lập: python test_connection.py [path-to-db]."""
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).with_name('parking.sqlite3')
DB_PATH = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_DB
EXPECTED = {'student', 'session', 'timetable_entry', 'session_block', 'parking_request', 'config'}


def main():
    if not DB_PATH.is_file():
        print(f'FAIL: Không tìm thấy cơ sở dữ liệu: {DB_PATH}')
        return 1
    try:
        with sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True) as conn:
            conn.execute('PRAGMA foreign_keys = ON')
            result = conn.execute('SELECT sqlite_version()').fetchone()[0]
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            missing = EXPECTED - names
            fk_errors = conn.execute('PRAGMA foreign_key_check').fetchall()
            integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
            print('SQLite version:', result)
            print('DB:', DB_PATH)
            print('Tables:', ', '.join(sorted(names & EXPECTED)))
            print('Integrity:', integrity)
            print('Foreign key errors:', len(fk_errors))
            if missing or fk_errors or integrity != 'ok':
                print('FAIL: Missing:', sorted(missing))
                return 1
            print('PASS: Kết nối và cấu trúc database hợp lệ')
        return 0
    except sqlite3.Error as exc:
        print('FAIL:', exc)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
