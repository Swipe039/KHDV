PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS student (
    student_code TEXT PRIMARY KEY,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0)
);

CREATE TABLE IF NOT EXISTS session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
    order_in_day INTEGER NOT NULL CHECK (order_in_day >= 1),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    CHECK (start_time < end_time),
    UNIQUE (weekday, order_in_day)
);

CREATE TABLE IF NOT EXISTS timetable_entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL REFERENCES student(student_code) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    UNIQUE (student_code, session_id)
);

CREATE TABLE IF NOT EXISTS session_block (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL REFERENCES student(student_code) ON DELETE CASCADE,
    start_session_id INTEGER NOT NULL REFERENCES session(id) ON DELETE RESTRICT,
    end_session_id INTEGER NOT NULL REFERENCES session(id) ON DELETE RESTRICT,
    length INTEGER NOT NULL CHECK (length >= 1),
    UNIQUE (student_code, start_session_id, end_session_id)
);

CREATE TABLE IF NOT EXISTS parking_request (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_block_id INTEGER NOT NULL UNIQUE REFERENCES session_block(id) ON DELETE CASCADE,
    wants_motorbike INTEGER NOT NULL DEFAULT 0 CHECK (wants_motorbike IN (0, 1)),
    permit_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (permit_status IN ('pending', 'granted', 'denied')),
    reason TEXT NOT NULL DEFAULT '',
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (wants_motorbike = 1 OR permit_status <> 'granted')
);

CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    registration_deadline TEXT NOT NULL,
    random_seed INTEGER NOT NULL DEFAULT 42
);

CREATE INDEX IF NOT EXISTS idx_timetable_session ON timetable_entry(session_id);
CREATE INDEX IF NOT EXISTS idx_block_student ON session_block(student_code);
CREATE INDEX IF NOT EXISTS idx_block_start ON session_block(start_session_id);
CREATE INDEX IF NOT EXISTS idx_block_end ON session_block(end_session_id);
CREATE INDEX IF NOT EXISTS idx_request_status ON parking_request(permit_status);
