import streamlit as st
from utils.data_engine import DATASETS, get_data

st.set_page_config(
    page_title="निर्णय — Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "page" not in st.session_state:
    st.session_state.page = "🏠 Overview"
if "selected_ds" not in st.session_state:
    st.session_state.selected_ds = "telecom"

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="collapsedControl"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
.stApp { background-color: #07090f; }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="metric-container"] label { font-size: 12px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 24px !important; font-weight: 800 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(79,110,247,0.2) !important; }
.stButton > button {
    background: rgba(79,110,247,0.15) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
.stButton > button:hover { background: rgba(79,110,247,0.28) !important; }
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,#4f6ef7,#7c3aed) !important;
    color: #fff !important; border: none !important; font-weight: 700 !important;
}
h1, h2, h3 { color: #dde3f0 !important; }
div[data-testid="stVerticalBlock"] { gap: 0rem; }

/* Custom sidebar panel */
.sidebar-panel {
    background: #0c1018;
    border-right: 1px solid rgba(255,255,255,0.07);
    height: 100vh;
    padding: 16px 12px;
    position: sticky;
    top: 0;
}
.nav-btn {
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: #8892a4;
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    margin-bottom: 2px;
    transition: all 0.2s;
}
.nav-btn:hover { background: rgba(255,255,255,0.05); color: #dde3f0; }
.nav-btn.active { background: rgba(79,110,247,0.15); color: #818cf8; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
# Top bar with hamburger
top = st.container()
with top:
    tb1, tb2 = st.columns([0.04, 0.96])
    with tb1:
        if st.button("☰", key="hamburger"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open

# Main layout
if st.session_state.sidebar_open:
    col_side, col_main = st.columns([0.18, 0.82])
else:
    col_side, col_main = st.columns([0.0001, 0.9999])

# ── FAKE SIDEBAR ──────────────────────────────────────────────────────────────
with col_side:
    if st.session_state.sidebar_open:
        st.markdown("""
        <div style="background:#0c1018;border-right:1px solid rgba(255,255,255,0.07);
             min-height:100vh;padding:16px 10px;margin-top:-60px;padding-top:70px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px">
            <div style="width:32px;height:32px;border-radius:8px;
                 background:linear-gradient(135deg,#4f6ef7,#7c3aed);
                 display:flex;align-items:center;justify-content:center;
                 font-size:14px;font-weight:900;color:#fff">न</div>
            <div>
              <div style="font-size:15px;font-weight:800;color:#dde3f0">निर्णय</div>
              <div style="font-size:8px;color:#3d4f68;letter-spacing:2px;
                   text-transform:uppercase">Decision Intelligence</div>
            </div>
          </div>
          <div style="font-size:9px;color:#3d4f68;font-weight:700;
               text-transform:uppercase;letter-spacing:.08em;
               margin-bottom:6px;padding:0 4px">Navigation</div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            "🏠 Overview", "⚠️ Risk Monitor", "🎯 Decision Engine",
            "🔬 Simulation Studio", "🔀 What-If Analysis",
            "📊 Analytics", "⚙️ Rule Engine", "✅ Human Review", "📋 Reports"
        ]
        for p in pages:
            if st.button(p, key=f"nav_{p}",
                         use_container_width=True):
                st.session_state.page = p

        st.divider()
        st.markdown(
            '<p style="color:#3d4f68;font-size:10px;font-weight:700;'
            'text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">'
            'Active Dataset</p>',
            unsafe_allow_html=True
        )

        ds_labels = {k: f"{v['icon']} {v['name']}" for k, v in DATASETS.items()}
        new_ds = st.selectbox(
            "Dataset",
            list(ds_labels.keys()),
            index=list(ds_labels.keys()).index(st.session_state.selected_ds),
            format_func=lambda k: ds_labels[k],
            label_visibility="collapsed",
            key="ds_select"
        )
        st.session_state.selected_ds = new_ds

        df_side = get_data(st.session_state.selected_ds)
        high_n  = int((df_side["risk_score"] > 0.7).sum())
        meta    = DATASETS[st.session_state.selected_ds]

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

        st.markdown("""
        <div style="background:rgba(16,185,129,0.08);
             border:1px solid rgba(16,185,129,0.2);
             border-radius:8px;padding:8px 10px;margin-top:8px">
          <div style="font-size:10px;font-weight:700;color:#34d399">
            ● All systems live</div>
          <div style="font-size:9px;color:#3d4f68;margin-top:2px">
            10 datasets · 3 models each</div>
        </div>
        """, unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with col_main:
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
    }[st.session_state.page](st.session_state.selected_ds)
