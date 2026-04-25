import streamlit as st
from utils.data_engine import DATASETS, get_data

st.set_page_config(
    page_title="निर्णय — Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "page" not in st.session_state:
    st.session_state.page = "🏠 Overview"
if "selected_ds" not in st.session_state:
    st.session_state.selected_ds = "telecom"

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="collapsedControl"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
.stApp { background-color: #07090f; }

/* Remove ALL default padding and gaps */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="column"] {
    padding: 0 !important;
}

/* Metrics */
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

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(79,110,247,0.2) !important; }

/* Buttons */
.stButton > button {
    background: rgba(79,110,247,0.15) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: rgba(79,110,247,0.28) !important; }
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,#4f6ef7,#7c3aed) !important;
    color: #fff !important; border: none !important; font-weight: 700 !important;
}
h1, h2, h3 { color: #dde3f0 !important; }

/* Nav buttons inside sidebar */
div[data-testid="stVerticalBlock"] .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    color: #8892a4 !important;
    padding: 7px 10px !important;
    border-radius: 7px !important;
    font-size: 12.5px !important;
    font-weight: 400 !important;
    margin-bottom: 1px !important;
}
div[data-testid="stVerticalBlock"] .stButton > button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #dde3f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── TOP BAR — hamburger only ───────────────────────────────────────────────────
st.markdown("""
<div style="background:#0c1018;border-bottom:1px solid rgba(255,255,255,0.06);
     padding:10px 16px;display:flex;align-items:center;gap:14px;
     position:sticky;top:0;z-index:999;width:100%">
  <div id="hamburger-icon" onclick="document.getElementById('fake-hamburger-btn').click()"
       style="width:36px;height:36px;border-radius:8px;
              background:rgba(79,110,247,0.15);border:1px solid rgba(79,110,247,0.3);
              display:flex;align-items:center;justify-content:center;
              font-size:18px;color:#818cf8;cursor:pointer;flex-shrink:0">☰</div>
  <div style="display:flex;align-items:center;gap:8px">
    <div style="width:28px;height:28px;border-radius:7px;
         background:linear-gradient(135deg,#4f6ef7,#7c3aed);
         display:flex;align-items:center;justify-content:center;
         font-size:13px;font-weight:900;color:#fff">न</div>
    <div style="font-size:15px;font-weight:800;color:#dde3f0;letter-spacing:-0.3px">
      निर्णय
      <span style="font-size:10px;color:#3d4f68;font-weight:400;
            letter-spacing:1px;text-transform:uppercase;margin-left:6px">
        Decision Intelligence
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Hidden real button that toggles state
col_hid = st.columns([0.001, 0.999])
with col_hid[0]:
    if st.button("☰", key="fake-hamburger-btn"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
if st.session_state.sidebar_open:
    col_side, col_main = st.columns([0.17, 0.83])
else:
    col_side, col_main = st.columns([0.0001, 0.9999])

# ── FAKE SIDEBAR ──────────────────────────────────────────────────────────────
with col_side:
    if st.session_state.sidebar_open:

        st.markdown("""
        <div style="background:#0c1018;border-right:1px solid rgba(255,255,255,0.07);
             height:100vh;padding:14px 10px 14px 10px;overflow-y:auto">
          <div style="font-size:9.5px;color:#3d4f68;font-weight:700;
               text-transform:uppercase;letter-spacing:.09em;
               margin-bottom:6px;padding:0 4px">Navigation</div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            "🏠 Overview",
            "⚠️ Risk Monitor",
            "🎯 Decision Engine",
            "🔬 Simulation Studio",
            "🔀 What-If Analysis",
            "📊 Analytics",
            "⚙️ Rule Engine",
            "✅ Human Review",
            "📋 Reports",
        ]

        for p in pages:
            is_active = st.session_state.page == p
            btn_style = (
                "background:rgba(79,110,247,0.15) !important;"
                "color:#818cf8 !important;"
                "font-weight:600 !important;"
                "border:1px solid rgba(79,110,247,0.25) !important;"
            ) if is_active else ""

            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p
                st.rerun()

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:10px 0"/>'
            '<p style="color:#3d4f68;font-size:10px;font-weight:700;'
            'text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;padding:0 4px">'
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
        if new_ds != st.session_state.selected_ds:
            st.session_state.selected_ds = new_ds
            st.rerun()

        df_side = get_data(st.session_state.selected_ds)
        high_n  = int((df_side["risk_score"] > 0.7).sum())
        meta    = DATASETS[st.session_state.selected_ds]

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);
             border:1px solid rgba(255,255,255,0.07);
             border-radius:9px;padding:10px 12px;margin-top:6px">
          <div style="font-size:11px;color:{meta['color']};font-weight:700">{meta['sector']}</div>
          <div style="font-size:10px;color:#3d4f68;margin-top:2px">{meta['records']:,} records</div>
          <div style="font-size:10px;color:#ef4444;margin-top:2px;font-weight:600">{high_n} high-risk cases</div>
        </div>
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
             border-radius:8px;padding:8px 10px;margin-top:8px">
          <div style="font-size:10px;font-weight:700;color:#34d399">● All systems live</div>
          <div style="font-size:9px;color:#3d4f68;margin-top:2px">10 datasets · 3 models each</div>
        </div>
        """, unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with col_main:
    st.markdown('<div style="padding:20px 24px">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)
