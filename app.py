"""
निर्णय — Nirnay Decision Intelligence Platform
Run: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="निर्णय — Decision Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar toggle button ──────────────────────────────────────────────────
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

col_toggle, col_title = st.columns([0.05, 0.95])
with col_toggle:
    if st.button("☰"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open

if st.session_state.sidebar_open:
    sidebar_width = "218px"
else:
    sidebar_width = "0px"

st.markdown(f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display: none;}}
.stApp {{ background-color: #07090f; }}

/* Sidebar toggle control */
section[data-testid="stSidebar"] {{
    width: {sidebar_width} !important;
    min-width: {sidebar_width} !important;
    transition: width 0.3s ease;
    overflow: hidden;
}}
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* Rest of your existing CSS */
[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
}}
[data-testid="metric-container"] label {{ font-size: 12px !important; }}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{ font-size: 24px !important; font-weight: 800 !important; }}
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px; font-weight: 500; }}
.stTabs [aria-selected="true"] {{ background: rgba(79,110,247,0.2) !important; }}
.stButton > button {{
    background: rgba(79,110,247,0.15) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(79,110,247,0.3) !important;
    border-radius: 8px !important; font-weight: 600 !important;
}}
.stButton > button:hover {{ background: rgba(79,110,247,0.28) !important; }}
[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg,#4f6ef7,#7c3aed) !important;
    color:#fff !important; border:none !important; font-weight:700 !important;
}}
h1,h2,h3 {{ color: #dde3f0 !important; }}
</style>
""", unsafe_allow_html=True)