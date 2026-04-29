"""
Nirnay — Business KPI Dashboard
Real business metrics: revenue at risk, interventions, success rate, cost saved
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_engine import DATASETS, get_data
from utils.action_tracker import load_logs


def render(email: str, ds_key: str):
    st.markdown("## 📈 Business Dashboard")
    st.caption("Real business metrics — revenue at risk, interventions, cost saved, success rate")

    df   = get_data(ds_key)
    meta = DATASETS[ds_key]
    logs = load_logs(email)

    high = df[df["risk_score"] > 0.7]
    med  = df[(df["risk_score"] > 0.4) & (df["risk_score"] <= 0.7)]
    low  = df[df["risk_score"] <= 0.4]

    # Estimate revenue at risk
    val_col = next((c for c in ["loan_amount","order_value","monthly_recharge",
                                "sum_insured","funding_cr","budget_lakhs"] if c in df.columns), None)
    if val_col:
        rev_at_risk = float(df[df["risk_score"] > 0.7][val_col].sum())
        total_rev   = float(df[val_col].sum())
        rev_pct     = round(rev_at_risk / total_rev * 100, 1) if total_rev > 0 else 0
    else:
        rev_at_risk = len(high) * 50000
        total_rev   = len(df) * 50000
        rev_pct     = round(len(high) / len(df) * 100, 1)

    # Action log stats
    logs_df = pd.DataFrame(logs.values()) if logs else pd.DataFrame()
    total_actions   = len(logs_df)
    resolved        = int((logs_df["status"] == "Resolved").sum()) if len(logs_df) > 0 else 0
    total_spent     = float(logs_df["cost_rs"].sum()) if len(logs_df) > 0 else 0
    success_rate    = round(resolved / total_actions * 100, 1) if total_actions > 0 else 0

    resolved_df = logs_df[logs_df["risk_after"].notna()] if len(logs_df) > 0 else pd.DataFrame()
    risk_reduction = 0.0
    if len(resolved_df) > 0:
        risk_reduction = float(
            ((resolved_df["risk_before"] - resolved_df["risk_after"]) /
             resolved_df["risk_before"] * 100).mean()
        )

    # ── Row 1 KPIs ────────────────────────────────────────────────────────────
    st.markdown("### Portfolio Overview")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Records",    f"{len(df):,}")
    k2.metric("🔴 High Risk",     len(high), delta=f"{round(len(high)/len(df)*100)}%", delta_color="inverse")
    k3.metric("Revenue at Risk",  f"₹{rev_at_risk/100000:.1f}L", delta=f"{rev_pct}% of total", delta_color="inverse")
    k4.metric("Actions Taken",    total_actions)
    k5.metric("Success Rate",     f"{success_rate}%", delta="resolved cases")
    k6.metric("Total Spent",      f"₹{total_spent:,.0f}")

    st.divider()

    # ── Charts Row 1 ─────────────────────────────────────────────────────────
    st.markdown("### Risk & Revenue Analysis")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Risk Level Distribution**")
        fig1 = go.Figure(go.Pie(
            labels=["High Risk","Medium Risk","Low Risk"],
            values=[len(high), len(med), len(low)],
            hole=0.6,
            marker_colors=["#ef4444","#f59e0b","#10b981"],
            textinfo="percent+label",
            textfont=dict(size=11, color="#dde3f0"),
        ))
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892a4"), height=220,
            margin=dict(l=0,r=0,t=10,b=0), showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.markdown("**Monthly Risk Trend**")
        months = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
        trend = [df.iloc[i::12]["risk_score"].mean()*100 for i in range(12)]
        fig2 = go.Figure(go.Scatter(
            x=months, y=[round(v,1) for v in trend],
            mode="lines+markers",
            line=dict(color=meta["color"], width=2),
            marker=dict(size=5, color=meta["color"]),
            fill="tozeroy",
            fillcolor="rgba(79,110,247,0.12)",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#8892a4",size=10), height=220,
            margin=dict(l=0,r=0,t=10,b=0),
            yaxis=dict(title="Avg Risk %", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Action Performance ─────────────────────────────────────────────────────
    if total_actions > 0:
        st.divider()
        st.markdown("### Intervention Performance")

        p1, p2 = st.columns(2)

        with p1:
            st.markdown("**Actions by Status**")
            statuses = logs_df["status"].value_counts()
            colors   = {"Resolved":"#10b981","Pending":"#f59e0b","Failed":"#ef4444"}
            fig3 = go.Figure(go.Bar(
                x=statuses.index.tolist(),
                y=statuses.values.tolist(),
                marker_color=[colors.get(s,"#818cf8") for s in statuses.index],
                text=statuses.values.tolist(),
                textposition="outside",
                marker=dict(cornerradius=4),
            ))
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#8892a4",size=11), height=200,
                margin=dict(l=0,r=0,t=10,b=0),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)

        with p2:
            st.markdown("**Actions by Type**")
            action_counts = logs_df["action"].value_counts().head(5)
            fig4 = go.Figure(go.Bar(
                x=action_counts.values.tolist(),
                y=action_counts.index.tolist(),
                orientation="h",
                marker_color="#4f6ef7",
                marker=dict(cornerradius=4),
            ))
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#8892a4",size=10), height=200,
                margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

        # Summary stats
        st.markdown("**ROI Summary**")
        rs1, rs2, rs3, rs4 = st.columns(4)
        rs1.metric("Total Interventions", total_actions)
        rs2.metric("Resolved",            f"{resolved} ({success_rate}%)")
        rs3.metric("Total Cost",          f"₹{total_spent:,.0f}")
        rs4.metric("Avg Risk Reduced",    f"{risk_reduction:.1f}%")

    else:
        st.info("No interventions logged yet. Use **Action Tracker** to log actions and see performance metrics here.")

    # ── Top risks right now ───────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🚨 Top 5 Cases Needing Attention Right Now")
    top5 = high.sort_values("risk_score", ascending=False).head(5)
    from utils.data_engine import score_actions
    for rank, (_, row) in enumerate(top5.iterrows(), 1):
        rec   = score_actions(row, ds_key).iloc[0]
        rv_c  = "#ef4444"
        val_str = ""
        if val_col and val_col in row:
            val_str = f"· Value: ₹{int(row[val_col]):,}"
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.12);
             border-radius:9px;padding:10px 16px;margin-bottom:7px;
             display:flex;justify-content:space-between;align-items:center">
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:24px;height:24px;border-radius:50%;
                 background:rgba(239,68,68,0.15);display:flex;align-items:center;
                 justify-content:center;font-size:10px;color:#f87171;font-weight:700">
              #{rank}</div>
            <div>
              <div style="font-size:13px;font-weight:600;color:#dde3f0">{row['label']}</div>
              <div style="font-size:10px;color:#3d4f68">{row['id']} {val_str}</div>
            </div>
          </div>
          <div style="text-align:center">
            <div style="font-size:20px;font-weight:800;color:{rv_c}">
              {round(row['risk_score']*100)}%</div>
            <div style="font-size:10px;color:{rv_c}">High Risk</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:12px;color:{rec['color']};font-weight:600">{rec['label']}</div>
            <div style="font-size:10px;color:#3d4f68">ROI: {rec['roi']}%</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
