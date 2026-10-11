"""
Unit Tests for the Academic Improvement Engine (services/improvement_service.py)
Tests Rules 1 through 6, topic-evidence constraints, non-stigmatizing phrasing, and plan persistence.
"""
import pytest
from services.improvement_service import ImprovementService, Recommendation


def test_rule_1_failed_subject_creates_recovery_plan():
    service = ImprovementService()
    results = [{
        "subject_code": "CS503",
        "subject_name": "Theory of Computation",
        "is_published": 1,
        "is_passed": 0,
        "grade": "F",
        "grade_points": 0,
        "internal_marks": 18.0,
        "external_marks": 18.0,
        "max_internal": 40.0,
        "max_external": 60.0,
        "min_internal_pass": 16.0,
        "min_external_pass": 21.0
    }]

    recs = service.generate_recommendations_for_results(results)
    assert len(recs) == 1
    rec = recs[0]
    assert rec.priority == "High"
    assert "Rule 1: Subject Recovery Plan" in rec.rule_applied
    assert "solve 5 previous year question papers" in rec.suggested_action.lower()


def test_rule_2_low_internal_score_reinforcement():
    service = ImprovementService()
    # Internal is 17/40 (42.5%, which is < 50%), External is 38/60 (63.3%, Cleared)
    results = [{
        "subject_code": "CS501",
        "subject_name": "Database Systems",
        "is_published": 1,
        "is_passed": 1,
        "grade": "B",
        "grade_points": 6,
        "internal_marks": 17.0,
        "external_marks": 38.0,
        "max_internal": 40.0,
        "max_external": 60.0,
        "min_internal_pass": 16.0,
        "min_external_pass": 21.0
    }]

    recs = service.generate_recommendations_for_results(results)
    rec = next(r for r in recs if "Rule 2" in r.rule_applied)
    assert "Foundational Internal Reinforcement" in rec.rule_applied
    assert "office hours" in rec.suggested_action.lower()


def test_rule_3_strong_internal_weak_external_exam_technique():
    service = ImprovementService()
    # Internal is 35/40 (87.5% - strong!), External is 25/60 (41.6% - weak/low external)
    results = [{
        "subject_code": "CS502",
        "subject_name": "Computer Networks",
        "is_published": 1,
        "is_passed": 1,
        "grade": "B+",
        "grade_points": 7,
        "internal_marks": 35.0,
        "external_marks": 25.0,
        "max_internal": 40.0,
        "max_external": 60.0,
        "min_internal_pass": 16.0,
        "min_external_pass": 21.0
    }]

    recs = service.generate_recommendations_for_results(results)
    rec = next(r for r in recs if "Rule 3" in r.rule_applied)
    assert "Examination Technique & Time Management" in rec.rule_applied
    assert "timed exam simulations" in rec.suggested_action.lower()


def test_rule_4_declining_semester_trend():
    service = ImprovementService()
    # Sem 4 SGPA: 8.5, Sem 5 SGPA: 7.2 (Drop of 1.3 points)
    historical_sgpas = {4: 8.5, 5: 7.2}
    results = []

    recs = service.generate_recommendations_for_results(results, historical_sgpas=historical_sgpas)
    assert len(recs) == 1
    rec = recs[0]
    assert "Rule 4: Semester Trajectory Alignment" in rec.rule_applied
    assert rec.priority == "High"
    assert "mentorship" in rec.suggested_action.lower()


def test_rule_5_unpublished_and_absent_status_resolution():
    service = ImprovementService()
    # Course CS505 is unpublished
    results = [{
        "subject_code": "CS505",
        "subject_name": "Cloud Computing",
        "is_published": 0,
        "is_passed": 0,
        "grade": "PENDING",
        "internal_marks": 35.0,
        "external_marks": 50.0
    }]

    recs = service.generate_recommendations_for_results(results)
    assert len(recs) == 1
    rec = recs[0]
    assert "Rule 5: Unpublished Result" in rec.rule_applied
    # Must NOT label them as failed!
    assert "fail" not in rec.reason.lower()
    assert "consult the department coordinator" in rec.suggested_action.lower()


def test_rule_6_passed_below_target():
    service = ImprovementService()
    # Passed with B grade (grade points 6), target SGPA is 8.5
    results = [{
        "subject_code": "CS504",
        "subject_name": "Software Engineering",
        "is_published": 1,
        "is_passed": 1,
        "grade": "B",
        "grade_points": 6,
        "internal_marks": 25.0,
        "external_marks": 35.0,
        "max_internal": 40.0,
        "max_external": 60.0,
        "min_internal_pass": 16.0,
        "min_external_pass": 21.0
    }]

    recs = service.generate_recommendations_for_results(results, target_sgpa=8.5)
    rec = next(r for r in recs if "Rule 6" in r.rule_applied)
    assert "Targeted Grade Elevation" in rec.rule_applied


def test_topic_recommendations_only_with_evidence():
    """
    CRITICAL CONSTRAINT: Do NOT infer exact weak topics from total marks alone.
    Only generate topic-specific recommendations from recorded assessment evidence.
    """
    service = ImprovementService()
    
    # Failed subject WITHOUT topic assessment evidence
    results_no_topics = [{
        "subject_code": "CS503",
        "subject_id": 101,
        "subject_name": "Theory of Computation",
        "is_published": 1,
        "is_passed": 0,
        "grade": "F",
        "grade_points": 0,
        "internal_marks": 15.0,
        "external_marks": 15.0,
        "max_internal": 40.0,
        "max_external": 60.0,
        "min_internal_pass": 16.0,
        "min_external_pass": 21.0
    }]

    recs_no_topics = service.generate_recommendations_for_results(results_no_topics, topic_scores=[])
    assert recs_no_topics[0].topic_evidence is None
    # Action does NOT make up fake topic names
    assert "specifically prioritize verified weak modules" not in recs_no_topics[0].suggested_action.lower()

    # Failed subject WITH topic assessment evidence
    topic_evidence = [
        {"subject_id": 101, "topic_name": "Decidability", "score": 3.0, "max_score": 15.0, "assessment_type": "Quiz 1"}
    ]
    recs_with_topics = service.generate_recommendations_for_results(results_no_topics, topic_scores=topic_evidence)
    assert recs_with_topics[0].topic_evidence is not None
    assert recs_with_topics[0].topic_evidence[0]["topic_name"] == "Decidability"
    assert "Decidability" in recs_with_topics[0].suggested_action
