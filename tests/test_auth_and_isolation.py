"""
Authentication and Data Isolation Tests
Verifies password hashing, credential checks, and strict student data isolation.
"""
import pytest
from pathlib import Path
from database.connection import get_connection
from database.seed_data import seed_database
from services.auth_service import AuthService
from services.result_service import ResultService
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from repositories.result_repository import ResultRepository


@pytest.fixture
def test_db(tmp_path):
    """Provides a fresh isolated test database for each test run."""
    db_file = tmp_path / "test_campus.db"
    seed_database(db_file)
    return db_file


def test_password_hashing_and_verification():
    raw_password = "SuperSecretPassword123!"
    h1, s1 = AuthService.hash_password(raw_password)
    h2, s2 = AuthService.hash_password(raw_password)

    # Different salts must yield different hashes
    assert s1 != s2
    assert h1 != h2

    # Verification must pass
    assert AuthService.verify_password(raw_password, h1, s1) is True
    assert AuthService.verify_password("WrongPassword!", h1, s1) is False


def test_authentication_workflow(test_db):
    auth_service = AuthService(
        user_repo=UserRepository(test_db),
        student_repo=StudentRepository(test_db)
    )

    # Valid faculty login
    fac = auth_service.authenticate("dr.sharma", "Password123!")
    assert fac is not None
    assert fac["role"] == "faculty"
    assert fac["full_name"] == "Dr. Ramesh Sharma"

    # Valid student login
    stu = auth_service.authenticate("usn101", "Student123!")
    assert stu is not None
    assert stu["role"] == "student"
    assert stu["usn"] == "1CI22CS101"

    # Invalid password
    bad = auth_service.authenticate("usn101", "WrongPassword!")
    assert bad is None


def test_student_data_isolation(test_db):
    """Verifies that students can access ONLY their own results."""
    user_repo = UserRepository(test_db)
    student_repo = StudentRepository(test_db)
    result_repo = ResultRepository(test_db)
    result_service = ResultService(
        result_repo=result_repo,
        student_repo=student_repo
    )

    # Student 1: Aarav Patel (usn101)
    user1 = user_repo.get_by_username("usn101")
    stu1 = student_repo.get_by_user_id(user1["id"])

    # Student 2: Bhavya Rao (usn102)
    user2 = user_repo.get_by_username("usn102")
    stu2 = student_repo.get_by_user_id(user2["id"])

    results_stu1 = result_service.get_student_results(user1["id"])
    results_stu2 = result_service.get_student_results(user2["id"])

    # Ensure all results returned for student 1 belong strictly to student 1
    for r in results_stu1:
        assert r["student_id"] == stu1["id"]
        assert r["student_id"] != stu2["id"]

    # Ensure all results returned for student 2 belong strictly to student 2
    for r in results_stu2:
        assert r["student_id"] == stu2["id"]
        assert r["student_id"] != stu1["id"]


def test_unpublished_results_hidden_from_students(test_db):
    """Verifies that unpublished courses (like CS505 in seed data) are hidden from students."""
    user_repo = UserRepository(test_db)
    student_repo = StudentRepository(test_db)
    result_repo = ResultRepository(test_db)
    result_service = ResultService(
        result_repo=result_repo,
        student_repo=student_repo
    )

    user1 = user_repo.get_by_username("usn101")
    results = result_service.get_student_results(user1["id"], semester=5)

    # In seed data, CS505 has is_published = 0
    course_codes = [r["subject_code"] for r in results]
    assert "CS501" in course_codes
    assert "CS502" in course_codes
    assert "CS503" in course_codes
    assert "CS504" in course_codes
    assert "CS505" not in course_codes  # Strictly hidden because unpublished!


def test_student_cannot_acknowledge_other_student_result(test_db):
    """Verifies that a student cannot acknowledge another student's marks."""
    user_repo = UserRepository(test_db)
    student_repo = StudentRepository(test_db)
    result_repo = ResultRepository(test_db)
    result_service = ResultService(
        result_repo=result_repo,
        student_repo=student_repo
    )

    user1 = user_repo.get_by_username("usn101")
    user2 = user_repo.get_by_username("usn102")

    # Get a result belonging to student 2
    stu2_results = result_repo.get_student_results(
        student_repo.get_by_user_id(user2["id"])["id"],
        only_published=False
    )
    target_result_id = stu2_results[0]["id"]

    # Student 1 attempts to acknowledge Student 2's result -> must raise PermissionError
    with pytest.raises(PermissionError, match="You cannot acknowledge another student's result"):
        result_service.acknowledge_result(
            student_user_id=user1["id"],
            result_id=target_result_id,
            comments="Unauthorized attempt"
        )
