"""
Student Dashboard: Academic Improvement Plan Page
Interactive interface for generating grounded, evidence-based recommendations,
tracking study schedules, logging practice sessions, and receiving faculty mentorship.
"""
import json
from datetime import date
import streamlit as st
import pandas as pd
from ui.components import render_page_header, render_status_badge
from services.improvement_service import ImprovementService
from repositories.improvement_repository import ImprovementRepository
from repositories.subject_repository import SubjectRepository
from repositories.result_repository import ResultRepository


def render_student_improvement_plan(user: dict) -> None:
    """Renders the student academic improvement roadmap and practice tracking."""
    render_page_header(
        title="Academic Improvement Engine 🎯",
        subtitle=f"Personalized study roadmap for {user.get('full_name')} ({user.get('usn')})"
    )

    improvement_service = ImprovementService()
    improvement_repo = ImprovementRepository()
    subject_repo = SubjectRepository()
    result_repo = ResultRepository()

    student_id = user.get("student_id")
    if not student_id:
        st.error("Student profile could not be identified.")
        return

    # Check existing plans
    existing_plans = improvement_repo.get_student_plans(student_id)

    # Top Controls: Plan Generator / Selector
    col_sel, col_gen = st.columns([2, 1])
    with col_sel:
        target_sgpa = st.slider("Set Target SGPA Goal:", min_value=7.0, max_value=10.0, value=8.5, step=0.1)

    with col_gen:
        st.write("") # spacing
        st.write("")
        if st.button("🚀 Generate / Refresh My Plan", use_container_width=True, type="primary"):
            with st.spinner("Analyzing performance records and evidence..."):
                new_plan = improvement_service.generate_and_save_plan(user["id"], target_sgpa=target_sgpa)
                st.success(f"Academic plan created! Plan ID #{new_plan['plan_id']}")
                st.rerun()

    # If no plans exist yet
    if not existing_plans:
        st.info("You don't have an active academic improvement plan yet. Click 'Generate / Refresh My Plan' above to build one based on your current grades and quiz evidence.")
        return

    current_plan = existing_plans[0]
    recs = json.loads(current_plan["recommendations_json"])
    schedule = json.loads(current_plan["weekly_schedule_json"])

    # Faculty Mentorship Feedback Banner (if reviewed)
    if current_plan.get("faculty_feedback"):
        st.markdown(f"""
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem;">
                <div style="font-weight: 700; color: #166534; font-size: 1rem;">
                    👨‍🏫 Faculty Mentor Feedback ({current_plan.get('faculty_reviewer_name') or 'Department Mentor'}):
                </div>
                <div style="color: #14532D; font-size: 0.925rem; margin-top: 0.35rem;">
                    "{current_plan['faculty_feedback']}"
                </div>
            </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📌 Grounded Recommendations", "📅 Weekly Action Schedule", "✍️ Practice Log & Self-Assessment"])

    # TAB 1: Structured Recommendations
    with tab1:
        st.markdown("### 📋 Evidence-Based Academic Recommendations")
        if not recs:
            st.success("🎉 Excellent standing! You have cleared all course criteria above the benchmark. Keep up the high standard!")
        else:
            for r in recs:
                badge_html = render_status_badge(r["priority"])
                st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; font-size: 1.05rem; color: #1E3A8A;">
                                {r['subject_code']} – {r['subject_name']}
                            </span>
                            <div>{badge_html}</div>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.2rem;">
                            Applied Rule: <b>{r['rule_applied']}</b>
                        </div>
                        <div style="font-size: 0.9rem; color: #334155; margin-top: 0.6rem;">
                            <b>Rationale:</b> {r['reason']}
                        </div>
                        <div style="font-size: 0.875rem; background: #F8FAFC; border-left: 3px solid #3B82F6; padding: 0.5rem 0.75rem; margin-top: 0.5rem; color: #1E293B;">
                            <b>Evidence:</b> {r['evidence']}
                        </div>
                        <div style="font-size: 0.9rem; color: #0D9488; margin-top: 0.6rem;">
                            <b>Suggested Action:</b> {r['suggested_action']}
                        </div>
                        <div style="font-size: 0.85rem; color: #475569; margin-top: 0.4rem;">
                            <b>Follow-up Measurement:</b> {r['follow_up_measurement']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Show topic-level assessment evidence if present
                if r.get("topic_evidence"):
                    with st.expander(f"🔬 Detailed Quiz/Assessment Evidence for {r['subject_code']}"):
                        t_df = pd.DataFrame(r["topic_evidence"])
                        st.dataframe(t_df, use_container_width=True, hide_index=True)

    # TAB 2: Weekly Schedule
    with tab2:
        st.markdown("### 🗓️ Realistic Weekly Study Roadmap")
        st.caption("Structured, manageable allocation designed to build mastery without overwhelm.")
        
        sch_df = pd.DataFrame(schedule)
        sch_df.columns = ["Day", "Study Focus", "Duration (Minutes)", "Target Goal"]
        st.dataframe(sch_df, use_container_width=True, hide_index=True)

    # TAB 3: Practice Log & Progress Tracker
    with tab3:
        st.markdown("### 📝 Record Self-Directed Practice Session")
        st.caption("Log problem-solving sessions, past-paper drills, or lab rehearsals to record measurable progress.")

        # Load enrolled subjects
        subjects = subject_repo.list_subjects(semester=user.get("semester", 5))
        sub_map = {f"{s['code']} - {s['name']}": s["id"] for s in subjects}

        with st.form("log_practice_form"):
            c_sub, c_date = st.columns([2, 1])
            with c_sub:
                selected_sub_label = st.selectbox("Course Subject:", list(sub_map.keys()))
            with c_date:
                log_date = st.date_input("Date Completed:", value=date.today())

            c_act, c_dur, c_sc = st.columns([2, 1, 1])
            with c_act:
                activity_desc = st.text_input("Activity Description:", placeholder="e.g. Solved 10 Decidability problems / Timed quiz")
            with c_dur:
                duration_mins = st.number_input("Duration (Mins):", min_value=15, max_value=240, value=60, step=15)
            with c_sc:
                self_score = st.number_input("Self-Score % (Optional):", min_value=0.0, max_value=100.0, value=75.0, step=5.0)

            notes = st.text_area("Personal Reflections & Doubts to Clarify:", placeholder="Identified confusion in reduction technique; scheduled office hours.")

            submit_log = st.form_submit_button("Record Practice Session", type="primary")

            if submit_log:
                if not activity_desc:
                    st.error("Please enter an activity description.")
                else:
                    improvement_service.log_student_practice(
                        student_user_id=user["id"],
                        plan_id=current_plan["id"],
                        subject_id=sub_map[selected_sub_label],
                        date_completed=str(log_date),
                        practice_activity=activity_desc,
                        duration_minutes=int(duration_mins),
                        self_assessment_score=float(self_score),
                        notes=notes
                    )
                    st.success("✅ Practice session logged successfully!")
                    st.rerun()

        # Display historical practice logs
        st.markdown("#### 📜 Your Practice Session History")
        logs = improvement_repo.get_practice_logs(student_id=student_id, plan_id=current_plan["id"])
        if not logs:
            st.info("No practice sessions logged yet. Record your first practice session above!")
        else:
            log_table = []
            for l in logs:
                log_table.append({
                    "Date": l["date_completed"],
                    "Course": f"{l['subject_code']} - {l['subject_name']}",
                    "Activity": l["practice_activity"],
                    "Duration": f"{l['duration_minutes']} mins",
                    "Self Score": f"{l['self_assessment_score']}%" if l["self_assessment_score"] is not None else "N/A",
                    "Notes": l.get("notes") or ""
                })
            st.dataframe(pd.DataFrame(log_table), use_container_width=True, hide_index=True)
