"""
Database Seeding Script
Populates the database with rich, realistic synthetic academic data:
Users, Students, Faculty Assignments, Subjects, Results, Topics, Queries, and Audit Logs.
"""
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from typing import Optional, Union
from database.connection import get_db_context
from database.init_db import init_database
from services.auth_service import AuthService
from services.grading_service import GradingService
from config import DATABASE_PATH, DEMO_CREDENTIALS


def seed_database(db_path: Optional[Union[str, Path]] = None) -> None:
    """Populates the database with synthetic college data."""
    init_database(db_path)
    grading = GradingService()

    with get_db_context(db_path) as conn:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("Database already contains data. Skipping seeding.")
            return

        print("Seeding users and credentials...")
        # 1. Faculty Users
        fac1_hash, fac1_salt = AuthService.hash_password("Password123!")
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, role, full_name, email)
            VALUES (?, ?, ?, 'faculty', ?, ?)
        """, ("dr.sharma", fac1_hash, fac1_salt, "Dr. Ramesh Sharma", "r.sharma@campusinsight.edu"))
        fac1_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, role, full_name, email)
            VALUES (?, ?, ?, 'faculty', ?, ?)
        """, ("prof.anita", fac1_hash, fac1_salt, "Prof. Anita Deshmukh", "a.deshmukh@campusinsight.edu"))
        fac2_id = cursor.lastrowid

        # 2. Student Users & Profiles
        student_specs = [
            ("usn101", "Aarav Patel", "aarav.patel@student.edu", "1CI22CS101", 5, "A"),
            ("usn102", "Bhavya Rao", "bhavya.rao@student.edu", "1CI22CS102", 5, "A"),
            ("usn103", "Chirag Nair", "chirag.nair@student.edu", "1CI22CS103", 5, "B"),
            ("usn104", "Divya Kulkarni", "divya.kulkarni@student.edu", "1CI22CS104", 5, "A"),
            ("usn105", "Esha Menon", "esha.menon@student.edu", "1CI22CS105", 5, "B"),
            ("usn106", "Farhan Ali", "farhan.ali@student.edu", "1CI22CS106", 5, "A"),
            ("usn107", "Gauri Sen", "gauri.sen@student.edu", "1CI22CS107", 5, "B"),
            ("usn108", "Harish Verma", "harish.verma@student.edu", "1CI22CS108", 5, "A"),
        ]

        student_ids = {}
        stud_pwd_hash, stud_pwd_salt = AuthService.hash_password("Student123!")

        for username, name, email, usn, sem, sec in student_specs:
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, role, full_name, email)
                VALUES (?, ?, ?, 'student', ?, ?)
            """, (username, stud_pwd_hash, stud_pwd_salt, name, email))
            u_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO students (user_id, usn, branch, semester, section, batch_year)
                VALUES (?, ?, 'Computer Science and Engineering', ?, ?, 2022)
            """, (u_id, usn, sem, sec))
            student_ids[usn] = cursor.lastrowid

        # 3. Subjects
        subjects_data = [
            # Sem 4 subjects (historical)
            ("CS401", "Design & Analysis of Algorithms", 4, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 4),
            ("CS402", "Operating Systems", 4, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 4),
            ("CS403", "Microcontrollers & Embedded Systems", 4, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 3),
            # Sem 5 subjects (current)
            ("CS501", "Database Management Systems", 5, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 4),
            ("CS502", "Computer Networks", 5, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 4),
            ("CS503", "Theory of Computation", 5, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 3),
            ("CS504", "Software Engineering & Agile", 5, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 3),
            ("CS505", "Cloud Computing & DevOps", 5, "Computer Science and Engineering", 40.0, 60.0, 16.0, 21.0, 40.0, 3),
        ]

        subject_ids = {}
        for code, name, sem, branch, m_int, m_ext, p_int, p_ext, p_tot, cred in subjects_data:
            cursor.execute("""
                INSERT INTO subjects (code, name, semester, branch, max_internal, max_external, min_internal_pass, min_external_pass, min_total_pass, credits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, sem, branch, m_int, m_ext, p_int, p_ext, p_tot, cred))
            subject_ids[code] = cursor.lastrowid

        # 4. Faculty Course Assignments
        # Dr. Sharma teaches CS501 and CS503 (both sections A and B)
        # Prof. Anita teaches CS502 and CS504 (both sections A and B)
        for sec in ["A", "B"]:
            cursor.execute("INSERT INTO faculty_assignments (faculty_user_id, subject_id, semester, section) VALUES (?, ?, 5, ?)",
                           (fac1_id, subject_ids["CS501"], sec))
            cursor.execute("INSERT INTO faculty_assignments (faculty_user_id, subject_id, semester, section) VALUES (?, ?, 5, ?)",
                           (fac1_id, subject_ids["CS503"], sec))
            cursor.execute("INSERT INTO faculty_assignments (faculty_user_id, subject_id, semester, section) VALUES (?, ?, 5, ?)",
                           (fac2_id, subject_ids["CS502"], sec))
            cursor.execute("INSERT INTO faculty_assignments (faculty_user_id, subject_id, semester, section) VALUES (?, ?, 5, ?)",
                           (fac2_id, subject_ids["CS504"], sec))

        # 5. Results (Sem 4 Historical)
        sem4_marks = [
            ("1CI22CS101", "CS401", 36, 52), ("1CI22CS101", "CS402", 34, 48), ("1CI22CS101", "CS403", 35, 50),
            ("1CI22CS102", "CS401", 38, 55), ("1CI22CS102", "CS402", 36, 54), ("1CI22CS102", "CS403", 37, 52),
            ("1CI22CS103", "CS401", 28, 38), ("1CI22CS103", "CS402", 26, 35), ("1CI22CS103", "CS403", 25, 36),
            ("1CI22CS104", "CS401", 32, 44), ("1CI22CS104", "CS402", 30, 42), ("1CI22CS104", "CS403", 31, 40),
            ("1CI22CS105", "CS401", 35, 49), ("1CI22CS105", "CS402", 33, 46), ("1CI22CS105", "CS403", 34, 48),
        ]
        for usn, scode, int_m, ext_m in sem4_marks:
            s_id = student_ids[usn]
            sub_id = subject_ids[scode]
            eval_res = grading.evaluate_result(int_m, ext_m)
            cursor.execute("""
                INSERT INTO results (student_id, subject_id, semester, internal_marks, external_marks, total_marks, grade, grade_points, is_passed, is_published, published_at)
                VALUES (?, ?, 4, ?, ?, ?, ?, ?, ?, 1, datetime('now', '-60 days'))
            """, (s_id, sub_id, int_m, ext_m, eval_res["total_marks"], eval_res["grade"], eval_res["grade_points"], eval_res["is_passed"]))

        # 6. Results (Sem 5 Current)
        # Note: CS501, CS502, CS503, CS504 are PUBLISHED.
        # CS505 is UNPUBLISHED (demonstrates unpublished isolation and Rule 5!).
        sem5_marks = [
            # Aarav Patel (High performer)
            ("1CI22CS101", "CS501", 37, 54, 1),
            ("1CI22CS101", "CS502", 35, 50, 1),
            ("1CI22CS101", "CS503", 34, 48, 1),
            ("1CI22CS101", "CS504", 38, 52, 1),
            ("1CI22CS101", "CS505", 36, 50, 0),  # UNPUBLISHED

            # Bhavya Rao (Top of Class)
            ("1CI22CS102", "CS501", 39, 56, 1),
            ("1CI22CS102", "CS502", 38, 55, 1),
            ("1CI22CS102", "CS503", 37, 53, 1),
            ("1CI22CS102", "CS504", 39, 57, 1),
            ("1CI22CS102", "CS505", 38, 54, 0),  # UNPUBLISHED

            # Chirag Nair (Needs Subject Recovery: Failed CS503 SEE=18/60, and below pass)
            ("1CI22CS103", "CS501", 28, 38, 1),
            ("1CI22CS103", "CS502", 27, 36, 1),
            ("1CI22CS103", "CS503", 18, 18, 1),  # FAIL: External < 21 cutoff
            ("1CI22CS103", "CS504", 26, 35, 1),
            ("1CI22CS103", "CS505", 25, 30, 0),  # UNPUBLISHED

            # Divya Kulkarni (Low Internals: CS501 CIE=17/40)
            ("1CI22CS104", "CS501", 17, 38, 1),  # Low CIE < 50%
            ("1CI22CS104", "CS502", 29, 41, 1),
            ("1CI22CS104", "CS503", 28, 39, 1),
            ("1CI22CS104", "CS504", 30, 42, 1),
            ("1CI22CS104", "CS505", 28, 38, 0),  # UNPUBLISHED

            # Esha Menon (Strong Internal, Weak External: CS502 CIE=35/40, SEE=25/60)
            ("1CI22CS105", "CS501", 33, 44, 1),
            ("1CI22CS105", "CS502", 35, 25, 1),  # CIE=87.5%, SEE=41.6% (Rule 3)
            ("1CI22CS105", "CS503", 30, 42, 1),
            ("1CI22CS105", "CS504", 32, 45, 1),
            ("1CI22CS105", "CS505", 31, 40, 0),  # UNPUBLISHED

            # Farhan Ali (Solid Average)
            ("1CI22CS106", "CS501", 31, 42, 1),
            ("1CI22CS106", "CS502", 30, 40, 1),
            ("1CI22CS106", "CS503", 29, 38, 1),
            ("1CI22CS106", "CS504", 31, 41, 1),
            ("1CI22CS106", "CS505", 30, 39, 0),  # UNPUBLISHED

            # Gauri Sen (Good Consistency)
            ("1CI22CS107", "CS501", 34, 46, 1),
            ("1CI22CS107", "CS502", 33, 44, 1),
            ("1CI22CS107", "CS503", 32, 43, 1),
            ("1CI22CS107", "CS504", 35, 47, 1),
            ("1CI22CS107", "CS505", 33, 42, 0),  # UNPUBLISHED

            # Harish Verma (Absent in CS503 SEE)
            ("1CI22CS108", "CS501", 30, 40, 1),
            ("1CI22CS108", "CS502", 28, 38, 1),
            ("1CI22CS108", "CS503", 0, 0, 1),   # Will mark as absent below
            ("1CI22CS108", "CS504", 29, 39, 1),
            ("1CI22CS108", "CS505", 27, 36, 0),  # UNPUBLISHED
        ]

        result_ids = []
        for usn, scode, int_m, ext_m, is_pub in sem5_marks:
            s_id = student_ids[usn]
            sub_id = subject_ids[scode]
            is_ab = 1 if (usn == "1CI22CS108" and scode == "CS503") else 0

            eval_res = grading.evaluate_result(int_m, ext_m, is_absent=bool(is_ab))
            cursor.execute("""
                INSERT INTO results (
                    student_id, subject_id, semester, internal_marks, external_marks,
                    total_marks, grade, grade_points, is_passed, is_absent, is_published,
                    published_at
                )
                VALUES (?, ?, 5, ?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 1 THEN datetime('now', '-5 days') ELSE NULL END)
            """, (
                s_id, sub_id,
                None if is_ab else int_m,
                None if is_ab else ext_m,
                eval_res["total_marks"], eval_res["grade"], eval_res["grade_points"],
                eval_res["is_passed"], is_ab, is_pub, is_pub
            ))
            result_ids.append(cursor.lastrowid)

        # 7. Result Acknowledgement (Aarav acknowledged CS501)
        cursor.execute("""
            INSERT INTO acknowledgements (result_id, student_id, comments, acknowledged_at)
            VALUES (1, ?, 'Reviewed marks for DBMS; no discrepancies observed.', datetime('now', '-2 days'))
        """, (student_ids["1CI22CS101"],))

        # 8. Topic Assessments (Evidence for Improvement Engine)
        topics = [
            (student_ids["1CI22CS103"], subject_ids["CS503"], "Turing Machines & Decidability", 3.5, 15.0, "Quiz 1"),
            (student_ids["1CI22CS103"], subject_ids["CS503"], "Pushdown Automata & CFLs", 6.0, 15.0, "Assignment 2"),
            (student_ids["1CI22CS103"], subject_ids["CS503"], "Regular Expressions & Finite Automata", 13.0, 15.0, "Unit Test 1"),
            (student_ids["1CI22CS104"], subject_ids["CS501"], "Relational Algebra & Normal Forms", 5.5, 15.0, "Quiz 1"),
            (student_ids["1CI22CS105"], subject_ids["CS502"], "Subnetting & IP Routing Protocols", 13.5, 15.0, "Assignment 1"),
            (student_ids["1CI22CS105"], subject_ids["CS502"], "Socket Programming & Transport Layer", 14.0, 15.0, "Lab Evaluation"),
        ]
        for s_id, sub_id, t_name, sc, m_sc, a_type in topics:
            cursor.execute("""
                INSERT INTO topic_scores (student_id, subject_id, topic_name, score, max_score, assessment_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (s_id, sub_id, t_name, sc, m_sc, a_type))

        # 9. Discrepancy Queries
        cursor.execute("""
            INSERT INTO result_queries (student_id, subject_id, category, description, status, faculty_response, faculty_user_id, created_at, updated_at)
            VALUES (?, ?, 'Internal Marks Discrepancy', 'My Quiz 2 mark was recorded as 4 instead of 14 on the portal.', 'Submitted', NULL, NULL, datetime('now', '-3 days'), datetime('now', '-3 days'))
        """, (student_ids["1CI22CS103"], subject_ids["CS501"]))

        cursor.execute("""
            INSERT INTO result_queries (student_id, subject_id, category, description, status, faculty_response, faculty_user_id, created_at, updated_at)
            VALUES (?, ?, 'External Marks Re-evaluation', 'Requesting verification of question 4c in SEE answer sheet.', 'Resolved', 'Answer script re-checked. Verified total 55/60 is correct.', ?, datetime('now', '-4 days'), datetime('now', '-1 days'))
        """, (student_ids["1CI22CS102"], subject_ids["CS502"], fac2_id))

        # 10. Audit Events
        cursor.execute("""
            INSERT INTO audit_events (actor_user_id, action, entity_type, entity_id, old_value, new_value, reason, timestamp)
            VALUES (?, 'PUBLISH_RESULTS', 'subject', ?, 'Unpublished', 'Published', 'Departmental approval of 5th semester SEE results', datetime('now', '-5 days'))
        """, (fac1_id, subject_ids["CS501"]))

        cursor.execute("""
            INSERT INTO audit_events (actor_user_id, action, entity_type, entity_id, old_value, new_value, reason, timestamp)
            VALUES (?, 'UPDATE_STUDENT_MARKS', 'result', 1, 'Internal=35.0, External=54.0, Total=89.0, Grade=A+', 'Internal=37.0, External=54.0, Total=91.0, Grade=O', 'Rectified CIE bonus assignment score', datetime('now', '-4 days'))
        """, (fac1_id,))

        cursor.execute("""
            INSERT INTO audit_events (actor_user_id, action, entity_type, entity_id, old_value, new_value, reason, timestamp)
            VALUES (?, 'RESOLVE_QUERY', 'query', 2, 'Status: Under Review', 'Status: Resolved', 'Re-evaluation completed and communicated to candidate', datetime('now', '-1 days'))
        """, (fac2_id,))

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
