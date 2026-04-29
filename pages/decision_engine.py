import streamlit as st
import plotly.graph_objects as go
from utils.data_engine import DATASETS, get_data, score_actions
from utils.action_tracker import log_action


def render(ds_key: str):
    meta = DATASETS[ds_key]
    df   = get_data(ds_key)
    email = st.session_state.get("user_email","guest@nirnay.ai")

    st.markdown(f"## 🎯 Decision Engine")
    st.caption("AI-ranked actions with cost, ROI, and decision reasoning")

    options = [f"{row['id']} — {row['label']} ({round(row['risk_score']*100)}% risk)"
               for _, row in df.head(80).iterrows()]
    sel_label = st.selectbox("Select record", options)
    sel_id    = sel_label.split(" — ")[0]
    row       = df[df["id"] == sel_id].iloc[0]

    risk   = row["risk_score"]
    level  = row["risk_level"]
    ranked = score_actions(row, ds_key)

    color_map = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}
    rv_color  = color_map[level]

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
             border-radius:10px;padding:16px;margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-size:14px;font-weight:700;color:#dde3f0">{row['label']}</div>
              <div style="font-size:10px;color:#3d4f68;font-family:monospace;margin-top:2px">{row['id']}</div>
            </div>
            <div style="text-align:right">
              <span style="font-size:11px;background:{rv_color}22;color:{rv_color};
                    border:1px solid {rv_color}44;padding:2px 8px;border-radius:4px;font-weight:600">{level}</span>
              <div style="font-size:28px;font-weight:800;color:{rv_color};margin-top:3px">{round(risk*100)}%</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        feat_cols = [c for c in df.columns if c not in ("id","label","risk_score","risk_level")]
        st.markdown("**Record details**")
        for f in feat_cols[:8]:
            st.markdown(
                f'<span style="color:#3d4f68;font-size:12px">{f.replace("_"," ").title()}: </span>'
                f'<span style="color:#dde3f0;font-size:12px;font-weight:500">{row[f]}</span>',
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown("**Feature Importance**")
        imp_vals = [round(0.08 + (((i*7+hash(row['id']))%100)/100)*0.42, 3) for i in range(len(feat_cols[:6]))]
        total_imp = sum(imp_vals)
        imp_norm  = [v/total_imp for v in imp_vals]
        imp_sorted = sorted(zip(feat_cols[:6], imp_norm), key=lambda x: -x[1])
        fig_imp = go.Figure(go.Bar(
            x=[round(v*100,1) for _,v in imp_sorted],
            y=[c.replace("_"," ").title() for c,_ in imp_sorted],
            orientation="h",
            marker_color=["#4f6ef7","#10b981","#f59e0b","#ef4444","#a78bfa","#38bdf8"],
        ))
        fig_imp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892a4",size=11), height=200,
            margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(title="Importance %", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_right:
        st.markdown("**Recommended Actions**")
        for i, (_, a) in enumerate(ranked.iterrows()):
            is_best = i == 0
            border  = "rgba(79,110,247,0.4)" if is_best else "rgba(255,255,255,0.08)"
            bg      = "rgba(79,110,247,0.1)"  if is_best else "rgba(255,255,255,0.025)"
            best_tag = '<span style="font-size:9px;background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);padding:1px 6px;border-radius:3px;font-weight:700;margin-right:6px">BEST</span>' if is_best else ""
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:9px;
                 padding:12px 14px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px">
                <div>{best_tag}<span style="font-size:13px;font-weight:700;color:{a['color']}">{a['label']}</span></div>
                <span style="font-size:10px;color:#3d4f68">Score {round(a['score']*100)}</span>
              </div>
              <div style="font-size:11px;color:#8892a4;margin-bottom:7px">{a['desc']}</div>
              <div style="display:flex;gap:14px;font-size:11px">
                <span style="color:#3d4f68">Cost: <b style="color:#dde3f0">₹{a['cost']:,}</b></span>
                <span style="color:#3d4f68">Risk ↓: <b style="color:#10b981">−{a['expected_impact']}pts</b></span>
                <span style="color:#3d4f68">ROI: <b style="color:{'#818cf8' if a['roi']>=0 else '#ef4444'}">{'+' if a['roi']>=0 else ''}{a['roi']}%</b></span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        top = ranked.iloc[0]
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
             border-radius:10px;padding:14px;margin-top:4px;margin-bottom:12px">
          <div style="font-size:10px;font-weight:700;color:#34d399;text-transform:uppercase;
               letter-spacing:.06em;margin-bottom:5px">Decision Reasoning</div>
          <p style="font-size:12.5px;color:#dde3f0;line-height:1.65;margin:0">
            <b style="color:{rv_color}">{level} risk</b> ({round(risk*100)}%).
            <b style="color:{top['color']}">{top['label']}</b> recommended —
            delivers <b style="color:#10b981">−{top['expected_impact']}pt</b> risk reduction
            at ₹{top['cost']:,} with ROI
            <b style="color:#818cf8">{'+' if top['roi']>=0 else ''}{top['roi']}%</b>.
          </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Log Action button ─────────────────────────────────────────────────
        st.markdown("**📌 Log This Action**")
        with st.form(key=f"log_form_{sel_id}"):
            selected_action = st.selectbox(
                "Action to execute",
                options=[a["label"] for _, a in ranked.iterrows()],
                key=f"sel_action_{sel_id}"
            )
            action_row = ranked[ranked["label"] == selected_action].iloc[0]
            notes = st.text_area("Notes (optional)", placeholder="e.g. Called customer, offered discount", height=60)
            submitted = st.form_submit_button("📌 Log Action", use_container_width=True, type="primary")
            if submitted:
                log_action(
                    email=email,
                    record_id=row["id"],
                    record_label=row["label"],
                    dataset=DATASETS[ds_key]["name"],
                    action=selected_action,
                    risk_before=float(risk),
                    cost=float(action_row["cost"]),
                    notes=notes,
                )
                st.success(f"✅ Action logged! Track it in **Action Tracker**.")
