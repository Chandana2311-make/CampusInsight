"""
Student Dashboard: My Results Page
Presents published academic results, official grades, credits, SGPA, and status indicators.
Enforces strict student data isolation: students only see their own published results.
"""
import streamlit as st
import pandas as pd
from ui.components import render_page_header, render_metric_card, render_status_badge
from services.result_service import ResultService
from services.grading_service import GradingService


def render_student_results(user: dict) -> None:
    """Renders the student results table and semester breakdown."""
    render_page_header(
        title="Official Academic Results 📜",
        subtitle=f"Student USN: {user.get('usn', 'N/A')} | Published Examination Records"
    )

    result_service = ResultService()
    grading_service = GradingService()

    # Security: retrieves ONLY published results for this authenticated student
    all_results = result_service.get_student_results(user["id"])

    if not all_results:
        st.info("No published academic results are currently released for your profile.")
        return

    # Semester filter
    available_sems = sorted(list({r["semester"] for r in all_results}), reverse=True)
    selected_sem = st.selectbox(
        "Select Academic Semester:",
        options=available_sems,
        format_func=lambda s: f"Semester {s} ({'Current' if s == user.get('semester') else 'Historical'})"
    )

    sem_results = [r for r in all_results if r["semester"] == selected_sem]
    sgpa = grading_service.calculate_sgpa(sem_results)
    total_credits = sum(r.get("credits", 0) for r in sem_results)
    cleared_credits = sum(r.get("credits", 0) for r in sem_results if r.get("is_passed") == 1)

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Semester SGPA", f"{sgpa:.2f}" if sgpa else "N/A", "10-Point Scale")
    with c2:
        render_metric_card("Total Credits", str(total_credits), "Registered")
    with c3:
        render_metric_card("Credits Earned", str(cleared_credits), f"{round((cleared_credits/total_credits*100) if total_credits else 0)}% Completed")
    with c4:
        render_metric_card("Result Status", "OFFICIALLY PUBLISHED", "Verified Record")

    # Data Source Notice
    st.markdown("""
        <div class="notice-box">
            <b>Official Evaluation Notice:</b> The marks below reflect departmental semester-end notifications. 
            All values are verified against university passing regulations (CIE ≥ 40%, SEE ≥ 35%, Total ≥ 40%).
        </div>
    """, unsafe_allow_html=True)

    # Clean Results Data Table
    table_rows = []
    for r in sem_results:
        ack_status = "✅ Acknowledged" if r.get("ack_id") else "⏳ Unconfirmed"
        table_rows.append({
            "Course Code": r["subject_code"],
            "Course Title": r["subject_name"],
            "Credits": r["credits"],
            "Internal (CIE / 40)": r["internal_marks"] if r["internal_marks"] is not None else "AB",
            "External (SEE / 60)": r["external_marks"] if r["external_marks"] is not None else "AB",
            "Total (100)": r["total_marks"] if r["total_marks"] is not None else 0,
            "Letter Grade": r["grade"],
            "Grade Points": r["grade_points"],
            "Clearance": "PASS" if r["is_passed"] == 1 else "FAIL",
            "Acknowledgement": ack_status
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Detailed grade breakdown expander
    with st.expander("🔍 View Official Grade Scale & Passing Cutoffs"):
        st.markdown("""
        | Grade | Total Score Range | Grade Points | Performance Level |
        |---|---|---|---|
        | **O** | 90% – 100% | 10 | Outstanding |
        | **A+** | 80% – 89% | 9 | Excellent |
        | **A** | 70% – 79% | 8 | Very Good |
        | **B+** | 60% – 69% | 7 | Good |
        | **B** | 55% – 59% | 6 | Above Average |
        | **C** | 50% – 54% | 5 | Average |
        | **P** | 40% – 49% | 4 | Pass |
        | **F** | < 40% (or CIE < 16 / SEE < 21) | 0 | Fail / Needs Recovery |
        """)
