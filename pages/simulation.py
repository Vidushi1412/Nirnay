import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.data_engine import DATASETS, get_data, get_actions


def render(ds_key: str):
    meta    = DATASETS[ds_key]
    df      = get_data(ds_key)
    actions = get_actions(ds_key)

    st.markdown("## 🔬 Simulation Studio")
    st.caption("Model interventions at scale — set budget, strategy, and see projected outcomes")

    c1, c2, c3 = st.columns(3)
    budget   = c1.slider("Budget (₹)", 5_000, 500_000, 50_000, step=5_000, format="₹%d")
    top_n    = c2.slider("Top-N High Risk Cases", 5, min(150, int((df["risk_score"]>0.7).sum())), 25, step=5)
    strategy = c3.selectbox("Strategy Mode", ["Balanced — Optimal ROI", "Aggressive — Max Impact",
                                               "Low Budget Mode", "Premium Accounts Only"])

    # Select action for strategy
    if "Low Budget" in strategy:
        cheap = [a for a in actions if 0 < a["cost"] < 100]
        action = cheap[0] if cheap else actions[0]
    else:
        action = actions[0]

    high_risk = df[df["risk_score"] > 0.7].sort_values("risk_score", ascending=False)
    targets   = high_risk.head(top_n)
    cases_budgeted = min(len(targets), int(budget // action["cost"]) if action["cost"] > 0 else len(targets))
    total_cost     = cases_budgeted * action["cost"]
    risk_reduced   = targets.head(cases_budgeted)["risk_score"].sum() * action["impact"]

    st.divider()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("High-Risk Pool",     len(high_risk))
    k2.metric("Within Budget",      cases_budgeted, delta=f"of {top_n} targeted")
    k3.metric("Risk Pts Reduced",   f"{risk_reduced:.1f}pts", delta="est. reduction")
    k4.metric("Total Cost",         f"₹{total_cost:,.0f}")

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Risk Score Distribution**")
        bins   = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        labels = ["0-20%","20-40%","40-60%","60-80%","80-100%"]
        counts = [int(((df["risk_score"] >= bins[i]) & (df["risk_score"] < bins[i+1])).sum()) for i in range(5)]
        colors = ["#10b981","#34d399","#f59e0b","#f87171","#ef4444"]

        fig = go.Figure(go.Bar(x=labels, y=counts, marker_color=colors,
                               text=counts, textposition="outside",
                               marker=dict(cornerradius=4)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                          font=dict(color="#8892a4",size=11), height=250,
                          margin=dict(l=0,r=0,t=10,b=0),
                          yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("**Action Impact vs Cost**")
        act_df = [a for a in actions if a["id"] != "no_action"]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=[a["cost"] for a in act_df],
            y=[round(a["impact"]*100) for a in act_df],
            mode="markers+text",
            text=[a["label"] for a in act_df],
            textposition="top center",
            marker=dict(size=14, color=[a["color"] for a in act_df],
                        line=dict(width=1, color="rgba(255,255,255,0.3)")),
        ))
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                           font=dict(color="#8892a4",size=10), height=250,
                           margin=dict(l=0,r=0,t=10,b=0),
                           xaxis=dict(title="Cost (₹)", gridcolor="rgba(255,255,255,0.05)"),
                           yaxis=dict(title="Risk Reduction %", gridcolor="rgba(255,255,255,0.05)"),
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Budget allocation waterfall
    st.markdown("**Budget Allocation Plan**")
    remaining = budget
    alloc_rows = []
    for _, row in targets.iterrows():
        if remaining < action["cost"]:
            break
        remaining -= action["cost"]
        alloc_rows.append({
            "Case": row["id"],
            "Risk Score": round(row["risk_score"], 3),
            "Action": action["label"],
            "Cost (₹)": action["cost"],
            "Est. Risk Reduction": f"{round(row['risk_score'] * action['impact'] * 100, 1)}pts",
            "Budget Remaining": f"₹{remaining:,.0f}",
        })
    if alloc_rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, height=220, hide_index=True)
