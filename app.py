import streamlit as st
from utils.data_engine import DATASETS, get_data

st.set_page_config(
    page_title="निर्णय — Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

if st.button("☰", key="sidebar_toggle"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()

sidebar_width = "240px" if st.session_state.sidebar_open else "0px"
sidebar_display = "block" if st.session_state.sidebar_open else "none"

st.markdown(f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display: none;}}
.stApp {{ background-color: #07090f; }}

section[data-testid="stSidebar"] {{
    width: {sidebar_width} !important;
    min-width: {sidebar_width} !important;
    display: {sidebar_display} !important;
    transition: all 0.3s ease;
    background-color: #0c1018 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}}
[data-testid="collapsedControl"] {{
    display: none !important;
}}
[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
}}
[data-testid="metric-container"] label {{
    font-size: 12px !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size: 24px !important;
    font-weight: 800 !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    font-weight: 500;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(79,110,247,0.2) !important;
}}
.stButton > button {{
    background: rgba(79,110,247,0.15) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stButton > button:hover {{
    background: rgba(79,110,247,0.28) !important;
}}
[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg,#4f6ef7,#7c3aed) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700 !important;
}}
h1, h2, h3 {{
    color: #dde3f0 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px">
      <div style="width:36px;height:36px;border-radius:9px;
           background:linear-gradient(135deg,#4f6ef7,#7c3aed);
           display:flex;align-items:center;justify-content:center;
           font-size:16px;font-weight:900;color:#fff">न</div>
      <div>
        <div style="font-size:17px;font-weight:800;color:#dde3f0;
             letter-spacing:-0.3px">निर्णय</div>
        <div style="font-size:9px;color:#3d4f68;letter-spacing:2px;
             text-transform:uppercase">Decision Intelligence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Overview",
        "⚠️ Risk Monitor",
        "🎯 Decision Engine",
        "🔬 Simulation Studio",
        "🔀 What-If Analysis",
        "📊 Analytics",
        "⚙️ Rule Engine",
        "✅ Human Review",
        "📋 Reports"
    ], label_visibility="collapsed")

    st.divider()

    st.markdown(
        '<p style="color:#3d4f68;font-size:11px;font-weight:700;'
        'text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">'
        'Active Dataset</p>',
        unsafe_allow_html=True
    )

    ds_labels = {k: f"{v['icon']}  {v['name']}" for k, v in DATASETS.items()}
    selected_ds = st.selectbox(
        "Dataset",
        list(ds_labels.keys()),
        format_func=lambda k: ds_labels[k],
        label_visibility="collapsed"
    )

    df_side = get_data(selected_ds)
    high_n  = int((df_side["risk_score"] > 0.7).sum())
    meta    = DATASETS[selected_ds]

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);
         border:1px solid rgba(255,255,255,0.07);
         border-radius:9px;padding:10px 12px;margin-top:4px">
      <div style="font-size:11px;color:{meta['color']};font-weight:700">
        {meta['sector']}</div>
      <div style="font-size:10px;color:#3d4f68;margin-top:2px">
        {meta['records']:,} records</div>
      <div style="font-size:10px;color:#ef4444;margin-top:2px;font-weight:600">
        {high_n} high-risk cases</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="background:rgba(16,185,129,0.08);
         border:1px solid rgba(16,185,129,0.2);
         border-radius:8px;padding:8px 10px">
      <div style="font-size:10px;font-weight:700;color:#34d399">
        ● All systems live</div>
      <div style="font-size:9px;color:#3d4f68;margin-top:2px">
        10 datasets · 3 models each</div>
    </div>
    """, unsafe_allow_html=True)

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
from pages import (overview, risk_monitor, decision_engine, simulation,
                   whatif, analytics, rule_engine, human_review, reports)

{
    "🏠 Overview":          overview.render,
    "⚠️ Risk Monitor":       risk_monitor.render,
    "🎯 Decision Engine":   decision_engine.render,
    "🔬 Simulation Studio": simulation.render,
    "🔀 What-If Analysis":  whatif.render,
    "📊 Analytics":         analytics.render,
    "⚙️ Rule Engine":       rule_engine.render,
    "✅ Human Review":      human_review.render,
    "📋 Reports":           reports.render,
}[page](selected_ds)