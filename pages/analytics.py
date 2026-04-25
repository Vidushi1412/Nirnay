import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_engine import DATASETS, get_data, score_actions

CAT_FIELDS = ["city","state","sector","plan_type","loan_type","payment_method","crop_type",
              "diagnosis","route_type","platform","geography","origin_city","insurance",
              "irrigation","focus_area","location_tier","project_stage","sector_type",
              "discharge_type","weather_risk","city_tier","policy_type"]


def hex_to_rgba(hex_color, alpha=0.08):
    """Convert hex color to rgba string safely."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"rgba({r},{g},{b},{alpha})"
    return f"rgba(79,110,247,{alpha})"


def find_cat(df):
    return next((f for f in CAT_FIELDS if f in df.columns), None)


def render(ds_key: str):
    meta = DATASETS[ds_key]
    df   = get_data(ds_key)

    st.markdown("## 📊 Analytics")
    st.caption("Segment-level risk insights, trends, and critical case identification")

    high  = int((df["risk_score"] > 0.7).sum())
    med   = int(((df["risk_score"] > 0.4) & (df["risk_score"] <= 0.7)).sum())
    low   = int((df["risk_score"] <= 0.4).sum())
    avg_r = round(df["risk_score"].mean() * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Avg Risk", f"{avg_r}%")
    c2.metric("🔴 High Risk",       high)
    c3.metric("🟡 Medium Risk",     med)
    c4.metric("🟢 Low Risk",        low)

    st.divider()

    cat_field = find_cat(df)
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        if cat_field:
            st.markdown(f"**Risk by {cat_field.replace('_', ' ').title()}**")
            grp = (df.groupby(cat_field)["risk_score"]
                     .agg(["mean","count"])
                     .rename(columns={"mean":"avg_risk","count":"records"})
                     .sort_values("avg_risk", ascending=False)
                     .head(8))

            colors = ["#ef4444" if v>0.7 else "#f59e0b" if v>0.4 else "#10b981"
                      for v in grp["avg_risk"]]
            fig = go.Figure(go.Bar(
                x=grp.index.tolist(),
                y=(grp["avg_risk"]*100).round(1).tolist(),
                marker_color=colors,
                text=(grp["avg_risk"]*100).round(1).tolist(),
                texttemplate="%{text}%", textposition="outside",
                marker=dict(cornerradius=4),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#8892a4",size=10), height=240,
                margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.03)"),
                yaxis=dict(title="Avg Risk %", gridcolor="rgba(255,255,255,0.05)"),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("**Monthly Risk Trend (simulated)**")
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        slices = [df.iloc[i::12]["risk_score"].mean()*100 for i in range(12)]

        # Fix: use hex_to_rgba instead of string concatenation
        fill_color = hex_to_rgba(meta["color"], 0.12)

        fig2 = go.Figure(go.Scatter(
            x=months,
            y=[round(v,1) for v in slices],
            mode="lines+markers",
            line=dict(color=meta["color"], width=2),
            marker=dict(size=5, color=meta["color"]),
            fill="tozeroy",
            fillcolor=fill_color,
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#8892a4",size=10), height=160,
            margin=dict(l=0,r=0,t=10,b=0),
            yaxis=dict(title="Avg Risk %", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Risk Distribution**")
        fig3 = go.Figure(go.Pie(
            labels=["High","Medium","Low"],
            values=[high, med, low],
            hole=0.65,
            marker_colors=["#ef4444","#f59e0b","#10b981"],
            textinfo="percent+label",
            textfont=dict(size=11, color="#dde3f0"),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892a4"), height=180,
            margin=dict(l=0,r=0,t=0,b=0),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Segment deep-dive
    if cat_field:
        st.divider()
        st.markdown(f"**Segment Deep-Dive by {cat_field.replace('_',' ').title()}**")
        grp_full = (df.groupby(cat_field)["risk_score"]
                      .agg(["mean","count",
                            lambda x: int((x>0.7).sum()),
                            lambda x: int((x<=0.4).sum())])
                      .rename(columns={"mean":"Avg Risk","count":"Records",
                                       "<lambda_0>":"High Risk","<lambda_1>":"Low Risk"})
                      .sort_values("Avg Risk", ascending=False))
        grp_full["Avg Risk"] = (grp_full["Avg Risk"]*100).round(1).astype(str) + "%"
        st.dataframe(grp_full, use_container_width=True, height=260)

    # Top 5 critical
    st.divider()
    st.markdown("**Top 5 Critical Cases — Immediate Action Required**")
    top5 = df.sort_values("risk_score", ascending=False).head(5)
    for rank, (_, row) in enumerate(top5.iterrows(), 1):
        rec  = score_actions(row, ds_key).iloc[0]
        rv_c = "#ef4444" if row["risk_level"]=="High" else "#f59e0b"
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.12);
             border-radius:9px;padding:10px 14px;margin-bottom:7px;
             display:flex;justify-content:space-between;align-items:center">
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:22px;height:22px;border-radius:50%;
                 background:rgba(239,68,68,0.15);display:flex;align-items:center;
                 justify-content:center;font-size:10px;color:#f87171;font-weight:700">#{rank}</div>
            <div>
              <div style="font-size:13px;font-weight:600;color:#dde3f0">{row['label']}</div>
              <div style="font-size:10px;color:#3d4f68;font-family:monospace">{row['id']}</div>
            </div>
          </div>
          <div style="text-align:center">
            <div style="font-size:20px;font-weight:800;color:{rv_c}">{round(row['risk_score']*100)}%</div>
            <span style="font-size:10px;color:{rv_c}">{row['risk_level']} Risk</span>
          </div>
          <div style="text-align:right">
            <div style="font-size:12px;color:{rec['color']};font-weight:600">{rec['label']}</div>
            <div style="font-size:10px;color:#3d4f68">ROI: {rec['roi']}%</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
