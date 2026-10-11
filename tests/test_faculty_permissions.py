"""
Faculty Authorization & Subject-Assignment Enforcement Tests
Verifies that faculty can access/modify results only for assigned courses,
mandates justification reasons, and checks CSV validation rules.
"""
import pytest
from database.seed_data import seed_database
from repositories.user_repository import UserRepository
from repositories.subject_repository import SubjectRepository
from repositories.faculty_repository import FacultyRepository
from repositories.result_repository import ResultRepository
from repositories.audit_repository import AuditRepository
from services.result_service import ResultService


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_faculty.db"
    seed_database(db_file)
    return db_file


def test_faculty_course_access_authorization(test_db):
    user_repo = UserRepository(test_db)
    subject_repo = SubjectRepository(test_db)
    faculty_repo = FacultyRepository(test_db)
    result_repo = ResultRepository(test_db)
    audit_repo = AuditRepository(test_db)

    result_service = ResultService(
        result_repo=result_repo,
        subject_repo=subject_repo,
        faculty_repo=faculty_repo,
        audit_repo=audit_repo
    )

    fac1 = user_repo.get_by_username("dr.sharma")
    sub_cs501 = subject_repo.get_by_code("CS501") # Assigned to Dr. Sharma
    sub_cs502 = subject_repo.get_by_code("CS502") # Assigned to Prof. Anita

    # Dr. Sharma CAN access CS501 results
    res_cs501 = result_service.get_faculty_subject_results(
        faculty_user_id=fac1["id"],
        subject_id=sub_cs501["id"],
        semester=5
    )
    assert len(res_cs501) > 0

    # Dr. Sharma CANNOT access CS502 results -> Raises PermissionError
    with pytest.raises(PermissionError, match="Access denied: You are not authorized"):
        result_service.get_faculty_subject_results(
            faculty_user_id=fac1["id"],
            subject_id=sub_cs502["id"],
            semester=5
        )


def test_faculty_cannot_modify_unassigned_course_marks(test_db):
    user_repo = UserRepository(test_db)
    subject_repo = SubjectRepository(test_db)
    faculty_repo = FacultyRepository(test_db)
    result_repo = ResultRepository(test_db)
    audit_repo = AuditRepository(test_db)

    result_service = ResultService(
        result_repo=result_repo,
        subject_repo=subject_repo,
        faculty_repo=faculty_repo,
        audit_repo=audit_repo
    )

    fac1 = user_repo.get_by_username("dr.sharma")
    sub_cs502 = subject_repo.get_by_code("CS502") # Assigned to Prof. Anita

    # Find a result for CS502
    cs502_results = result_repo.get_subject_results(sub_cs502["id"], semester=5)
    target_res = cs502_results[0]

    # Dr. Sharma tries to modify marks for CS502
    with pytest.raises(PermissionError, match="You are not authorized to modify results for this subject"):
        result_service.update_result_mark(
            faculty_user_id=fac1["id"],
            result_id=target_res["id"],
            internal_marks=35.0,
            external_marks=50.0,
            reason="Unauthorized change test"
        )


def test_mandatory_justification_reason_for_mark_changes(test_db):
    user_repo = UserRepository(test_db)
    subject_repo = SubjectRepository(test_db)
    faculty_repo = FacultyRepository(test_db)
    result_repo = ResultRepository(test_db)
    audit_repo = AuditRepository(test_db)

    result_service = ResultService(
        result_repo=result_repo,
        subject_repo=subject_repo,
        faculty_repo=faculty_repo,
        audit_repo=audit_repo
    )

    fac1 = user_repo.get_by_username("dr.sharma")
    sub_cs501 = subject_repo.get_by_code("CS501")
    cs501_results = result_repo.get_subject_results(sub_cs501["id"], semester=5)
    target_res = cs501_results[0]

    # Attempting to change mark with empty or trivial reason fails
    with pytest.raises(ValueError, match="A clear, valid justification reason"):
        result_service.update_result_mark(
            faculty_user_id=fac1["id"],
            result_id=target_res["id"],
            internal_marks=35.0,
            external_marks=50.0,
            reason=""
        )

    with pytest.raises(ValueError, match="A clear, valid justification reason"):
        result_service.update_result_mark(
            faculty_user_id=fac1["id"],
            result_id=target_res["id"],
            internal_marks=35.0,
            external_marks=50.0,
            reason="bad" # Less than 5 chars
        )


def test_csv_validation_engine(test_db):
    subject_repo = SubjectRepository(test_db)
    result_service = ResultService(subject_repo=subject_repo)

    sub_cs501 = subject_repo.get_by_code("CS501")

    # CSV with duplicate USN and out-of-range marks
    csv_content = """USN,Internal,External,Is_Absent
1CI22CS101,38,55,0
1CI22CS101,35,50,0
1CI22CS102,45,55,0
1CI22CS103,30,65,0
1CI22CS104,abc,50,0
1CI22CS999,35,45,0
"""
    valid_rows, error_rows = result_service.validate_csv_content(
        csv_text_or_bytes=csv_content,
        subject_id=sub_cs501["id"],
        semester=5
    )

    # 1CI22CS101 first row is valid
    assert len(valid_rows) == 1
    assert valid_rows[0]["usn"] == "1CI22CS101"

    # All others must be in error rows
    error_messages = [e["error"] for e in error_rows]
    assert any("Duplicate record" in err or "Duplicate USN" in err for err in error_messages)
    assert any("Internal mark 45.0 exceeds range" in err for err in error_messages)
    assert any("External mark 65.0 exceeds range" in err for err in error_messages)
    assert any("must be numeric" in err for err in error_messages)
    assert any("not registered" in err for err in error_messages)


def test_csv_flexible_column_aliases(test_db):
    """Verifies that college marksheet headers like Roll_No, CIE, SEE are properly mapped."""
    subject_repo = SubjectRepository(test_db)
    result_service = ResultService(subject_repo=subject_repo)

    sub_cs501 = subject_repo.get_by_code("CS501")

    # CSV using Indian college aliases: Roll_No, CIE, SEE, Status
    college_csv = """Roll_No,CIE,SEE,Status
1CI22CS101,37,53,0
1CI22CS102,39,57,0
"""
    valid_rows, error_rows = result_service.validate_csv_content(
        csv_text_or_bytes=college_csv,
        subject_id=sub_cs501["id"],
        semester=5
    )

    assert len(error_rows) == 0
    assert len(valid_rows) == 2
    assert valid_rows[0]["usn"] == "1CI22CS101"
    assert valid_rows[0]["internal_marks"] == 37.0
    assert valid_rows[0]["external_marks"] == 53.0
    assert valid_rows[0]["grade"] == "O"

