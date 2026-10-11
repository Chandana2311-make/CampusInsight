"""
UI Styling and CSS Design Tokens
Professional education SaaS theme featuring deep navy, vibrant teal, and clean modern card components.
"""

def get_custom_css() -> str:
    """Returns CSS styles for Streamlit application."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
    }

    /* Main Container - Centered, no horizontal overflow */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 1180px;
        margin: 0 auto;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }

    /* Center images in their columns */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stImage"] > img {
        object-fit: contain;
    }

    /* Login Page Layout & Hero */
    .login-hero {
        text-align: center;
        margin-bottom: 1.25rem;
    }

    .login-hero-tagline {
        color: #0D9488;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.25rem;
        margin-bottom: 0.75rem;
    }

    .demo-info-banner {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #0D9488;
        border-radius: 8px;
        padding: 0.65rem 1rem;
        color: #14532D;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        line-height: 1.45;
        text-align: left;
    }

    /* Balanced Login Cards */
    .login-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    .login-card-title {
        color: #111827;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .login-card-subtitle {
        color: #64748B;
        font-size: 0.825rem;
        margin-bottom: 1rem;
    }

    .demo-credential-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1.25rem;
        font-size: 0.85rem;
        color: #334155;
    }

    /* Primary Buttons - Solid Navy with White Text */
    button[kind="primary"],
    div.stButton > button[kind="primary"] {
        background: #111827 !important;
        background-color: #111827 !important;
        border: 1px solid #111827 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.925rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.25rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }

    button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover {
        background: #1F2937 !important;
        background-color: #1F2937 !important;
        border-color: #1F2937 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
    }

    button[kind="primary"] * {
        color: #FFFFFF !important;
    }

    /* High-Contrast Demo Login Button */
    div.st-key-demo_login_btn > button {
        background: #0D9488 !important;
        background-color: #0D9488 !important;
        border: 1px solid #0F766E !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.925rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.25rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 1px 3px rgba(13, 148, 136, 0.3) !important;
    }

    div.st-key-demo_login_btn > button:hover {
        background: #0F766E !important;
        background-color: #0F766E !important;
        border-color: #115E59 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    div.st-key-demo_login_btn > button * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.85rem;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -3px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }

    .metric-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.2;
    }

    .metric-subtitle {
        font-size: 0.775rem;
        color: #0D9488;
        font-weight: 600;
        margin-top: 0.3rem;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .badge-pass {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }

    .badge-fail {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }

    .badge-pending {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    .badge-info {
        background-color: #E0F2FE;
        color: #0369A1;
        border: 1px solid #BAE6FD;
    }

    /* Page Header Banner */
    .page-header {
        background: linear-gradient(135deg, #111827 0%, #1E3A8A 50%, #0D9488 100%);
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(17, 24, 39, 0.2);
    }

    .page-header h1 {
        color: #FFFFFF !important;
        font-size: 1.65rem;
        font-weight: 800;
        margin: 0;
    }

    .page-header p {
        color: #E0E7FF !important;
        font-size: 0.9rem;
        margin: 0.35rem 0 0 0;
    }

    /* User Profile Card in Sidebar */
    .sidebar-profile {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-profile-name {
        font-weight: 700;
        font-size: 0.925rem;
        color: #FFFFFF !important;
    }

    .sidebar-profile-role {
        font-size: 0.725rem;
        color: #2DD4BF !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    /* Notice Boxes */
    .notice-box {
        border-left: 4px solid #0D9488;
        background-color: #F0FDFA;
        padding: 0.85rem 1.15rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.875rem;
        color: #134E4A;
        margin-bottom: 1rem;
    }

    .alert-box {
        border-left: 4px solid #F59E0B;
        background-color: #FFFBEB;
        padding: 0.85rem 1.15rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.875rem;
        color: #78350F;
        margin-bottom: 1rem;
    }

    /* Clean Streamlit Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ============================================================
       SPECIALIZED LOGOUT BUTTON (Requirement 4)
       Solid dark navy (#111827), white text (#FFFFFF), 
       visible border (#374151), rounded corners (8px), 
       hover state (#1F2937), high contrast.
       ============================================================ */
    .logout-container {
        margin-top: 1.5rem;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .logout-container button,
    div.st-key-logout_btn button,
    div[data-testid="stSidebar"] div.st-key-logout_btn button {
        background-color: #111827 !important;
        background: #111827 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #374151 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.925rem !important;
        padding: 0.6rem 1.25rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        cursor: pointer !important;
    }

    .logout-container button:hover,
    div.st-key-logout_btn button:hover,
    div[data-testid="stSidebar"] div.st-key-logout_btn button:hover {
        background-color: #1F2937 !important;
        background: #1F2937 !important;
        color: #FFFFFF !important;
        border-color: #4B5563 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.6) !important;
        transform: translateY(-1px);
    }

    .logout-container button:active,
    div.st-key-logout_btn button:active,
    div[data-testid="stSidebar"] div.st-key-logout_btn button:active {
        background-color: #030712 !important;
        background: #030712 !important;
        color: #F9FAFB !important;
        border-color: #6B7280 !important;
    }

    .logout-container button p,
    .logout-container button span,
    div.st-key-logout_btn button p,
    div.st-key-logout_btn button span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    </style>
    """
