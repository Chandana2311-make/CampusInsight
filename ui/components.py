"""
Reusable UI Components for CampusInsight
Standardized header banners, KPI metric cards, badge indicators, branding logos, and logout controls.
"""
from pathlib import Path
from typing import Optional
import streamlit as st
from config import BASE_DIR, DEMO_CREDENTIALS

PNG_LOGO_PATH = BASE_DIR / "assets" / "campusinsight_logo.png"
PNG_SIDEBAR_LOGO_PATH = BASE_DIR / "assets" / "campusinsight_sidebar_logo.png"
SVG_LOGO_PATH = BASE_DIR / "assets" / "campusinsight_logo.svg"


def render_logo(width: int = 360, dark_theme: bool = False, in_sidebar: bool = False) -> None:
    """
    Renders the official CampusInsight logo using st.image().
    Guarantees that raw SVG source code, tags, or attributes are NEVER displayed in the UI.
    Maintains proper aspect ratio with graceful fallback.
    """
    target = st.sidebar if in_sidebar else st
    logo_file = PNG_SIDEBAR_LOGO_PATH if (dark_theme and PNG_SIDEBAR_LOGO_PATH.exists()) else PNG_LOGO_PATH

    if logo_file.exists():
        target.image(str(logo_file), width=width)
    elif SVG_LOGO_PATH.exists():
        target.image(str(SVG_LOGO_PATH), width=width)
    else:
        # Clean text-based fallback: strictly never raw markup
        brand_color = "#38BDF8" if dark_theme else "#111827"
        target.markdown(
            f'<div style="text-align: center; font-weight: 800; font-size: 1.5rem; color: {brand_color}; padding: 0.5rem 0;">'
            f'🎓 CampusInsight'
            f'</div>',
            unsafe_allow_html=True
        )


def render_sidebar_logo() -> None:
    """Renders the official logo at the top of the sidebar with correct sizing and contrast."""
    render_logo(width=220, dark_theme=True, in_sidebar=True)


def render_page_header(title: str, subtitle: str) -> None:
    """Renders a modern gradient banner at the top of a page with brand accent."""
    st.markdown(f"""
        <div class="page-header">
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: Optional[str] = None) -> None:
    """Renders a polished KPI metric card."""
    sub_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Returns an HTML badge for a status."""
    s_lower = str(status).lower()
    if s_lower in ("pass", "cleared", "resolved", "active"):
        css_class = "badge-pass"
    elif s_lower in ("fail", "rejected", "critical", "high"):
        css_class = "badge-fail"
    elif s_lower in ("under review", "in progress", "pending"):
        css_class = "badge-pending"
    else:
        css_class = "badge-info"
    return f'<span class="badge {css_class}">{status}</span>'


def render_sidebar_profile(user: dict) -> None:
    """Renders the authenticated user's card in the Streamlit sidebar."""
    role_title = user.get("role", "User").upper()
    full_name = user.get("full_name", "Anonymous")
    username = user.get("username", "")
    
    extra_info = ""
    if user.get("role") == "student":
        extra_info = f"<div style='font-size: 0.75rem; color: #94A3B8;'>USN: {user.get('usn', 'N/A')} | Sem {user.get('semester', '-')}{user.get('section', '')}</div>"
    elif user.get("role") == "faculty":
        extra_info = f"<div style='font-size: 0.75rem; color: #94A3B8;'>Dept: Computer Science & Engg</div>"

    st.sidebar.markdown(f"""
        <div class="sidebar-profile">
            <div class="sidebar-profile-role">{role_title} SESSION</div>
            <div class="sidebar-profile-name">{full_name}</div>
            <div style="font-size: 0.8rem; color: #CBD5E1;">@{username}</div>
            {extra_info}
        </div>
    """, unsafe_allow_html=True)


def render_logout_button() -> None:
    """
    Renders the solid dark navy/black (#111827), high-contrast, rounded logout button.
    Ensures clear visibility and immediate session termination across student and faculty views.
    """
    st.sidebar.markdown('<div class="logout-container">', unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
