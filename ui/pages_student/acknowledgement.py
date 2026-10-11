"""
Student Dashboard: Result Acknowledgement Page
Allows students to confirm having viewed their published results without waiving discrepancy rights.
"""
import streamlit as st
import pandas as pd
from ui.components import render_page_header
from services.result_service import ResultService


def render_student_acknowledgement(user: dict) -> None:
    """Renders the result viewing confirmation workflow."""
    render_page_header(
        title="Result Viewing & Acknowledgement ✍️",
        subtitle=f"Student USN: {user.get('usn', 'N/A')} | Official Result Confirmation"
    )

    result_service = ResultService()
    results = result_service.get_student_results(user["id"])

    # Legal / Institutional Safeguard Notice
    st.markdown("""
        <div class="alert-box">
            <b>Important Institutional Safeguard:</b> Acknowledging a result confirms that you have formally inspected 
            your published internal and external scores. <b>Confirming receipt does NOT waive or compromise your right 
            to submit an evaluation query, request answer script re-totaling, or seek faculty review.</b>
        </div>
    """, unsafe_allow_html=True)

    if not results:
        st.info("No published academic results available to acknowledge.")
        return

    # Filter by semester
    sems = sorted(list({r["semester"] for r in results}), reverse=True)
    sel_sem = st.selectbox("Select Semester:", sems)
    sem_results = [r for r in results if r["semester"] == sel_sem]

    unacknowledged = [r for r in sem_results if not r.get("ack_id")]
    acknowledged = [r for r in sem_results if r.get("ack_id")]

    st.markdown(f"### ⏳ Pending Acknowledgements ({len(unacknowledged)})")
    if not unacknowledged:
        st.success("All published course results for this semester have been acknowledged.")
    else:
        for r in unacknowledged:
            with st.container():
                st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem;">
                        <div style="font-weight: 700; color: #1E3A8A; font-size: 1.05rem;">
                            {r['subject_code']} – {r['subject_name']}
                        </div>
                        <div style="font-size: 0.875rem; color: #475569; margin-top: 0.35rem;">
                            CIE: <b>{r['internal_marks']}/40</b> | SEE: <b>{r['external_marks']}/60</b> | Total: <b>{r['total_marks']}/100</b> | Grade: <b>{r['grade']}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_btn, col_txt = st.columns([1, 3])
                with col_txt:
                    comments = st.text_input(
                        f"Comments / Observations for {r['subject_code']} (Optional):",
                        key=f"ack_comm_{r['id']}",
                        placeholder="e.g. Verified CIE components and practical marks."
                    )
                with col_btn:
                    st.write("") # spacing
                    if st.button(f"Acknowledge {r['subject_code']}", key=f"btn_ack_{r['id']}", type="primary"):
                        result_service.acknowledge_result(
                            student_user_id=user["id"],
                            result_id=r["id"],
                            comments=comments
                        )
                        st.success(f"Result for {r['subject_code']} acknowledged.")
                        st.rerun()

    if acknowledged:
        st.markdown("---")
        st.markdown(f"### ✅ Confirmed Acknowledgements ({len(acknowledged)})")
        ack_table = []
        for a in acknowledged:
            ack_table.append({
                "Course": f"{a['subject_code']} - {a['subject_name']}",
                "Total Marks": a["total_marks"],
                "Grade": a["grade"],
                "Confirmed At": a["acknowledged_at"],
            })
        st.dataframe(pd.DataFrame(ack_table), use_container_width=True, hide_index=True)
