"""
Plotly Chart Builders for CampusInsight
Generates responsive, accessible, interactive visualizations styled with Navy & Teal SaaS themes.
"""
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import THEME_COLORS


def build_grade_distribution_chart(grade_counts: Dict[str, int]) -> go.Figure:
    """Creates a stylized bar chart showing student counts across letter grades."""
    df = pd.DataFrame(list(grade_counts.items()), columns=["Grade", "Count"])
    
    # Custom color per grade
    color_map = {
        "O": "#0D9488",   # Teal
        "A+": "#14B8A6",  # Light Teal
        "A": "#3B82F6",   # Royal Blue
        "B+": "#60A5FA",  # Light Blue
        "B": "#93C5FD",   # Soft Blue
        "C": "#FBBF24",   # Amber
        "P": "#F59E0B",   # Dark Amber
        "F": "#EF4444",   # Crimson Red
        "PENDING": "#94A3B8"
    }
    colors = [color_map.get(g, "#64748B") for g in df["Grade"]]

    fig = go.Figure(data=[
        go.Bar(
            x=df["Grade"],
            y=df["Count"],
            marker_color=colors,
            text=df["Count"],
            textposition="outside",
            hoverinfo="x+y"
        )
    ])

    fig.update_layout(
        title="<b>Grade Distribution</b>",
        xaxis_title="Letter Grade",
        yaxis_title="Number of Students",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    return fig


def build_internal_vs_external_scatter(results: List[dict]) -> go.Figure:
    """Creates an interactive scatter plot comparing Continuous Internal Evaluation (CIE) vs Semester End Exam (SEE)."""
    df = pd.DataFrame(results)
    if df.empty or "internal_marks" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No evaluation data available")
        return fig

    # Filter out records without valid numeric marks
    df = df.dropna(subset=["internal_marks", "external_marks"])

    fig = px.scatter(
        df,
        x="internal_marks",
        y="external_marks",
        color="grade",
        hover_data=["usn", "student_name", "total_marks"],
        color_discrete_map={
            "O": "#0D9488",
            "A+": "#14B8A6",
            "A": "#3B82F6",
            "B+": "#60A5FA",
            "B": "#93C5FD",
            "C": "#FBBF24",
            "P": "#F59E0B",
            "F": "#EF4444",
        },
        labels={
            "internal_marks": "Continuous Internal Evaluation (CIE / 40)",
            "external_marks": "Semester End Exam (SEE / 60)",
            "grade": "Grade"
        }
    )

    fig.update_layout(
        title="<b>CIE vs. SEE Marks Correlation</b>",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=360,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A"),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 42]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 65]),
    )
    return fig


def build_semester_trend_chart(semester_sgpas: Dict[int, float]) -> go.Figure:
    """Creates a progression line chart showing SGPA across semesters."""
    if not semester_sgpas:
        fig = go.Figure()
        fig.update_layout(title="No semester progression data")
        return fig

    sorted_sems = sorted(semester_sgpas.keys())
    sems_label = [f"Semester {s}" for s in sorted_sems]
    sgpas = [semester_sgpas[s] for s in sorted_sems]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sems_label,
        y=sgpas,
        mode="lines+markers+text",
        name="SGPA",
        line=dict(color="#1E3A8A", width=3),
        marker=dict(size=9, color="#0D9488", line=dict(width=2, color="#FFFFFF")),
        text=[f"{v:.2f}" for v in sgpas],
        textposition="top center"
    ))

    fig.update_layout(
        title="<b>Semester-over-Semester Academic Trend (SGPA)</b>",
        yaxis_title="SGPA (out of 10.0)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        yaxis=dict(range=[0, 10.5], showgrid=True, gridcolor="#F1F5F9"),
        xaxis=dict(showgrid=False),
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A")
    )
    return fig


def build_subject_breakdown_bar(results: List[dict]) -> go.Figure:
    """Stacked bar chart showing Internal vs External score components for each subject."""
    df = pd.DataFrame(results)
    if df.empty:
        return go.Figure()

    df = df.dropna(subset=["internal_marks", "external_marks"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["subject_code"],
        y=df["internal_marks"],
        name="Internal (CIE)",
        marker_color="#0D9488"
    ))
    fig.add_trace(go.Bar(
        x=df["subject_code"],
        y=df["external_marks"],
        name="External (SEE)",
        marker_color="#1E3A8A"
    ))

    fig.update_layout(
        barmode="stack",
        title="<b>Course Marks Breakdown (Internal + External)</b>",
        yaxis_title="Total Marks",
        xaxis_title="Course Code",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A"),
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def build_pass_fail_donut(pass_count: int, fail_count: int) -> go.Figure:
    """Donut chart illustrating overall pass rate."""
    labels = ["Cleared", "Needs Recovery"]
    values = [pass_count, fail_count]
    colors = ["#10B981", "#EF4444"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo="percent+label",
        hoverinfo="label+value"
    )])

    fig.update_layout(
        title="<b>Course Clearance Ratio</b>",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=35, b=10),
        height=260,
        showlegend=False,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F172A")
    )
    return fig
