import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_engine import DATASETS, get_data


def _s(seed, max_val):
    return ((seed * 9301 + 49297) % 233280) / 233280 * max_val


def render(ds_key: str):
    df   = get_data(ds_key)
    meta = DATASETS[ds_key]

    st.markdown("## 🔀 What-If Analysis")
    st.caption("Simulate different business assumptions and compare outcomes side by side")

    options = [f"{row['id']} — {row['label']} ({round(row['risk_score']*100)}% risk)"
               for _, row in df.head(50).iterrows()]
    sel     = st.selectbox("Record to analyse", options)
    sel_id  = sel.split(" — ")[0]
    row     = df[df["id"] == sel_id].iloc[0]
    base    = float(row["risk_score"])

    color_map = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}
    level     = row["risk_level"]
    rv_color  = color_map[level]

    c1, c2, c3 = st.columns(3)
    bonus = c1.slider("Bonus / Discount %", 5, 35, 15, step=5)
    cap   = c2.slider("Budget cap per case (₹)", 100, 3000, 500, step=100)
    c3.metric("Current Baseline", f"{round(base*100)}%", delta=f"{level} Risk", delta_color="inverse")

    st.divider()

    scenarios = [
        {"label": "No intervention (baseline)",         "risk": base,                                              "cost": 0},
        {"label": f"{bonus}% bonus/discount offer",     "risk": max(0.01, base*(1-0.25*(bonus/10))),              "cost": bonus*55},
        {"label": "Retention call only",                "risk": max(0.01, base*0.79),                             "cost": 80},
        {"label": f"Call + {bonus}% bonus combined",    "risk": max(0.01, base*0.62*(1-bonus/100)),               "cost": bonus*55+80},
        {"label": f"Budget cap ₹{cap:,}",               "risk": max(0.01, base*(0.73 if cap>300 else 0.88)),      "cost": cap},
        {"label": "Watch & wait",                       "risk": base*0.96,                                        "cost": 0},
    ]

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown("**Scenario Comparison**")
        for i, s in enumerate(scenarios):
            srv    = "High" if s["risk"]>0.7 else ("Medium" if s["risk"]>0.4 else "Low")
            sc     = color_map[srv]
            red    = round((base - s["risk"]) / base * 100) if i > 0 else 0
            badge  = f'<span style="font-size:10px;color:#10b981;font-weight:600">↓{red}%</span>' if red > 0 else ""
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                 border-radius:9px;padding:11px 14px;margin-bottom:7px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:12px;font-weight:{'400' if i==0 else '600'};
                      color:{'#8892a4' if i==0 else '#dde3f0'}">{s['label']}</span>
                <div style="display:flex;gap:12px;align-items:center">
                  <span style="font-size:11px;color:#3d4f68">₹{s['cost']:,}</span>
                  <span style="font-size:11px;color:{sc};font-weight:600">{round(s['risk']*100)}%</span>
                  {badge}
                </div>
              </div>
              <div style="height:7px;background:rgba(255,255,255,0.07);border-radius:4px;overflow:hidden">
                <div style="height:100%;width:{round(s['risk']*100)}%;background:{sc};border-radius:4px"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("**6-Month Projected Risk Trend**")
        months = ["Jan","Feb","Mar","Apr","May","Jun"]
        seed_base = int(sel_id.replace("TL","").replace("BK","").replace("EC","").replace("IN","")
                        .replace("ST","").replace("AG","").replace("HS","").replace("RE","")
                        .replace("CS","").replace("LG",""), 10) if sel_id[2:].isdigit() else 42
        trend = [round((base*(0.95+i*0.01) + _s(i*17+seed_base%50, 0.06))*100, 1) for i in range(6)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=trend, mode="lines+markers",
                                 line=dict(color=rv_color, width=2),
                                 marker=dict(size=6, color=rv_color),
                                 fill="tozeroy", fillcolor=rv_color.replace("#","rgba(").replace("ef4444","239,68,68,0.08)").replace("f59e0b","245,158,11,0.08)").replace("10b981","16,185,129,0.08)")))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                          font=dict(color="#8892a4",size=10), height=200,
                          margin=dict(l=0,r=0,t=10,b=0),
                          xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                          yaxis=dict(title="Risk %", gridcolor="rgba(255,255,255,0.04)"),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
             border-radius:8px;padding:12px 14px;margin-top:4px;font-size:12px;color:#8892a4;line-height:1.6">
          Trend based on current trajectory <b style="color:#dde3f0">without intervention</b>.
          Risk is projected to remain <b style="color:{rv_color}">{level}</b> over 6 months.
          Best scenario reduces risk to <b style="color:#10b981">{round(min(s['risk'] for s in scenarios)*100)}%</b>.
        </div>
        """, unsafe_allow_html=True)

        # Scenario table
        st.markdown("**Summary Table**")
        tbl = pd.DataFrame([{
            "Scenario": s["label"][:30]+"…" if len(s["label"])>30 else s["label"],
            "Risk After": f"{round(s['risk']*100)}%",
            "Cost (₹)": f"{s['cost']:,}",
            "Reduction": f"{round((base-s['risk'])/base*100)}%" if i>0 else "—",
        } for i, s in enumerate(scenarios)])
        st.dataframe(tbl, use_container_width=True, hide_index=True)
