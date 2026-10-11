"""
Unit Tests for Audit Logging (services/audit_service and repositories/audit_repository)
Verifies immutable event logging, mandatory reasons, and audit trail queryability.
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
    db_file = tmp_path / "test_audit.db"
    seed_database(db_file)
    return db_file


def test_audit_event_logged_on_mark_update(test_db):
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

    fac = user_repo.get_by_username("dr.sharma")
    sub = subject_repo.get_by_code("CS501")
    results = result_repo.get_subject_results(sub["id"], semester=5)
    target_res = results[0]

    old_int = target_res["internal_marks"]
    reason_str = "Re-evaluation of final lab assignment component"

    result_service.update_result_mark(
        faculty_user_id=fac["id"],
        result_id=target_res["id"],
        internal_marks=39.0,
        external_marks=target_res["external_marks"],
        reason=reason_str
    )

    # Inspect audit trail
    events = audit_repo.list_events(entity_type="result", entity_id=target_res["id"])
    assert len(events) >= 1
    latest_event = events[0]

    assert latest_event["action"] == "UPDATE_STUDENT_MARKS"
    assert latest_event["actor_user_id"] == fac["id"]
    assert latest_event["reason"] == reason_str
    assert f"Internal={old_int}" in latest_event["old_value"]
    assert "Internal=39.0" in latest_event["new_value"]


def test_audit_event_logged_on_publishing_toggle(test_db):
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

    fac = user_repo.get_by_username("dr.sharma")
    sub = subject_repo.get_by_code("CS501")

    # Unpublish
    result_service.set_publish_status(
        faculty_user_id=fac["id"],
        subject_id=sub["id"],
        semester=5,
        publish=False,
        reason="Temporary hold for re-checking practical grades"
    )

    events = audit_repo.list_events(entity_type="subject", entity_id=sub["id"])
    assert any(e["action"] == "UNPUBLISH_RESULTS" for e in events)

    # Publish back
    result_service.set_publish_status(
        faculty_user_id=fac["id"],
        subject_id=sub["id"],
        semester=5,
        publish=True,
        reason="Re-published following departmental ratification"
    )

    events_after = audit_repo.list_events(entity_type="subject", entity_id=sub["id"])
    assert events_after[0]["action"] == "PUBLISH_RESULTS"
    assert events_after[0]["reason"] == "Re-published following departmental ratification"
