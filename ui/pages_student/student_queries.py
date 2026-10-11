"""
Student Dashboard: Result Queries Page
Allows students to raise discrepancy queries and track the lifecycle (Submitted -> Under Review -> Resolved/Rejected).
Enforces student data isolation: students only see their own query records.
"""
import streamlit as st
import pandas as pd
from ui.components import render_page_header, render_status_badge
from services.query_service import QueryService
from services.result_service import ResultService
from repositories.subject_repository import SubjectRepository


def render_student_queries(user: dict) -> None:
    """Renders query submission and status history."""
    render_page_header(
        title="Result Discrepancy & Evaluation Queries 💬",
        subtitle=f"Student USN: {user.get('usn', 'N/A')} | Formal Academic Resolution System"
    )

    query_service = QueryService()
    subject_repo = SubjectRepository()
    result_service = ResultService()

    # Load enrolled subjects for the student
    published_results = result_service.get_student_results(user["id"])
    if not published_results:
        st.info("No published courses available to raise queries for.")
        return

    sub_options = {f"{r['subject_code']} - {r['subject_name']}": r["subject_id"] for r in published_results}

    tab_raise, tab_history = st.tabs(["➕ Raise New Query", "📜 My Query History & Responses"])

    # TAB 1: Raise Query
    with tab_raise:
        st.markdown("### Submit an Evaluation Discrepancy")
        st.caption("Your submission will be routed directly to the authorized faculty instructor for formal review.")

        categories = [
            "Internal Marks Discrepancy",
            "External Marks Re-evaluation",
            "Total/Grade Calculation Error",
            "Attendance/Assessment Record",
            "Other"
        ]

        with st.form("raise_query_form"):
            col1, col2 = st.columns(2)
            with col1:
                selected_sub_label = st.selectbox("Course Subject:", list(sub_options.keys()))
            with col2:
                selected_category = st.selectbox("Discrepancy Category:", categories)

            description = st.text_area(
                "Detailed Description & Grounds for Query:",
                placeholder="Explain the specific issue (e.g. 'My Quiz 2 score was 14/15 on physical paper but recorded as 4/15 on portal. Attached assignment proof with class representative.'). Minimum 10 characters.",
                height=120
            )

            submit_btn = st.form_submit_button("Submit Discrepancy Query", type="primary")

            if submit_btn:
                try:
                    subject_id = sub_options[selected_sub_label]
                    query_id = query_service.submit_query(
                        student_user_id=user["id"],
                        subject_id=subject_id,
                        category=selected_category,
                        description=description
                    )
                    st.success(f"✅ Query submitted successfully! (Reference ID: #{query_id}). Status is now 'Submitted'.")
                    st.rerun()
                except (ValueError, PermissionError) as e:
                    st.error(f"Error submitting query: {e}")

    # TAB 2: Query History
    with tab_history:
        st.markdown("### 📋 Your Query Records")
        queries = query_service.get_student_queries(user["id"])

        if not queries:
            st.info("You have not submitted any discrepancy queries yet.")
        else:
            for q in queries:
                status_badge = render_status_badge(q["status"])
                faculty_resp_html = ""
                if q["faculty_response"]:
                    faculty_resp_html = f"""
                        <div style="background: #F8FAFC; border-left: 3px solid #0D9488; padding: 0.75rem 1rem; border-radius: 4px; margin-top: 0.75rem;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #0D9488;">
                                Faculty Response ({q.get('faculty_name') or 'Course Instructor'}):
                            </div>
                            <div style="font-size: 0.875rem; color: #1E293B; margin-top: 0.25rem;">
                                {q['faculty_response']}
                            </div>
                        </div>
                    """

                st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: #1E3A8A; font-size: 1rem;">
                                    Query #{q['id']}: {q['subject_code']} – {q['subject_name']}
                                </span>
                                <span style="font-size: 0.8rem; color: #64748B; margin-left: 0.5rem;">
                                    ({q['category']})
                                </span>
                            </div>
                            <div>{status_badge}</div>
                        </div>
                        <div style="font-size: 0.9rem; color: #334155; margin-top: 0.65rem;">
                            <b>Student Description:</b> {q['description']}
                        </div>
                        <div style="font-size: 0.775rem; color: #94A3B8; margin-top: 0.4rem;">
                            Submitted: {q['created_at']} | Last Updated: {q['updated_at']}
                        </div>
                        {faculty_resp_html}
                    </div>
                """, unsafe_allow_html=True)
