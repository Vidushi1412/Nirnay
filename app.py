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
.stApp {background-color: #07090f;}

/* Remove all default streamlit spacing */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] {gap: 0 !important;}
[data-testid="stHorizontalBlock"] {gap: 0 !important;}
[data-testid="column"] {
    padding: 0 !important;
    gap: 0 !important;
}
/* Remove gap from every element inside columns */
[data-testid="column"] > div {
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="column"] > div > div {
    gap: 0 !important;
}
/* Remove margin from button wrappers */
[data-testid="column"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="column"] .stButton > button {
    margin: 0 !important;
    padding: 7px 10px !important;
    border-radius: 7px !important;
    font-size: 12.5px !important;
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border: none !important;
    background: transparent !important;
    color: #8892a4 !important;
    font-weight: 400 !important;
}
[data-testid="column"] .stButton > button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #dde3f0 !important;
}

/* Active nav button */
[data-testid="stBaseButton-primary"] {
    background: rgba(79,110,247,0.15) !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    color: #818cf8 !important;
    font-weight: 700 !important;
}

/* Hamburger specifically */
#hamburger_btn > button {
    background: rgba(79,110,247,0.15) !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    color: #818cf8 !important;
    font-size: 18px !important;
    padding: 4px 10px !important;
    text-align: center !important;
    justify-content: center !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="metric-container"] label {font-size: 12px !important;}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 24px !important; font-weight: 800 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {border-radius: 8px; font-weight: 500;}
.stTabs [aria-selected="true"] {background: rgba(79,110,247,0.2) !important;}
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,#4f6ef7,#7c3aed) !important;
    color: #fff !important; border: none !important; font-weight: 700 !important;
}
h1, h2, h3 {color: #dde3f0 !important;}
p {color: #8892a4 !important;}
</style>
""", unsafe_allow_html=True)

# ── COLUMNS ───────────────────────────────────────────────────────────────────
if st.session_state.sidebar_open:
    sidebar_col, main_col = st.columns([1, 5])
else:
    sidebar_col, main_col = st.columns([0.001, 5])

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with sidebar_col:
    if st.session_state.sidebar_open:

        # Everything inside one HTML block — no Streamlit gaps
        st.markdown("""
        <div style="
            background: #0c1018;
            min-height: 100vh;
            border-right: 1px solid rgba(255,255,255,0.07);
            padding: 16px 10px 16px 12px;
        ">
            <div style="display:flex;align-items:center;gap:9px;margin-bottom:18px">
                <div style="
                    width:32px;height:32px;border-radius:8px;flex-shrink:0;
                    background:linear-gradient(135deg,#4f6ef7,#7c3aed);
                    display:flex;align-items:center;justify-content:center;
                    font-size:14px;font-weight:900;color:#fff;
                ">न</div>
                <div>
                    <div style="font-size:15px;font-weight:800;color:#dde3f0;letter-spacing:-0.3px">
                        निर्णय
                    </div>
                    <div style="font-size:8px;color:#3d4f68;letter-spacing:1.5px;text-transform:uppercase">
                        Decision Intelligence
                    </div>
                </div>
            </div>
            <div style="
                font-size:9px;color:#3d4f68;font-weight:700;
                text-transform:uppercase;letter-spacing:.09em;
                margin-bottom:6px;
            ">Navigation</div>
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
            btn_type = "primary" if st.session_state.page == p else "secondary"
            if st.button(p, key=f"nav_{p}", use_container_width=True, type=btn_type):
                st.session_state.page = p
                st.rerun()

        st.markdown("""
        <div style="
            height:1px;background:rgba(255,255,255,0.07);
            margin:10px 0 8px 0;
        "></div>
        <p style="
            color:#3d4f68;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.08em;
            margin-bottom:4px;
        ">Active Dataset</p>
        """, unsafe_allow_html=True)

        ds_labels = {k: f"{v['icon']} {v['name']}" for k, v in DATASETS.items()}
        new_ds = st.selectbox(
            "ds",
            list(ds_labels.keys()),
            index=list(ds_labels.keys()).index(st.session_state.selected_ds),
            format_func=lambda k: ds_labels[k],
            label_visibility="collapsed",
        )
        if new_ds != st.session_state.selected_ds:
            st.session_state.selected_ds = new_ds
            st.rerun()

        df_s   = get_data(st.session_state.selected_ds)
        high_n = int((df_s["risk_score"] > 0.7).sum())
        meta   = DATASETS[st.session_state.selected_ds]

        st.markdown(f"""
        <div style="
            background:rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.07);
            border-radius:9px;padding:9px 11px;margin-top:5px;
        ">
            <div style="font-size:11px;color:{meta['color']};font-weight:700">{meta['sector']}</div>
            <div style="font-size:10px;color:#3d4f68;margin-top:2px">{meta['records']:,} records</div>
            <div style="font-size:10px;color:#ef4444;margin-top:2px;font-weight:600">{high_n} high-risk</div>
        </div>
        <div style="
            background:rgba(16,185,129,0.08);
            border:1px solid rgba(16,185,129,0.2);
            border-radius:8px;padding:7px 10px;margin-top:8px;
        ">
            <div style="font-size:10px;font-weight:700;color:#34d399">● All systems live</div>
            <div style="font-size:9px;color:#3d4f68;margin-top:1px">10 datasets · 3 models each</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with main_col:

    # Hamburger top bar
    hcol, spacer = st.columns([0.055, 0.945])
    with hcol:
        if st.button("☰", key="hamburger_btn"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()

    # Divider line under top bar
    st.markdown("""
    <div style="
        height:1px;background:rgba(255,255,255,0.06);
        margin:0 0 16px 0;
    "></div>
    """, unsafe_allow_html=True)

    # Page content with padding
    st.markdown('<div style="padding:0 22px">', unsafe_allow_html=True)

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
