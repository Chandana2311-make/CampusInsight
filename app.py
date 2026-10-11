"""
CampusInsight: Student Result Analysis & Academic Improvement System
Main Streamlit Application Entrypoint
Provides layered routing, role-based navigation, session state management, and demo access.
"""
import sys
from pathlib import Path

# Ensure application root is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from config import APP_NAME, APP_TAGLINE, VERSION, DEMO_CREDENTIALS
from database.init_db import init_database
from database.seed_data import seed_database
from services.auth_service import AuthService
from ui.styles import get_custom_css
from ui.components import (
    render_sidebar_profile,
    render_demo_notice,
    render_logo,
    render_sidebar_logo,
    render_logout_button
)

# Student Pages
from ui.pages_student.overview import render_student_overview
from ui.pages_student.my_results import render_student_results
from ui.pages_student.my_performance import render_student_performance
from ui.pages_student.improvement_plan import render_student_improvement_plan
from ui.pages_student.acknowledgement import render_student_acknowledgement
from ui.pages_student.student_queries import render_student_queries

# Faculty Pages
from ui.pages_faculty.overview import render_faculty_overview
from ui.pages_faculty.result_management import render_faculty_results
from ui.pages_faculty.subject_analytics import render_faculty_analytics
from ui.pages_faculty.academic_support import render_faculty_support
from ui.pages_faculty.faculty_queries import render_faculty_queries
from ui.pages_faculty.audit_log import render_faculty_audit_log


def init_app_state() -> None:
    """Ensures database is initialized and seeds demo data on first boot."""
    if "db_initialized" not in st.session_state:
        init_database()
        seed_database()
        st.session_state["db_initialized"] = True

    if "user" not in st.session_state:
        st.session_state["user"] = None


def render_login_view(auth_service: AuthService) -> None:
    """Renders the polished, modern, responsive CampusInsight login portal."""
    # Centered Brand Hero Header
    st.markdown('<div class="login-hero">', unsafe_allow_html=True)
    col_l_sp, col_l_center, col_r_sp = st.columns([1, 2, 1])
    with col_l_center:
        render_logo(width=360)
    
    st.markdown(
        '<div class="login-hero-tagline">Academic Performance Intelligence & Student Improvement System</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="demo-info-banner">'
        '💡 <b>Local Demonstration Mode:</b> Pre-loaded with synthetic student & faculty profiles. '
        'Authorized college marksheets can be imported directly via the <b>Result Management</b> portal.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Balanced Cards Grid on Desktop (stacks vertically on mobile)
    col_login, col_demo = st.columns([1, 1], gap="medium")

    # Column 1: Manual Secure Login
    with col_login:
        st.markdown("""
            <div class="login-card-title">🔐 Secure Account Login</div>
            <div class="login-card-subtitle">Enter your institutional credentials to access your portal.</div>
        """, unsafe_allow_html=True)
        
        with st.form("manual_login_form"):
            username = st.text_input("Username:", placeholder="e.g. dr.sharma or usn101", key="input_user")
            password = st.text_input("Password:", type="password", placeholder="Enter your password", key="input_pwd")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submit:
                user = auth_service.authenticate(username, password)
                if user:
                    st.session_state["user"] = user
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Check credentials and retry.")

    # Column 2: Quick Demo Profile Launcher
    with col_demo:
        st.markdown("""
            <div class="login-card-title">🚀 One-Click Demo Profiles</div>
            <div class="login-card-subtitle">Select a synthetic persona to instantly explore role permissions.</div>
        """, unsafe_allow_html=True)

        demo_options = {
            "Dr. Ramesh Sharma (Faculty: DBMS & TOC)": DEMO_CREDENTIALS["faculty_1"],
            "Prof. Anita Deshmukh (Faculty: Networks & SE)": DEMO_CREDENTIALS["faculty_2"],
            "Aarav Patel (Student: Top Performer)": DEMO_CREDENTIALS["student_1"],
            "Bhavya Rao (Student: High Achiever)": DEMO_CREDENTIALS["student_2"],
            "Chirag Nair (Student: Needs Subject Recovery)": DEMO_CREDENTIALS["student_3"],
        }

        selected_demo_key = st.selectbox("Choose Persona:", list(demo_options.keys()))
        selected_cred = demo_options[selected_demo_key]

        role_badge_color = "#1D4ED8" if selected_cred["role"] == "faculty" else "#0D9488"
        role_badge_bg = "#EFF6FF" if selected_cred["role"] == "faculty" else "#F0FDFA"
        scope_info = f"<b>Courses:</b> {', '.join(selected_cred['subjects'])}" if "subjects" in selected_cred else f"<b>USN:</b> {selected_cred.get('usn')} (Sem {selected_cred.get('semester')})"

        st.markdown(f"""
            <div class="demo-credential-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">{selected_cred['name']}</span>
                    <span style="background: {role_badge_bg}; color: {role_badge_color}; font-weight: 800; font-size: 0.725rem; padding: 0.2rem 0.55rem; border-radius: 9999px;">
                        {selected_cred['role'].upper()}
                    </span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; line-height: 1.5;">
                    Username: <code>{selected_cred['username']}</code> &nbsp;|&nbsp; Password: <code>{selected_cred['password']}</code><br/>
                    {scope_info}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Access as Selected Persona", key="demo_login_btn", use_container_width=True):
            user = auth_service.authenticate(selected_cred["username"], selected_cred["password"])
            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Failed to authenticate demo account.")


def main() -> None:
    st.set_page_config(
        page_title="CampusInsight | Academic Intelligence",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject SaaS CSS design tokens
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    init_app_state()
    auth_service = AuthService()

    current_user = st.session_state.get("user")

    # If unauthenticated, show login view
    if not current_user:
        render_login_view(auth_service)
        return

    # Authenticated Session: Render Sidebar Logo & Profile
    render_sidebar_logo()
    render_sidebar_profile(current_user)

    # Role-Based Sidebar Navigation
    st.sidebar.markdown("---")
    role = current_user.get("role")

    if role == "student":
        nav_options = [
            "🏠 Overview",
            "📜 My Results",
            "📊 My Performance",
            "🎯 Improvement Plan",
            "✍️ Result Acknowledgement",
            "💬 Raise & Track Queries"
        ]
        choice = st.sidebar.radio("Student Portal Navigation:", nav_options)

        if choice == "🏠 Overview":
            render_student_overview(current_user)
        elif choice == "📜 My Results":
            render_student_results(current_user)
        elif choice == "📊 My Performance":
            render_student_performance(current_user)
        elif choice == "🎯 Improvement Plan":
            render_student_improvement_plan(current_user)
        elif choice == "✍️ Result Acknowledgement":
            render_student_acknowledgement(current_user)
        elif choice == "💬 Raise & Track Queries":
            render_student_queries(current_user)

    elif role == "faculty":
        nav_options = [
            "🏠 Overview",
            "📊 Result Management",
            "📈 Subject Analytics",
            "🤝 Academic Support",
            "📥 Query Management",
            "🛡️ Audit Log"
        ]
        choice = st.sidebar.radio("Faculty Portal Navigation:", nav_options)

        if choice == "🏠 Overview":
            render_faculty_overview(current_user)
        elif choice == "📊 Result Management":
            render_faculty_results(current_user)
        elif choice == "📈 Subject Analytics":
            render_faculty_analytics(current_user)
        elif choice == "🤝 Academic Support":
            render_faculty_support(current_user)
        elif choice == "📥 Query Management":
            render_faculty_queries(current_user)
        elif choice == "🛡️ Audit Log":
            render_faculty_audit_log(current_user)

    # Sidebar Logout Button (Requirement B)
    render_logout_button()


if __name__ == "__main__":
    main()
