import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_engine import DATASETS, get_data, get_actions, score_actions, train_models


def render(ds_key: str):
    meta    = DATASETS[ds_key]
    df      = get_data(ds_key)
    actions = get_actions(ds_key)

    st.markdown("## 📋 Reports")
    st.caption("Executive summary · Model performance · Action plan · Export")

    high = df[df["risk_score"] > 0.7]
    med  = df[(df["risk_score"] > 0.4) & (df["risk_score"] <= 0.7)]
    low  = df[df["risk_score"] <= 0.4]
    top_action = actions[0]
    total_cost = len(high) * top_action["cost"]
    risk_reduced = len(high) * top_action["impact"]

    # Executive Summary
    st.markdown(f"""
    <div style="background:rgba(79,110,247,0.07);border:1px solid rgba(79,110,247,0.18);
         border-radius:12px;padding:18px 20px;margin-bottom:16px">
      <div style="font-size:11px;font-weight:700;color:#818cf8;text-transform:uppercase;
           letter-spacing:.07em;margin-bottom:10px">Executive Summary — {meta['name']}</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
        {"".join(f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 12px"><div style="font-size:18px;font-weight:700;color:{c}">{v}</div><div style="font-size:10px;color:#3d4f68;margin-top:2px">{l}</div></div>'
                 for v,l,c in [
                     (f"{len(df):,}", "Records analysed", "#4f6ef7"),
                     (len(high), "High-risk cases", "#ef4444"),
                     (len(med),  "Medium-risk cases", "#f59e0b"),
                     (f"₹{total_cost:,.0f}", "Est. intervention cost", "#10b981"),
                     (f"{risk_reduced*100:.0f}pts", "Expected risk reduction", "#10b981"),
                     ("3", "Models benchmarked", "#818cf8"),
                 ])}
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Model Performance Comparison**")
        with st.spinner("Training models on dataset…"):
            model_results = train_models(ds_key)

        for model_name, res in model_results.items():
            if model_name.startswith("_"):
                continue
            badge_color = "#34d399" if "XGBoost" in model_name else "#60a5fa" if "Forest" in model_name else "#fbbf24"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                 border-radius:9px;padding:11px 14px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <span style="font-size:13px;font-weight:600;color:#dde3f0">{model_name}</span>
                <span style="background:{badge_color}22;color:{badge_color};border:1px solid {badge_color}44;
                      padding:2px 8px;border-radius:4px;font-size:10.5px;font-weight:600">
                  Accuracy {res['accuracy']}%</span>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
                {"".join(f'<div><div style="font-size:10px;color:#3d4f68">{k}</div><div style="font-size:13px;font-weight:600;color:#dde3f0">{v}%</div></div>'
                         for k,v in [("Precision",res['precision']),("Recall",res['recall']),("F1 Score",res['f1'])])}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Model accuracy comparison chart
        model_names = [k for k in model_results if not k.startswith("_")]
        accs = [model_results[k]["accuracy"] for k in model_names]
        fig = go.Figure(go.Bar(
            x=model_names, y=accs,
            marker_color=["#ef4444","#10b981","#4f6ef7"],
            text=[f"{v}%" for v in accs], textposition="outside",
            marker=dict(cornerradius=4),
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                          font=dict(color="#8892a4",size=11), height=180,
                          margin=dict(l=0,r=0,t=10,b=0),
                          yaxis=dict(title="Accuracy %", gridcolor="rgba(255,255,255,0.05)", range=[70,100]),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("**Action Allocation Plan**")
        alloc_rows = []
        for i, a in enumerate(actions):
            if i == 0:       assigned = len(high)
            elif i == len(actions)-1: assigned = len(low)
            else:            assigned = max(1, len(med) // max(1, len(actions)-2))
            alloc_rows.append({
                "Action":     a["label"],
                "Description":a["desc"],
                "Cases":      assigned,
                "Cost/Case":  f"₹{a['cost']:,}",
                "Total Cost": f"₹{assigned*a['cost']:,}",
            })
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, height=260, hide_index=True)

        st.divider()
        st.markdown("**Risk Level Breakdown**")
        fig2 = go.Figure(go.Bar(
            x=["High","Medium","Low"],
            y=[len(high), len(med), len(low)],
            marker_color=["#ef4444","#f59e0b","#10b981"],
            text=[len(high), len(med), len(low)],
            textposition="outside",
            marker=dict(cornerradius=4),
        ))
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                           font=dict(color="#8892a4",size=11), height=180,
                           margin=dict(l=0,r=0,t=10,b=0),
                           yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Export
    st.divider()
    st.markdown("**Export Decision Report**")
    ec1, ec2 = st.columns(2)

    with ec1:
        rows_export = []
        for _, row in df.iterrows():
            rec = score_actions(row, ds_key).iloc[0]
            rows_export.append({
                "ID": row["id"], "Label": row["label"],
                "Risk Score": f"{round(row['risk_score']*100)}%",
                "Risk Level": row["risk_level"],
                "Top Action": rec["label"],
                "Action Cost (Rs)": rec["cost"],
                "Est ROI %": rec["roi"],
                "Expected Risk Reduction (pts)": rec["expected_impact"],
            })
        full_csv = pd.DataFrame(rows_export).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Full Decision Report (CSV)",
                           full_csv, file_name=f"nirnay_{ds_key}_full_report.csv", mime="text/csv")

    with ec2:
        high_csv = pd.DataFrame(rows_export[:len(high)]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ High-Risk Cases Only (CSV)",
                           high_csv, file_name=f"nirnay_{ds_key}_high_risk.csv", mime="text/csv")
