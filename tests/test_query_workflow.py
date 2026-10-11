"""
Query Workflow and State Transition Tests
Tests the discrepancy query lifecycle: Submitted -> Under Review -> Resolved/Rejected,
and validates faculty assignment permissions and student isolation.
"""
import pytest
from database.seed_data import seed_database
from repositories.user_repository import UserRepository
from repositories.subject_repository import SubjectRepository
from repositories.faculty_repository import FacultyRepository
from repositories.student_repository import StudentRepository
from repositories.query_repository import QueryRepository
from repositories.audit_repository import AuditRepository
from services.query_service import QueryService


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_queries.db"
    seed_database(db_file)
    return db_file


def test_query_creation_and_student_isolation(test_db):
    user_repo = UserRepository(test_db)
    subject_repo = SubjectRepository(test_db)
    student_repo = StudentRepository(test_db)
    query_repo = QueryRepository(test_db)
    audit_repo = AuditRepository(test_db)
    faculty_repo = FacultyRepository(test_db)

    query_service = QueryService(
        query_repo=query_repo,
        student_repo=student_repo,
        faculty_repo=faculty_repo,
        subject_repo=subject_repo,
        audit_repo=audit_repo
    )

    stu1 = user_repo.get_by_username("usn101")
    stu2 = user_repo.get_by_username("usn102")
    sub_cs501 = subject_repo.get_by_code("CS501")

    # Student 1 raises a query
    q_id = query_service.submit_query(
        student_user_id=stu1["id"],
        subject_id=sub_cs501["id"],
        category="Internal Marks Discrepancy",
        description="My test 1 answer script was scored 18/20 but recorded as 8/20 on portal."
    )
    assert q_id > 0

    # Student 1 queries list includes this query
    q_list_1 = query_service.get_student_queries(stu1["id"])
    assert any(q["id"] == q_id for q in q_list_1)

    # Student 2 queries list DOES NOT include Student 1's query
    q_list_2 = query_service.get_student_queries(stu2["id"])
    assert not any(q["id"] == q_id for q in q_list_2)


def test_query_state_transitions_and_faculty_permissions(test_db):
    user_repo = UserRepository(test_db)
    subject_repo = SubjectRepository(test_db)
    student_repo = StudentRepository(test_db)
    query_repo = QueryRepository(test_db)
    audit_repo = AuditRepository(test_db)
    faculty_repo = FacultyRepository(test_db)

    query_service = QueryService(
        query_repo=query_repo,
        student_repo=student_repo,
        faculty_repo=faculty_repo,
        subject_repo=subject_repo,
        audit_repo=audit_repo
    )

    stu = user_repo.get_by_username("usn101")
    fac1 = user_repo.get_by_username("dr.sharma")    # Assigned to CS501
    fac2 = user_repo.get_by_username("prof.anita")   # NOT assigned to CS501
    sub_cs501 = subject_repo.get_by_code("CS501")

    q_id = query_service.submit_query(
        student_user_id=stu["id"],
        subject_id=sub_cs501["id"],
        category="Internal Marks Discrepancy",
        description="Need verification of attendance credit calculation."
    )

    # Unassigned faculty (Prof. Anita) attempts to update status -> raises PermissionError
    with pytest.raises(PermissionError, match="You are not authorized to review queries for this course"):
        query_service.update_query_status(
            faculty_user_id=fac2["id"],
            query_id=q_id,
            new_status="Under Review",
            faculty_response=None
        )

    # Assigned faculty updates to "Under Review" -> Succeeds
    success = query_service.update_query_status(
        faculty_user_id=fac1["id"],
        query_id=q_id,
        new_status="Under Review",
        faculty_response=None
    )
    assert success is True

    # Transitioning to Resolved WITHOUT response must fail
    with pytest.raises(ValueError, match="A detailed faculty response is required"):
        query_service.update_query_status(
            faculty_user_id=fac1["id"],
            query_id=q_id,
            new_status="Resolved",
            faculty_response=""
        )

    # Transitioning to Resolved WITH response -> Succeeds
    success_resolved = query_service.update_query_status(
        faculty_user_id=fac1["id"],
        query_id=q_id,
        new_status="Resolved",
        faculty_response="Attendance credits verified against ERP log; 5/5 granted."
    )
    assert success_resolved is True

    # Verify updated record
    updated_q = query_repo.get_by_id(q_id)
    assert updated_q["status"] == "Resolved"
    assert "Attendance credits verified" in updated_q["faculty_response"]
