from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ci_cd_analyzer.utils.helpers import analyze_pipeline_log


SAMPLE_LOGS = {
    "jenkins": PROJECT_ROOT / "examples" / "jenkins_sample.log",
    "github": PROJECT_ROOT / "examples" / "github_sample.log",
}


def _load_sample(source: str) -> str:
    sample_path = SAMPLE_LOGS[source]
    return sample_path.read_text(encoding="utf-8")


st.set_page_config(page_title="CI/CD Pipeline Analyzer", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        .hero {
            padding: 1.25rem 1.5rem;
            border-radius: 1rem;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            margin-bottom: 1.25rem;
        }
        .hero h1 { margin: 0; font-size: 2rem; }
        .hero p { margin: 0.5rem 0 0 0; color: #cbd5e1; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>CI/CD Pipeline Analyzer</h1>
        <p>Inspect build logs, spot bottlenecks, and surface flaky stages before they become blockers.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

source = st.sidebar.selectbox("Log source", ["jenkins", "github"], index=0)
use_sample = st.sidebar.checkbox("Load sample log", value=True)

uploaded_file = st.file_uploader("Upload a pipeline log", type=["log", "txt"])
log_text = ""

if uploaded_file is not None:
    log_text = uploaded_file.read().decode("utf-8", errors="replace")
elif use_sample:
    log_text = _load_sample(source)

st.text_area("Log input", value=log_text, height=260, key="log_input")

analyze_button = st.button("Analyze log")

if analyze_button:
    input_text = st.session_state.get("log_input", "")
    if not input_text.strip():
        st.error("Add or upload a log first.")
    else:
        try:
            report = analyze_pipeline_log(source, input_text)
        except ValueError as error:
            st.error(str(error))
        else:
            summary = report.summary
            columns = st.columns(5)
            columns[0].metric("Total runs", summary.total_runs)
            columns[1].metric("Success runs", summary.success_runs)
            columns[2].metric("Failure runs", summary.failure_runs)
            columns[3].metric("Success rate", f"{summary.success_rate:.0%}")
            columns[4].metric("Avg duration", f"{summary.average_execution_time_seconds:.1f}s")

            st.subheader("Stage analysis")
            stage_rows = [
                {
                    "Stage": metric.stage,
                    "Avg Time (s)": round(metric.average_duration_seconds, 1),
                    "Failures": metric.failure_count,
                    "Runs": metric.total_runs,
                    "Failure Rate": f"{metric.failure_rate:.0%}",
                    "Flaky": "Yes" if metric.flaky else "No",
                }
                for metric in report.stage_metrics
            ]
            st.dataframe(stage_rows, use_container_width=True)

            st.subheader("Bottlenecks")
            if report.bottlenecks:
                st.table([
                    {
                        "Stage": item.stage,
                        "Avg Time (s)": round(item.average_duration_seconds, 1),
                        "Multiplier": f"{item.multiplier_vs_average:.1f}x",
                        "Insight": item.insight,
                    }
                    for item in report.bottlenecks
                ])
            else:
                st.info("No major bottlenecks detected from the current log sample.")

            st.subheader("Failure patterns")
            if report.failure_patterns:
                st.table([
                    {
                        "Stage": item.stage,
                        "Failures": item.failure_count,
                        "Share": f"{item.share_of_failures:.0%}",
                        "Common errors": ", ".join(item.common_errors) if item.common_errors else "None captured",
                    }
                    for item in report.failure_patterns
                ])
            else:
                st.success("No failures detected in this log.")

            st.subheader("Flaky stages")
            if report.flaky_stages:
                st.table([
                    {
                        "Stage": item.stage,
                        "Pattern": " → ".join(item.pattern),
                        "Insight": item.insight,
                    }
                    for item in report.flaky_stages
                ])
            else:
                st.info("No flaky stage pattern detected.")

            st.subheader("Actionable suggestions")
            if report.suggestions:
                for suggestion in report.suggestions:
                    st.warning(f"**{suggestion.area}:** {suggestion.suggestion}  \nReason: {suggestion.reason}")
            else:
                st.success("No immediate suggestions were generated from the current log.")
