import streamlit as st
from utils.data_engine import DATASETS


RULES_DEFAULT = [
    {"id": 1, "label": "Max discount cap",       "desc": "Never offer discount above threshold",              "type": "cost"},
    {"id": 2, "label": "CIBIL floor",             "desc": "No top-up loans below CIBIL score floor",         "type": "eligibility"},
    {"id": 3, "label": "Premium-first support",   "desc": "Corporate accounts get call before discount",     "type": "priority"},
    {"id": 4, "label": "Tier-2 city boost",       "desc": "Extra impact weight for Tier-2 interventions",    "type": "boost"},
    {"id": 5, "label": "Low-value filter",        "desc": "Skip costly interventions for low-value accounts","type": "cost"},
    {"id": 6, "label": "Repeat block cooldown",   "desc": "Same action blocked within 30 days",              "type": "cooldown"},
    {"id": 7, "label": "High-risk auto-escalate", "desc": "Risk > 85% triggers senior team escalation",      "type": "escalation"},
    {"id": 8, "label": "Weekend intervention ban","desc": "No calls/actions on public holidays",              "type": "scheduling"},
]

TYPE_COLORS = {
    "cost":       ("rgba(245,158,11,0.12)",  "#fbbf24",  "rgba(245,158,11,0.2)"),
    "eligibility":("rgba(239,68,68,0.1)",    "#f87171",  "rgba(239,68,68,0.2)"),
    "priority":   ("rgba(59,130,246,0.1)",   "#60a5fa",  "rgba(59,130,246,0.2)"),
    "boost":      ("rgba(16,185,129,0.1)",   "#34d399",  "rgba(16,185,129,0.2)"),
    "cooldown":   ("rgba(167,139,250,0.1)",  "#a78bfa",  "rgba(167,139,250,0.2)"),
    "escalation": ("rgba(239,68,68,0.12)",   "#f87171",  "rgba(239,68,68,0.25)"),
    "scheduling": ("rgba(56,189,248,0.1)",   "#7dd3fc",  "rgba(56,189,248,0.2)"),
}


def render(ds_key: str):
    st.markdown("## ⚙️ Rule Engine")
    st.caption("Configure business constraints, eligibility rules, and action parameters")

    # Persist toggle state in session
    for r in RULES_DEFAULT:
        key = f"rule_{r['id']}_on"
        if key not in st.session_state:
            st.session_state[key] = r["id"] not in (3, 6, 8)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Business Rules**")
        for r in RULES_DEFAULT:
            key     = f"rule_{r['id']}_on"
            is_on   = st.session_state[key]
            bg, tc, bc = TYPE_COLORS.get(r["type"], TYPE_COLORS["cost"])
            col_a, col_b, col_c = st.columns([0.12, 0.72, 0.16])
            with col_a:
                toggled = st.checkbox("", value=is_on, key=f"cb_{r['id']}", label_visibility="collapsed")
                st.session_state[key] = toggled
            with col_b:
                st.markdown(f"""
                <div style="padding:4px 0">
                  <span style="font-size:13px;font-weight:600;color:#dde3f0">{r['label']}</span><br/>
                  <span style="font-size:11px;color:#8892a4">{r['desc']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                st.markdown(f'<span style="background:{bg};color:{tc};border:1px solid {bc};'
                            f'padding:2px 7px;border-radius:4px;font-size:10px;font-weight:600">'
                            f'{r["type"]}</span>', unsafe_allow_html=True)

    with col_right:
        st.markdown("**Business Parameters**")

        discount_max  = st.slider("Max Discount %",      5,  50,  25, key="re_disc")
        cibil_floor   = st.slider("CIBIL Floor Score",   400, 800, 600, step=10, key="re_cibil")
        budget_per    = st.slider("Budget per Case (₹)", 50,  5000, 500, step=50, key="re_budget")
        roi_threshold = st.slider("Min ROI Threshold %", 0,   100, 10,  key="re_roi")

        active_rules = sum(1 for r in RULES_DEFAULT if st.session_state.get(f"rule_{r['id']}_on", True))

        st.markdown(f"""
        <div style="background:rgba(79,110,247,0.07);border:1px solid rgba(79,110,247,0.2);
             border-radius:10px;padding:14px;margin-top:12px">
          <div style="font-size:10px;font-weight:700;color:#818cf8;text-transform:uppercase;
               letter-spacing:.07em;margin-bottom:7px">Rule Summary</div>
          <p style="font-size:12.5px;color:#dde3f0;line-height:1.7;margin:0">
            <b style="color:#dde3f0">{active_rules}</b> of {len(RULES_DEFAULT)} rules active.
            Discount capped at <b style="color:#dde3f0">{discount_max}%</b>.
            CIBIL floor at <b style="color:#dde3f0">{cibil_floor}</b>.
            Budget <b style="color:#dde3f0">₹{budget_per:,}</b>/case.
            Only actions with ROI ≥ <b style="color:#dde3f0">{roi_threshold}%</b> will be surfaced.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**Rule Impact Preview**")
        st.info(f"With current rules: **{discount_max}%** max discount, **CIBIL ≥ {cibil_floor}** for top-up loans, **₹{budget_per:,}** per-case budget cap.")

        if st.button("Reset All to Defaults"):
            for r in RULES_DEFAULT:
                st.session_state[f"rule_{r['id']}_on"] = r["id"] not in (3, 6, 8)
            st.rerun()
