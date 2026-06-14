"""DeploySense Dashboard — Interactive risk analysis across entities and deployments.

Flow:
  1. Select account → shows entities with deployments
  2. Select entity → shows deployment history
  3. Select a deployment as "test" → previous ones used for analysis
  4. Run analysis → Claude evaluates risk
  5. Compare → show actual outcome vs prediction

Run:
  pip install streamlit plotly httpx
  streamlit run dashboard.py
"""

import asyncio
import json
import os
import time
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Load .env file if present (for local development)
try:
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)
except FileNotFoundError:
    pass

# Import pipeline functions
import sys
sys.path.insert(0, ".")
from scripts.risk_pipeline import (
    query_nrql, query_nerdgraph, fetch_deployments, fetch_entity_and_related,
    enrich_all_parallel, fetch_all_patches_parallel, fetch_patches_for_deploy,
    build_prompt, call_llm, ms_to_str,
    THIRTY_DAYS_MS, MAX_CONCURRENT,
)
import scripts.risk_pipeline as pipeline

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="DeploySense",
    page_icon="🔍",
    layout="wide",
)

# ─── Configuration ────────────────────────────────────────────────────────────

ACCOUNTS = [
    {"id": 10888623, "name": "ace (Alerting)"},
    {"id": 779820, "name": "Derived Data Streams"},
    {"id": 10945818, "name": "Alerts Lifecycle"},
]

NR_API_KEY = os.environ.get("NR_API_KEY", "")
GHE_TOKEN = os.environ.get("GHE_TOKEN", "")
NERDGRAPH_URL = os.environ.get("NERDGRAPH_URL", "https://nerd-graph.staging-service.nr-ops.net")
LLM_TOKEN = os.environ.get("NERD_COMPLETION_TOKEN", "")

# Set pipeline globals
pipeline.API_KEY = NR_API_KEY
pipeline.GHE_TOKEN = GHE_TOKEN
pipeline.NERD_GRAPH_HOST = NERDGRAPH_URL
pipeline.LLM_TOKEN = LLM_TOKEN


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ─── State ────────────────────────────────────────────────────────────────────

if "entities" not in st.session_state:
    st.session_state.entities = []
if "deployments" not in st.session_state:
    st.session_state.deployments = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "prompt" not in st.session_state:
    st.session_state.prompt = None
if "part1" not in st.session_state:
    st.session_state.part1 = None
if "part2" not in st.session_state:
    st.session_state.part2 = None


# ─── URL Query Parameters (for deep-linking from PR comment) ──────────────────

query_params = st.query_params
prefill_account = query_params.get("account_id", None)
prefill_entity = query_params.get("entity_guid", None)
prefill_analysis = query_params.get("analysis_file", None)

# If prefill_analysis points to a file, load it
if prefill_analysis and os.path.exists(prefill_analysis) and not st.session_state.analysis_result:
    with open(prefill_analysis) as f:
        cached = f.read()
    st.session_state.analysis_result = cached
    if "PART 2:" in cached or "PART 2" in cached:
        parts = cached.split("PART 2:", 1) if "PART 2:" in cached else cached.split("PART 2", 1)
        part1 = parts[0].replace("PART 1: GITHUB/GITLAB PR COMMENT (CONCISE & SCANNABLE)", "").strip()
        part1 = "\n".join(l for l in part1.split("\n") if not l.strip().startswith("===="))
        st.session_state.part1 = part1.strip()
        part2 = parts[1] if len(parts) > 1 else ""
        part2 = part2.replace("DASHBOARD METRICS & ANALYSIS (DETAILED DATA COMPONENT)", "").strip()
        part2 = "\n".join(l for l in part2.split("\n") if not l.strip().startswith("===="))
        st.session_state.part2 = part2.strip()
    else:
        st.session_state.part1 = cached
        st.session_state.part2 = ""

# ─── Header ───────────────────────────────────────────────────────────────────

st.title("🔍 DeploySense")
st.caption("AI-powered deployment risk analysis — select an entity and deployment to evaluate")

# ─── Sidebar: Account + Entity Selection ──────────────────────────────────────

with st.sidebar:
    st.header("Configuration")

    # Account selector (auto-select from URL params if provided)
    account_names = [f"{a['name']} ({a['id']})" for a in ACCOUNTS]
    default_account_idx = 0
    if prefill_account:
        for i, a in enumerate(ACCOUNTS):
            if str(a["id"]) == str(prefill_account):
                default_account_idx = i
                break
    selected_account_idx = st.selectbox("Account", range(len(ACCOUNTS)), index=default_account_idx, format_func=lambda i: account_names[i])
    selected_account = ACCOUNTS[selected_account_idx]
    account_id = selected_account["id"]

    st.markdown("---")

    # Fetch entities for this account
    if st.button("🔄 Load Entities", use_container_width=True):
        with st.spinner("Fetching entities with deployments..."):
            nrql = (
                f"SELECT count(*) FROM ChangeTrackingEvent "
                f"WHERE category = 'Deployment' AND deployment_phase = 'end' "
                f"SINCE 30 days ago FACET `entity.guid`, `entity.name` LIMIT 50"
            )
            results = run_async(query_nrql(nrql, account_id))
            entities = []
            for r in results:
                facet = r.get("facet", [])
                if isinstance(facet, list) and len(facet) >= 2:
                    entities.append({
                        "guid": facet[0],
                        "name": facet[1],
                        "deploy_count": r.get("count", 0),
                    })
            st.session_state.entities = entities
            st.session_state.deployments = []
            st.session_state.analysis_result = None

    # Entity selector
    if st.session_state.entities:
        entity_labels = [f"{e['name']} ({e['deploy_count']} deploys)" for e in st.session_state.entities]
        selected_entity_idx = st.selectbox("Entity", range(len(st.session_state.entities)), format_func=lambda i: entity_labels[i])
        selected_entity = st.session_state.entities[selected_entity_idx]

        st.markdown(f"**GUID:** `{selected_entity['guid'][:25]}...`")

        # Fetch deployments
        if st.button("📋 Load Deployments", use_container_width=True):
            with st.spinner("Fetching deployments + violations..."):
                timestamp_ms = int(time.time() * 1000)
                deployments = run_async(fetch_deployments(selected_entity["guid"], timestamp_ms, account_id))

                if deployments:
                    # Enrich with violations (parallel)
                    root_entity, related_map = run_async(fetch_entity_and_related(selected_entity["guid"]))
                    deployments = run_async(enrich_all_parallel(deployments, root_entity, related_map, account_id))
                    st.session_state.deployments = deployments
                    st.session_state.analysis_result = None

        st.markdown("---")
        st.markdown(f"**Deployments loaded:** {len(st.session_state.deployments)}")
        violated = sum(1 for d in st.session_state.deployments if len(d.get("root_entity_alert_violations", [])) > 0)
        if violated:
            st.markdown(f"**With violations:** {violated}")


# ─── Main Area ────────────────────────────────────────────────────────────────

if not st.session_state.deployments:
    st.info("👈 Select an account, load entities, then load deployments from the sidebar.")
    st.stop()

col1, col2 = st.columns([1, 2])

# ─── Column 1: Deployment List ────────────────────────────────────────────────

with col1:
    st.subheader("Deployments")
    st.caption("Select one as the 'test deployment' — previous ones become history for analysis.")

    deployments = st.session_state.deployments

    for i, dep in enumerate(deployments):
        violations = dep.get("root_entity_alert_violations", [])
        result = dep.get("deployment_result", "?")
        version = dep.get("version", "?")
        ts = dep.get("timestamp_str", "?")
        user = dep.get("user", "?")

        # Status indicators
        if violations:
            icon = "🚨"
            status = f"{len(violations)} violations"
        elif result == "failure":
            icon = "❌"
            status = "infra failure"
        else:
            icon = "✅"
            status = "clean"

        if st.button(f"{icon} {version} — {status}", key=f"dep_{i}", use_container_width=True):
            st.session_state.selected_index = i
            st.session_state.analysis_result = None
            st.session_state.prompt = None

    # Show which is selected
    selected_idx = st.session_state.get("selected_index", 0)
    st.markdown(f"**Selected:** {deployments[selected_idx].get('version', '?')}")


# ─── Column 2: Analysis ──────────────────────────────────────────────────────

with col2:
    selected_idx = st.session_state.get("selected_index", 0)
    target_dep = deployments[selected_idx]

    st.subheader(f"Analysis: {target_dep.get('version', '?')}")

    # Deployment metadata
    with st.expander("Deployment Details", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Version:** {target_dep.get('version', '?')}")
            st.markdown(f"**Deployer:** {target_dep.get('user', '?')}")
            st.markdown(f"**Time:** {target_dep.get('timestamp_str', '?')}")
            st.markdown(f"**Environment:** {target_dep.get('environment', '?')}")
        with col_b:
            st.markdown(f"**Result:** {target_dep.get('deployment_result', '?')}")
            st.markdown(f"**Repo:** {target_dep.get('gheOrg', '')}/{target_dep.get('gheRepo', '')}")
            st.markdown(f"**Commit:** `{(target_dep.get('commit') or '')[:12]}`")
            st.markdown(f"**Mechanism:** {target_dep.get('deployMechanism', '?')}")

    # Actual outcome (the "answer" — hidden until after analysis)
    actual_violations = target_dep.get("root_entity_alert_violations", [])
    actual_result = target_dep.get("deployment_result", "?")

    # Run analysis
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 PR Summary", "📊 Detailed Analysis", "📄 Raw Prompt", "✅ Actual Outcome"])

    with tab1:
        if st.button("🚀 Run Risk Analysis", use_container_width=True, type="primary"):
            with st.spinner("Fetching code patches + building prompt..."):
                # Fetch patches for target
                run_async(fetch_patches_for_deploy(target_dep, asyncio.Semaphore(1)))

                # Fetch patches for violated historical deploys
                violated_history = [
                    d for d in deployments
                    if len(d.get("root_entity_alert_violations", [])) > 0
                    and d.get("changeTrackingId") != target_dep.get("changeTrackingId")
                ]
                if violated_history and GHE_TOKEN:
                    run_async(fetch_all_patches_parallel(violated_history))

                # Build prompt
                prompt = build_prompt(target_dep, deployments)
                st.session_state.prompt = prompt

            with st.spinner("Claude is analyzing... (may take 60-90s)"):
                response = run_async(call_llm(prompt))
                if response:
                    st.session_state.analysis_result = response
                    # Split into Part 1 and Part 2
                    if "PART 2:" in response or "PART 2" in response:
                        parts = response.split("PART 2:", 1) if "PART 2:" in response else response.split("PART 2", 1)
                        part1 = parts[0]
                        # Clean up Part 1: remove the "PART 1:" header if present
                        part1 = part1.replace("PART 1: GITHUB/GITLAB PR COMMENT (CONCISE & SCANNABLE)", "").strip()
                        part1 = part1.replace("PART 1:", "").strip()
                        # Remove separator lines
                        part1 = "\n".join(l for l in part1.split("\n") if not l.strip().startswith("===="))
                        st.session_state.part1 = part1.strip()

                        part2 = parts[1] if len(parts) > 1 else ""
                        part2 = part2.replace("DASHBOARD METRICS & ANALYSIS (DETAILED DATA COMPONENT)", "").strip()
                        part2 = "\n".join(l for l in part2.split("\n") if not l.strip().startswith("===="))
                        st.session_state.part2 = part2.strip()
                    else:
                        # Fallback: no split markers found, put everything in part1
                        st.session_state.part1 = response
                        st.session_state.part2 = ""
                else:
                    st.error("LLM call failed. Check token or network.")

        # Display Part 1 (concise PR comment)
        if st.session_state.get("part1"):
            st.markdown(st.session_state.part1, unsafe_allow_html=True)
        elif st.session_state.analysis_result:
            st.markdown(st.session_state.analysis_result)

    with tab2:
        # Display Part 2 (detailed analysis)
        if st.session_state.get("part2"):
            st.markdown(st.session_state.part2, unsafe_allow_html=True)
        elif st.session_state.analysis_result:
            st.info("Full analysis displayed in PR Summary tab (model did not split into parts).")
        else:
            st.info("Run analysis first to see detailed breakdown.")

    with tab3:
        if st.session_state.prompt:
            st.code(st.session_state.prompt[:10000], language="markdown")
            if len(st.session_state.prompt) > 10000:
                st.caption(f"... [{len(st.session_state.prompt) - 10000} more chars]")
        else:
            st.info("Run analysis first to see the prompt.")

    with tab4:
        st.subheader("Actual Deployment Outcome")

        if actual_violations:
            st.error(f"🚨 **{len(actual_violations)} alert violation(s) triggered after this deploy**")
            for v in actual_violations:
                st.markdown(f"- **[{v.get('level', '?')}]** {v.get('label', '?')}")
                st.caption(f"  Opened: {v.get('openedAt', '?')} | Closed: {v.get('closedAt', '?')}")
            actual_risk = "HIGH"
        elif actual_result == "failure":
            st.warning("❌ **Infrastructure failure** — pods couldn't start")
            actual_risk = "HIGH"
        else:
            st.success("✅ **Clean deployment** — no violations, no anomalies")
            actual_risk = "LOW"

        # Auto-compare: extract risk level from Claude's analysis
        st.markdown("---")
        st.subheader("Model Accuracy")

        if st.session_state.analysis_result:
            analysis_text = st.session_state.analysis_result.upper()

            # Extract predicted risk from the analysis
            predicted_risk = "UNKNOWN"
            for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if f"RISK RATING" in analysis_text or f"RISK:" in analysis_text:
                    # Look for risk level mentions in the risk matrix or summary
                    pass
            # Heuristic: count risk level mentions
            critical_count = analysis_text.count("CRITICAL")
            high_count = analysis_text.count("HIGH")
            medium_count = analysis_text.count("MEDIUM")
            low_count = analysis_text.count("LOW")

            if critical_count >= 2:
                predicted_risk = "CRITICAL"
            elif high_count >= 3:
                predicted_risk = "HIGH"
            elif medium_count >= 3:
                predicted_risk = "MEDIUM"
            elif low_count >= 3:
                predicted_risk = "LOW"
            else:
                # Fallback: dominant risk level
                counts = {"CRITICAL": critical_count, "HIGH": high_count, "MEDIUM": medium_count, "LOW": low_count}
                predicted_risk = max(counts, key=counts.get)

            # Determine if prediction was correct
            risky_predictions = ["HIGH", "CRITICAL"]
            risky_actual = actual_risk in ["HIGH", "CRITICAL"]
            predicted_risky = predicted_risk in risky_predictions

            if risky_actual and predicted_risky:
                verdict = "CORRECT"
                verdict_icon = "✅"
                verdict_msg = f"AI predicted **{predicted_risk}** risk → Actual: **{len(actual_violations)} violations triggered** → **Correctly identified risk**"
            elif not risky_actual and not predicted_risky:
                verdict = "CORRECT"
                verdict_icon = "✅"
                verdict_msg = f"AI predicted **{predicted_risk}** risk → Actual: **Clean deployment** → **Correctly identified safe deploy**"
            elif risky_actual and not predicted_risky:
                verdict = "MISSED"
                verdict_icon = "❌"
                verdict_msg = f"AI predicted **{predicted_risk}** risk → Actual: **{len(actual_violations)} violations triggered** → **Missed the risk**"
            else:
                verdict = "FALSE ALARM"
                verdict_icon = "⚠️"
                verdict_msg = f"AI predicted **{predicted_risk}** risk → Actual: **Clean deployment** → **Over-cautious (false alarm)**"

            # Display verdict
            if verdict == "CORRECT":
                st.success(f"{verdict_icon} {verdict_msg}")
            elif verdict == "MISSED":
                st.error(f"{verdict_icon} {verdict_msg}")
            else:
                st.warning(f"{verdict_icon} {verdict_msg}")

            # Score card
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1:
                st.metric("AI Prediction", predicted_risk)
            with col_v2:
                st.metric("Actual Outcome", f"{len(actual_violations)} violations" if actual_violations else "Clean")
            with col_v3:
                st.metric("Verdict", verdict)
        else:
            st.info("Run the risk analysis first to see accuracy comparison.")
