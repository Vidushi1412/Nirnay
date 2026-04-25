import streamlit as st
import pandas as pd
from utils.data_engine import DATASETS, get_data, score_actions


def render(ds_key: str):
    meta = DATASETS[ds_key]
    df   = get_data(ds_key)

    st.markdown("## ✅ Human Review")
    st.caption("Override or confirm AI recommendations before execution — human-in-the-loop workflow")

    targets = df[df["risk_score"] > 0.72].sort_values("risk_score", ascending=False).head(10)

    # Session state for review decisions
    for _, row in targets.iterrows():
        for key in [f"rev_status_{row['id']}", f"rev_note_{row['id']}"]:
            if key not in st.session_state:
                st.session_state[key] = "pending" if "status" in key else ""

    approved = sum(1 for _, r in targets.iterrows() if st.session_state.get(f"rev_status_{r['id']}") == "approved")
    rejected = sum(1 for _, r in targets.iterrows() if st.session_state.get(f"rev_status_{r['id']}") == "rejected")
    pending  = len(targets) - approved - rejected

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total in Queue", len(targets))
    k2.metric("✅ Approved",    approved)
    k3.metric("❌ Rejected",    rejected)
    k4.metric("⏳ Pending",     pending)

    st.divider()

    color_map = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}

    for _, row in targets.iterrows():
        rec    = score_actions(row, ds_key).iloc[0]
        status = st.session_state.get(f"rev_status_{row['id']}", "pending")
        level  = row["risk_level"]
        rv_c   = color_map[level]

        border = {"approved":"rgba(16,185,129,0.3)","rejected":"rgba(239,68,68,0.25)"}.get(status,"rgba(255,255,255,0.08)")
        bg     = {"approved":"rgba(16,185,129,0.05)","rejected":"rgba(239,68,68,0.04)"}.get(status,"rgba(255,255,255,0.025)")

        with st.container():
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:12px;padding:16px;margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:10px">
                  <div style="width:30px;height:30px;border-radius:8px;background:{meta['color']}22;
                       border:1px solid {meta['color']}44;display:flex;align-items:center;justify-content:center;
                       font-size:14px">{meta['icon']}</div>
                  <div>
                    <div style="font-size:14px;font-weight:700;color:#dde3f0">{row['label']}</div>
                    <div style="font-size:10px;color:#3d4f68;font-family:monospace">{row['id']}</div>
                  </div>
                </div>
                <div style="text-align:right">
                  <span style="font-size:10px;background:{rv_c}22;color:{rv_c};border:1px solid {rv_c}44;
                        padding:2px 7px;border-radius:4px;font-weight:600">{level}</span>
                  <div style="font-size:22px;font-weight:800;color:{rv_c};margin-top:3px">{round(row['risk_score']*100)}%</div>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:10px 12px;
                   display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-size:10px;color:#3d4f68">AI Recommends</div>
                  <div style="font-size:13px;font-weight:700;color:{rec['color']}">{rec['label']}</div>
                  <div style="font-size:11px;color:#8892a4">{rec['desc']}</div>
                </div>
                <div style="text-align:right">
                  <div style="font-size:10px;color:#3d4f68">Expected Outcome</div>
                  <div style="font-size:12px;color:#10b981;font-weight:600">Risk ↓ {rec['expected_impact']}pts</div>
                  <div style="font-size:11px;color:#8892a4">ROI: {'+' if rec['roi']>=0 else ''}{rec['roi']}%</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            note = st.text_area("Notes / Override reason (optional)",
                                value=st.session_state.get(f"rev_note_{row['id']}", ""),
                                key=f"note_area_{row['id']}", height=60,
                                label_visibility="collapsed",
                                placeholder="Add notes or override reason…")
            st.session_state[f"rev_note_{row['id']}"] = note

            bc1, bc2, bc3 = st.columns([1, 1, 2])
            if bc1.button(f"✅ Approve" if status != "approved" else "✓ Approved",
                          key=f"approve_{row['id']}",
                          type="primary" if status == "approved" else "secondary"):
                st.session_state[f"rev_status_{row['id']}"] = "approved"
                st.rerun()

            if bc2.button(f"❌ Reject" if status != "rejected" else "✗ Rejected",
                          key=f"reject_{row['id']}"):
                st.session_state[f"rev_status_{row['id']}"] = "rejected"
                st.rerun()

            if status != "pending":
                if bc3.button("↩ Reset", key=f"reset_{row['id']}"):
                    st.session_state[f"rev_status_{row['id']}"] = "pending"
                    st.rerun()

    # Export review decisions
    st.divider()
    if st.button("Export Review Log as CSV"):
        review_rows = []
        for _, row in targets.iterrows():
            review_rows.append({
                "ID": row["id"],
                "Label": row["label"],
                "Risk Score": f"{round(row['risk_score']*100)}%",
                "Risk Level": row["risk_level"],
                "AI Recommendation": score_actions(row, ds_key).iloc[0]["label"],
                "Review Status": st.session_state.get(f"rev_status_{row['id']}", "pending"),
                "Notes": st.session_state.get(f"rev_note_{row['id']}", ""),
            })
        csv = pd.DataFrame(review_rows).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Review Log", csv,
                           file_name=f"nirnay_{ds_key}_review_log.csv",
                           mime="text/csv")
