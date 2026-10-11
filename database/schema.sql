-- CampusInsight Database Schema
-- Robust, relational schema with foreign key constraints, indexes, and validation checks.

PRAGMA foreign_keys = ON;

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'admin')),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 2. STUDENTS
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    usn TEXT UNIQUE NOT NULL COLLATE NOCASE,
    branch TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
    section TEXT NOT NULL,
    batch_year INTEGER NOT NULL DEFAULT 2022
);

-- 3. SUBJECTS
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL COLLATE NOCASE,
    name TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
    branch TEXT NOT NULL,
    max_internal REAL NOT NULL DEFAULT 40.0 CHECK(max_internal > 0),
    max_external REAL NOT NULL DEFAULT 60.0 CHECK(max_external > 0),
    min_internal_pass REAL NOT NULL DEFAULT 16.0 CHECK(min_internal_pass >= 0),
    min_external_pass REAL NOT NULL DEFAULT 21.0 CHECK(min_external_pass >= 0),
    min_total_pass REAL NOT NULL DEFAULT 40.0 CHECK(min_total_pass >= 0),
    credits INTEGER NOT NULL DEFAULT 4 CHECK(credits > 0)
);

-- 4. FACULTY ASSIGNMENTS
CREATE TABLE IF NOT EXISTS faculty_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    section TEXT NOT NULL,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE(faculty_user_id, subject_id, semester, section)
);

-- 5. RESULTS
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
    internal_marks REAL CHECK(internal_marks IS NULL OR (internal_marks >= 0 AND internal_marks <= 100)),
    external_marks REAL CHECK(external_marks IS NULL OR (external_marks >= 0 AND external_marks <= 100)),
    total_marks REAL CHECK(total_marks IS NULL OR (total_marks >= 0 AND total_marks <= 200)),
    grade TEXT NOT NULL DEFAULT 'PENDING',
    grade_points INTEGER NOT NULL DEFAULT 0 CHECK(grade_points BETWEEN 0 AND 10),
    is_passed INTEGER NOT NULL DEFAULT 0 CHECK(is_passed IN (0, 1)),
    is_absent INTEGER NOT NULL DEFAULT 0 CHECK(is_absent IN (0, 1)),
    is_published INTEGER NOT NULL DEFAULT 0 CHECK(is_published IN (0, 1)),
    published_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE(student_id, subject_id, semester)
);

-- 6. RESULT ACKNOWLEDGEMENTS
CREATE TABLE IF NOT EXISTS acknowledgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    acknowledged_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    comments TEXT,
    UNIQUE(result_id, student_id)
);

-- 7. RESULT QUERIES
CREATE TABLE IF NOT EXISTS result_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK(category IN ('Internal Marks Discrepancy', 'External Marks Re-evaluation', 'Total/Grade Calculation Error', 'Attendance/Assessment Record', 'Other')),
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'Under Review', 'Resolved', 'Rejected')),
    faculty_response TEXT,
    faculty_user_id INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 8. AUDIT EVENTS
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_user_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    old_value TEXT,
    new_value TEXT,
    reason TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 9. TOPIC ASSESSMENTS (Evidence for improvement engine)
CREATE TABLE IF NOT EXISTS topic_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    topic_name TEXT NOT NULL,
    score REAL NOT NULL CHECK(score >= 0),
    max_score REAL NOT NULL CHECK(max_score > 0),
    assessment_type TEXT NOT NULL,
    recorded_date TEXT NOT NULL DEFAULT (date('now', 'localtime'))
);

-- 10. IMPROVEMENT PLANS
CREATE TABLE IF NOT EXISTS improvement_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    target_sgpa REAL CHECK(target_sgpa IS NULL OR (target_sgpa >= 0 AND target_sgpa <= 10)),
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'In Progress', 'Completed', 'Faculty Reviewed')),
    recommendations_json TEXT NOT NULL,
    weekly_schedule_json TEXT NOT NULL,
    faculty_feedback TEXT,
    reviewed_by_faculty_id INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 11. PRACTICE LOGS
CREATE TABLE IF NOT EXISTS practice_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES improvement_plans(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    date_completed TEXT NOT NULL,
    practice_activity TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK(duration_minutes > 0),
    self_assessment_score REAL CHECK(self_assessment_score IS NULL OR (self_assessment_score >= 0 AND self_assessment_score <= 100)),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_students_usn ON students(usn);
CREATE INDEX IF NOT EXISTS idx_students_sem ON students(semester);
CREATE INDEX IF NOT EXISTS idx_results_student_sem ON results(student_id, semester);
CREATE INDEX IF NOT EXISTS idx_results_subject ON results(subject_id);
CREATE INDEX IF NOT EXISTS idx_results_published ON results(is_published);
CREATE INDEX IF NOT EXISTS idx_queries_student ON result_queries(student_id);
CREATE INDEX IF NOT EXISTS idx_queries_subject ON result_queries(subject_id);
CREATE INDEX IF NOT EXISTS idx_queries_status ON result_queries(status);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_faculty_assign ON faculty_assignments(faculty_user_id, subject_id);
CREATE INDEX IF NOT EXISTS idx_topic_student ON topic_scores(student_id, subject_id);
