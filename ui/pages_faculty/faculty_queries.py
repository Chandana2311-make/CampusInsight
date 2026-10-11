"""
Faculty Dashboard: Query Management Page
Allows authorized faculty to review and resolve result discrepancy queries raised by students.
Implements the formal lifecycle: Submitted -> Under Review -> Resolved or Rejected.
"""
import streamlit as st
from ui.components import render_page_header, render_status_badge
from services.query_service import QueryService
from repositories.faculty_repository import FacultyRepository


def render_faculty_queries(user: dict) -> None:
    """Renders the query review and resolution workstation."""
    render_page_header(
        title="Student Discrepancy Query Inbox 📥",
        subtitle=f"Formal Academic Resolutions | Faculty: {user.get('full_name')}"
    )

    query_service = QueryService()
    faculty_repo = FacultyRepository()

    # Filter by status
    status_filter = st.selectbox(
        "Filter by Lifecycle Status:",
        ["All Queries", "Submitted", "Under Review", "Resolved", "Rejected"]
    )
    filter_val = None if status_filter == "All Queries" else status_filter

    queries = query_service.get_faculty_queries(user["id"], status=filter_val)

    if not queries:
        st.info(f"No queries found matching the status filter '{status_filter}'.")
        return

    st.markdown(f"### 📋 Actionable Queries ({len(queries)})")

    for q in queries:
        status_badge = render_status_badge(q["status"])

        with st.expander(f"Query #{q['id']}: [{q['subject_code']}] {q['student_name']} ({q['usn']}) – {q['category']} [{q['status']}]"):
            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 700; color: #1E3A8A;">Student: {q['student_name']} ({q['usn']})</span>
                        <div>{status_badge}</div>
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 0.35rem;">
                        <b>Course:</b> {q['subject_code']} - {q['subject_name']} | <b>Section:</b> {q['section']}
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 0.2rem;">
                        <b>Category:</b> {q['category']} | <b>Submitted:</b> {q['created_at']}
                    </div>
                    <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 0.5rem 0;" />
                    <div style="font-size: 0.9rem; color: #0F172A;">
                        <b>Student Description:</b> {q['description']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if q.get("faculty_response"):
                st.info(f"**Current Response:** {q['faculty_response']} *(Reviewed by {q.get('reviewer_name') or 'Faculty'})*")

            # Resolution Form
            with st.form(f"resolve_form_{q['id']}"):
                st.markdown("##### ✍️ Update Status & Respond:")
                
                status_options = ["Under Review", "Resolved", "Rejected"]
                curr_idx = status_options.index(q["status"]) if q["status"] in status_options else 0
                new_status = st.selectbox("New Lifecycle Status:", status_options, index=curr_idx)

                response_text = st.text_area(
                    "Faculty Response / Resolution Details (Required for Resolve/Reject):",
                    value=q.get("faculty_response") or "",
                    placeholder="e.g. Script re-evaluated. Internal marks verified as 38/40. No grade discrepancy found.",
                    height=90
                )

                submit_btn = st.form_submit_button("Submit Formal Resolution", type="primary")

                if submit_btn:
                    try:
                        query_service.update_query_status(
                            faculty_user_id=user["id"],
                            query_id=q["id"],
                            new_status=new_status,
                            faculty_response=response_text
                        )
                        st.success(f"✅ Query #{q['id']} status updated to '{new_status}'. Audit log created.")
                        st.rerun()
                    except (ValueError, PermissionError) as e:
                        st.error(f"Failed to update query: {e}")
