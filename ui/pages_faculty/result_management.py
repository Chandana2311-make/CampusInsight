"""
Faculty Dashboard: Result Management Page
Handles CSV mark upload, validation error preview, batch import, individual mark corrections
with mandatory justification reasons, audit trail logging, and explicit publish/unpublish toggling.
"""
from pathlib import Path
import streamlit as st
import pandas as pd
from ui.components import render_page_header
from services.result_service import ResultService
from repositories.faculty_repository import FacultyRepository
from repositories.result_repository import ResultRepository
from repositories.subject_repository import SubjectRepository
from config import BASE_DIR


def render_faculty_results(user: dict) -> None:
    """Renders the comprehensive faculty mark management workstation."""
    render_page_header(
        title="Result Management & Marks Control 📊",
        subtitle=f"Authorized Faculty: {user.get('full_name')} | Grade Evaluation & Publishing Engine"
    )

    faculty_repo = FacultyRepository()
    result_service = ResultService()
    result_repo = ResultRepository()
    subject_repo = SubjectRepository()

    # Load subjects assigned to this faculty member
    assignments = faculty_repo.get_assigned_subjects(user["id"])
    if not assignments:
        st.warning("No courses assigned to your account.")
        return

    # Subject and Semester selector
    unique_subjects = {f"{a['code']} - {a['name']} (Sem {a['semester']})": a for a in assignments}
    selected_label = st.selectbox("Select Course for Marks Management:", list(unique_subjects.keys()))
    selected_course = unique_subjects[selected_label]
    subject_id = selected_course["subject_id"]
    semester = selected_course["semester"]

    # Security check: verify authorization explicitly
    if not faculty_repo.is_faculty_assigned(user["id"], subject_id, semester=semester):
        st.error("Unauthorized: You do not have permissions for this course.")
        return

    tab1, tab2, tab3 = st.tabs([
        "📋 Student Marks Roster & Correction",
        "📤 CSV Batch Upload & Error Validation",
        "🚀 Explicit Publication Control"
    ])

    # -------------------------------------------------------------
    # TAB 1: Student Marks Roster & Individual Mark Correction
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 📝 Course Marks Roster")
        st.caption("View student marks, clearance status, and make individual corrections with mandatory audit justification.")

        results = result_repo.get_subject_results(subject_id=subject_id, semester=semester)

        if not results:
            st.info("No mark records found for this course. Use the 'CSV Batch Upload' tab to import student scores.")
        else:
            table_data = []
            for r in results:
                pub_badge = "🟢 Published" if r["is_published"] == 1 else "🟡 Unpublished"
                table_data.append({
                    "Result ID": r["id"],
                    "USN": r["usn"],
                    "Student Name": r["student_name"],
                    "Sec": r["section"],
                    "CIE (40)": r["internal_marks"] if r["internal_marks"] is not None else "AB",
                    "SEE (60)": r["external_marks"] if r["external_marks"] is not None else "AB",
                    "Total (100)": r["total_marks"] if r["total_marks"] is not None else 0,
                    "Grade": r["grade"],
                    "Grade Pts": r["grade_points"],
                    "Status": "PASS" if r["is_passed"] == 1 else "FAIL",
                    "Publication": pub_badge
                })

            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            # Mark Edit Form (with mandatory reason!)
            st.markdown("---")
            st.markdown("#### ✏️ Single Student Mark Amendment (Audit Logged)")
            st.caption("Any mark change requires a formal justification reason and is permanently recorded in the audit trail.")

            student_options = {f"{r['usn']} - {r['student_name']} (Result #{r['id']})": r for r in results}
            selected_student_label = st.selectbox("Select Student to Amend:", list(student_options.keys()))
            student_result = student_options[selected_student_label]

            with st.form("amend_mark_form"):
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    new_internal = st.number_input(
                        "Internal CIE (0 to 40):",
                        min_value=0.0,
                        max_value=float(selected_course["max_internal"]),
                        value=float(student_result["internal_marks"] or 0.0),
                        step=0.5
                    )
                with col_m2:
                    new_external = st.number_input(
                        "External SEE (0 to 60):",
                        min_value=0.0,
                        max_value=float(selected_course["max_external"]),
                        value=float(student_result["external_marks"] or 0.0),
                        step=0.5
                    )
                with col_m3:
                    is_absent = st.checkbox("Mark as Absent (AB)", value=bool(student_result["is_absent"]))

                reason = st.text_input(
                    "Mandatory Justification Reason (Required):",
                    placeholder="e.g. Rectified calculation error in question 3 of CIE 2 answer script."
                )

                submit_amend = st.form_submit_button("Save Correction & Log Audit Event", type="primary")

                if submit_amend:
                    try:
                        eval_out = result_service.update_result_mark(
                            faculty_user_id=user["id"],
                            result_id=student_result["id"],
                            internal_marks=new_internal if not is_absent else 0.0,
                            external_marks=new_external if not is_absent else 0.0,
                            reason=reason,
                            is_absent=is_absent
                        )
                        st.success(f"✅ Marks updated successfully! New Grade: {eval_out['grade']} ({eval_out['status_label']}). Audit entry created.")
                        st.rerun()
                    except (ValueError, PermissionError) as e:
                        st.error(f"Modification rejected: {e}")

    # -------------------------------------------------------------
    # TAB 2: Authorized College CSV Import & Validation
    # -------------------------------------------------------------
    with tab2:
        st.markdown("### 📤 Import Authorized College Marks CSV")
        st.markdown("""
            <div class="notice-box">
                <b>Departmental Import Workflow:</b> Authorised faculty may upload official semester-end marks. 
                Imported scores are thoroughly validated against university range constraints and 
                <b>saved as UNPUBLISHED</b> so you can review them prior to releasing them to students.
            </div>
        """, unsafe_allow_html=True)

        # Template Download & College Format Guidance
        col_guide, col_tmpl = st.columns([2, 1])
        with col_guide:
            st.markdown("""
                **Supported College Column Formats:**
                - **Student ID:** `USN`, `Roll_No`, `Reg_No`, or `Student_ID`
                - **Internal Marks:** `Internal`, `CIE`, `Internal_Marks`, or `IA_Marks` (0 to 40)
                - **External Exam:** `External`, `SEE`, `External_Marks`, or `University_Marks` (0 to 60)
                - **Absentee Status:** `Is_Absent` or `Absent` (0 = Present, 1 = Absent)
            """)
        with col_tmpl:
            sample_template_csv = "USN,Internal,External,Is_Absent\n1CI22CS101,36,52,0\n1CI22CS102,38,54,0\n1CI22CS103,28,40,0\n"
            st.download_button(
                label="📥 Download Blank CSV Template",
                data=sample_template_csv,
                file_name="campusinsight_marks_template.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        # Quick Demo File Loader Buttons
        st.markdown("##### 🧪 Quick Evaluation Samples:")
        c_v, c_iv = st.columns(2)
        valid_sample_path = BASE_DIR / "sample_data" / "valid_marks_upload.csv"
        invalid_sample_path = BASE_DIR / "sample_data" / "invalid_marks_sample.csv"

        use_demo_valid = False
        use_demo_invalid = False
        if c_v.button("📄 Load Sample Valid CSV (Synthetic)"):
            use_demo_valid = True
        if c_iv.button("⚠️ Load Sample Invalid CSV (Show Diagnostics)"):
            use_demo_invalid = True

        uploaded_file = st.file_uploader(
            "Upload College's Authorized Marks CSV File:",
            type=["csv"],
            help="Select your department's authorized CSV mark sheet"
        )

        raw_csv_content = None
        if uploaded_file is not None:
            raw_csv_content = uploaded_file.getvalue()
        elif use_demo_valid and valid_sample_path.exists():
            with open(valid_sample_path, "rb") as f:
                raw_csv_content = f.read()
            st.info("Loaded sample valid marks from `sample_data/valid_marks_upload.csv`")
        elif use_demo_invalid and invalid_sample_path.exists():
            with open(invalid_sample_path, "rb") as f:
                raw_csv_content = f.read()
            st.warning("Loaded sample invalid marks from `sample_data/invalid_marks_sample.csv` to showcase error diagnostics.")

        if raw_csv_content:
            valid_rows, error_rows = result_service.validate_csv_content(
                csv_text_or_bytes=raw_csv_content,
                subject_id=subject_id,
                semester=semester
            )

            col_val_summary, col_err_summary = st.columns(2)
            with col_val_summary:
                st.metric("Validated Valid Records", len(valid_rows))
            with col_err_summary:
                st.metric("Flagged Validation Errors", len(error_rows))

            # Display Errors Preview if any exist
            if error_rows:
                st.error("🚨 Validation Errors Detected in CSV:")
                st.dataframe(pd.DataFrame(error_rows), use_container_width=True, hide_index=True)

            # Display Valid Rows Preview
            if valid_rows:
                st.success("✅ Valid Rows Ready for Import:")
                preview_df = pd.DataFrame(valid_rows)[["usn", "student_name", "internal_marks", "external_marks", "total_marks", "grade", "is_passed"]]
                st.dataframe(preview_df, use_container_width=True, hide_index=True)

                if st.button(f"📥 Import {len(valid_rows)} Valid Rows into Database", type="primary"):
                    imported_count = result_service.import_marks(
                        faculty_user_id=user["id"],
                        subject_id=subject_id,
                        semester=semester,
                        valid_rows=valid_rows
                    )
                    st.success(f"🎉 Successfully imported {imported_count} marks! Results remain UNPUBLISHED until you explicitly publish them.")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 3: Explicit Publication Control
    # -------------------------------------------------------------
    with tab3:
        st.markdown("### 🚀 Explicit Result Publication Control")
        st.caption("Control student portal visibility. Results are never automatically published after CSV import.")

        current_subject_results = result_repo.get_subject_results(subject_id=subject_id, semester=semester)
        pub_count = sum(1 for r in current_subject_results if r["is_published"] == 1)
        unpub_count = len(current_subject_results) - pub_count

        cp1, cp2 = st.columns(2)
        with cp1:
            st.metric("Currently Published Records", pub_count)
        with cp2:
            st.metric("Currently Unpublished Records", unpub_count)

        is_currently_published = (pub_count > 0 and unpub_count == 0)

        st.markdown("---")
        with st.form("publish_toggle_form"):
            target_action = not is_currently_published
            action_label = "PUBLISH RESULTS TO STUDENTS" if target_action else "UNPUBLISH RESULTS (WITHDRAW VISIBILITY)"
            
            st.markdown(f"#### Target Action: **{action_label}**")
            pub_reason = st.text_input(
                "Mandatory Publication Authorization Note / Reason:",
                value="Verified and approved for publication." if target_action else "Withdrawn for grade reconciliation.",
                placeholder="e.g. Departmental approval obtained; releasing SEE marks."
            )

            btn_color = "primary" if target_action else "secondary"
            submit_pub = st.form_submit_button(action_label, type=btn_color)

            if submit_pub:
                try:
                    count = result_service.set_publish_status(
                        faculty_user_id=user["id"],
                        subject_id=subject_id,
                        semester=semester,
                        publish=target_action,
                        reason=pub_reason
                    )
                    status_verb = "published" if target_action else "unpublished"
                    st.success(f"✅ Successfully {status_verb} {count} records for {selected_course['code']}. Audit event logged.")
                    st.rerun()
                except (ValueError, PermissionError) as e:
                    st.error(f"Action failed: {e}")
