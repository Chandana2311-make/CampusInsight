"""
Persistence and Database Integrity Tests
Verifies that database mutations persist cleanly across application restarts and connection closures,
and that transactions roll back atomically upon error.
"""
import pytest
from database.connection import get_connection, get_db_context
from database.seed_data import seed_database
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from repositories.result_repository import ResultRepository


@pytest.fixture
def test_db_path(tmp_path):
    db_file = tmp_path / "persistence_test.db"
    seed_database(db_file)
    return db_file


def test_data_persists_across_connection_reopens(test_db_path):
    # Step 1: Open first connection and insert a student record
    conn1 = get_connection(test_db_path)
    user_repo1 = UserRepository(test_db_path)
    student_repo1 = StudentRepository(test_db_path)

    new_user_id = user_repo1.create_user(
        username="new_persisted_student",
        password_hash="testhash123",
        salt="testsalt123",
        role="student",
        full_name="Persisted Student",
        email="persisted@student.edu"
    )
    new_stu_id = student_repo1.create_student(
        user_id=new_user_id,
        usn="1CI22CS999",
        branch="Computer Science and Engineering",
        semester=5,
        section="A"
    )
    conn1.close()  # Simulate complete application process exit / connection close

    # Step 2: Open entirely fresh connection and verify record exists
    conn2 = get_connection(test_db_path)
    user_repo2 = UserRepository(test_db_path)
    student_repo2 = StudentRepository(test_db_path)

    found_user = user_repo2.get_by_username("new_persisted_student")
    assert found_user is not None
    assert found_user["id"] == new_user_id

    found_student = student_repo2.get_by_usn("1CI22CS999")
    assert found_student is not None
    assert found_student["id"] == new_stu_id
    assert found_student["full_name"] == "Persisted Student"

    conn2.close()


def test_atomic_transaction_rollback_on_failure(test_db_path):
    """Verifies that failures inside a transaction cleanly roll back all changes."""
    user_repo = UserRepository(test_db_path)

    # Count users before
    users_before = len(user_repo.list_users())

    with pytest.raises(RuntimeError):
        with get_db_context(test_db_path) as conn:
            # 1. Insert a user
            user_repo.create_user(
                username="rollback_user",
                password_hash="dummy",
                salt="dummy",
                role="student",
                full_name="Rollback Candidate",
                email="rollback@test.edu",
                conn=conn
            )
            # 2. Simulate an intentional exception midway
            raise RuntimeError("Intentional crash during transaction")

    # Verify that 'rollback_user' was rolled back and NOT persisted
    users_after = len(user_repo.list_users())
    assert users_after == users_before

    rolled_back_user = user_repo.get_by_username("rollback_user")
    assert rolled_back_user is None
