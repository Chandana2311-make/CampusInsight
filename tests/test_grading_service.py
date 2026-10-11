"""
Unit Tests for Grading Service
Validates mark boundaries, configurable passing cutoffs, letter grade scales, and SGPA/CGPA calculations.
"""
import pytest
from services.grading_service import GradingService


def test_mark_range_validation():
    service = GradingService()
    
    # Internal marks out of range (> 40)
    with pytest.raises(ValueError, match="Internal marks 45.0 out of permitted range"):
        service.evaluate_result(internal_marks=45.0, external_marks=50.0, max_internal=40.0, max_external=60.0)

    # Negative internal marks
    with pytest.raises(ValueError, match="Internal marks -2.0 out of permitted range"):
        service.evaluate_result(internal_marks=-2.0, external_marks=50.0, max_internal=40.0, max_external=60.0)

    # External marks out of range (> 60)
    with pytest.raises(ValueError, match="External marks 65.0 out of permitted range"):
        service.evaluate_result(internal_marks=35.0, external_marks=65.0, max_internal=40.0, max_external=60.0)


def test_standard_passing_and_grade_scales():
    service = GradingService()

    # Outstanding Grade (90%+)
    res_o = service.evaluate_result(internal_marks=38.0, external_marks=55.0)
    assert res_o["is_passed"] == 1
    assert res_o["grade"] == "O"
    assert res_o["grade_points"] == 10
    assert res_o["total_marks"] == 93.0

    # Excellent Grade (80-89%)
    res_aplus = service.evaluate_result(internal_marks=34.0, external_marks=50.0)
    assert res_aplus["is_passed"] == 1
    assert res_aplus["grade"] == "A+"
    assert res_aplus["grade_points"] == 9

    # Just passing (40%)
    res_pass = service.evaluate_result(internal_marks=16.0, external_marks=24.0)
    assert res_pass["is_passed"] == 1
    assert res_pass["grade"] == "P"
    assert res_pass["grade_points"] == 4


def test_separate_internal_and_external_passing_requirements():
    service = GradingService()

    # Case 1: Total is >= 40, but external is below minimum external cutoff (21)
    # CIE = 35/40 (Very high), SEE = 18/60 (Below 21 cutoff), Total = 53
    res_ext_fail = service.evaluate_result(
        internal_marks=35.0,
        external_marks=18.0,
        min_internal_pass=16.0,
        min_external_pass=21.0,
        min_total_pass=40.0
    )
    assert res_ext_fail["is_passed"] == 0
    assert res_ext_fail["grade"] == "F"
    assert res_ext_fail["grade_points"] == 0
    assert "External marks (18.0) below minimum required" in res_ext_fail["remarks"]

    # Case 2: Total is >= 40, but internal is below minimum internal cutoff (16)
    # CIE = 12/40 (Below 16), SEE = 40/60 (Pass), Total = 52
    res_int_fail = service.evaluate_result(
        internal_marks=12.0,
        external_marks=40.0,
        min_internal_pass=16.0,
        min_external_pass=21.0,
        min_total_pass=40.0
    )
    assert res_int_fail["is_passed"] == 0
    assert res_int_fail["grade"] == "F"
    assert "Internal marks (12.0) below minimum required" in res_int_fail["remarks"]


def test_configurable_passing_rules():
    # University with stricter requirements: 50% internal, 45% external, 50% total
    custom_rules = {
        "min_internal_percentage": 50.0,  # 20 / 40
        "min_external_percentage": 45.0,  # 27 / 60
        "min_total_percentage": 50.0,     # 50 / 100
    }
    custom_service = GradingService(passing_rules=custom_rules)

    # 18/40 internal passes default 40% (16), but fails custom 50% (20)
    res = custom_service.evaluate_result(internal_marks=18.0, external_marks=35.0)
    assert res["is_passed"] == 0
    assert res["grade"] == "F"


def test_absent_and_pending_handling():
    service = GradingService()

    # Absent
    res_absent = service.evaluate_result(internal_marks=30.0, external_marks=45.0, is_absent=True)
    assert res_absent["is_absent"] == 1
    assert res_absent["is_passed"] == 0
    assert res_absent["grade"] == "F"
    assert res_absent["status_label"] == "Absent"

    # Pending
    res_pending = service.evaluate_result(internal_marks=None, external_marks=None)
    assert res_pending["grade"] == "PENDING"
    assert res_pending["status_label"] == "Pending"


def test_sgpa_and_cgpa_calculation():
    service = GradingService()

    results = [
        {"subject_code": "CS501", "credits": 4, "grade_points": 10, "grade": "O"},  # 4 * 10 = 40
        {"subject_code": "CS502", "credits": 4, "grade_points": 8, "grade": "A"},   # 4 * 8  = 32
        {"subject_code": "CS503", "credits": 3, "grade_points": 6, "grade": "B"},   # 3 * 6  = 18
        {"subject_code": "CS504", "credits": 3, "grade_points": 0, "grade": "F"},   # 3 * 0  = 0
    ]
    # Total credit points = 40 + 32 + 18 + 0 = 90
    # Total credits = 4 + 4 + 3 + 3 = 14
    # Expected SGPA = 90 / 14 = 6.43
    sgpa = service.calculate_sgpa(results)
    assert sgpa == 6.43

    # CGPA across two semesters
    # Sem 1: SGPA 8.0, 20 credits
    # Sem 2: SGPA 6.43, 14 credits
    # Weighted = (8.0 * 20 + 6.43 * 14) / (20 + 14) = (160 + 90.02) / 34 = 250.02 / 34 = 7.35
    sem_data = {
        1: (8.0, 20),
        2: (6.43, 14)
    }
    cgpa = service.calculate_cgpa(sem_data)
    assert cgpa == 7.35
