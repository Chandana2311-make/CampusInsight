"""
Faculty Dashboard: Audit Log Page
Provides full visibility into the system audit trail, including mark amendments,
publication events, and query resolutions with timestamps and actor tracking.
"""
import streamlit as st
import pandas as pd
from ui.components import render_page_header
from repositories.audit_repository import AuditRepository


def render_faculty_audit_log(user: dict) -> None:
    """Renders the institutional audit trail table."""
    render_page_header(
        title="Institutional Audit Trail 🛡️",
        subtitle="Immutable Activity Log of Marks Amendments, CSV Imports, and Publication Events"
    )

    audit_repo = AuditRepository()

    # Filter controls
    col_act, col_ent = st.columns(2)
    with col_act:
        action_filter = st.selectbox(
            "Filter by Action:",
            ["ALL", "UPDATE_STUDENT_MARKS", "PUBLISH_RESULTS", "UNPUBLISH_RESULTS", "IMPORT_MARKS_CSV", "UPDATE_QUERY_STATUS"]
        )
    with col_ent:
        entity_filter = st.selectbox(
            "Filter by Entity Type:",
            ["ALL", "result", "subject", "query"]
        )

    action_val = None if action_filter == "ALL" else action_filter
    entity_val = None if entity_filter == "ALL" else entity_filter

    events = audit_repo.list_events(entity_type=entity_val, limit=300)
    if action_val:
        events = [e for e in events if e["action"] == action_val]

    if not events:
        st.info("No audit events found matching the selected filters.")
        return

    st.markdown(f"### 📋 Audit Events Record ({len(events)})")

    table_data = []
    for e in events:
        table_data.append({
            "Timestamp": e["timestamp"],
            "Actor": f"{e['actor_name']} (@{e['actor_username']})",
            "Action": e["action"],
            "Entity": f"{e['entity_type']} #{e['entity_id']}",
            "Prior Value": e["old_value"] or "—",
            "Updated Value": e["new_value"] or "—",
            "Mandatory Justification Reason": e["reason"]
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
