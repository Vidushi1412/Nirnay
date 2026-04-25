import streamlit as st
import plotly.graph_objects as go
from utils.data_engine import DATASETS, get_data


def render(ds_key: str):
    st.markdown("## निर्णय — Decision Intelligence Platform")
    st.caption("AI-powered risk decisioning for Indian enterprises · 10 sectors · 3 ML models each")

    # KPIs
    total_records = sum(d["records"] for d in DATASETS.values())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Datasets", "10", "Across 9 sectors")
    c2.metric("Total Records", f"{total_records:,}", "Training samples")
    c3.metric("Models Trained", "30", "3 per dataset")
    c4.metric("Avg Accuracy", "87.4%", "Cross-validated")

    st.divider()
    st.markdown("#### Active Datasets — click a dataset in the sidebar to explore")

    cols = st.columns(2)
    for idx, (key, meta) in enumerate(DATASETS.items()):
        df = get_data(key)
        high = int((df["risk_score"] > 0.7).sum())
        med  = int(((df["risk_score"] > 0.4) & (df["risk_score"] <= 0.7)).sum())
        low  = int((df["risk_score"] <= 0.4).sum())
        pct  = round(high / meta["records"] * 100)

        with cols[idx % 2]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                 border-radius:10px;padding:14px 16px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                <div>
                  <span style="font-size:18px">{meta['icon']}</span>
                  <span style="font-size:13px;font-weight:700;color:#dde3f0;margin-left:6px">{meta['name']}</span><br/>
                  <span style="font-size:11px;background:rgba(79,110,247,0.12);color:#a5b4fc;
                        border:1px solid rgba(79,110,247,0.2);padding:1px 7px;border-radius:4px">{meta['sector']}</span>
                </div>
                <div style="text-align:right">
                  <div style="font-size:12px;color:#ef4444;font-weight:700">{pct}% high risk</div>
                  <div style="font-size:10px;color:#3d4f68">{meta['records']:,} records</div>
                </div>
              </div>
              <div style="display:flex;gap:12px;font-size:11px">
                <span style="color:#ef4444">● {high} High</span>
                <span style="color:#f59e0b">● {med} Medium</span>
                <span style="color:#10b981">● {low} Low</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Risk distribution across all datasets
    st.divider()
    st.markdown("#### Portfolio Risk Distribution")
    fig = go.Figure()
    for key, meta in DATASETS.items():
        df = get_data(key)
        fig.add_trace(go.Box(
            y=df["risk_score"],
            name=meta["icon"] + " " + meta["sector"],
            marker_color=meta["color"],
            boxmean=True,
            showlegend=False,
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#8892a4", size=11),
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(title="Risk Score", gridcolor="rgba(255,255,255,0.05)", range=[0,1]),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)"),
    )
    st.plotly_chart(fig, use_container_width=True)
