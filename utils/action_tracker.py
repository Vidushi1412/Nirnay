"""
Nirnay — Action Tracker
Track interventions taken, outcomes, and ROI per case
"""
import streamlit as st
import pandas as pd
import json, os
from datetime import datetime, timedelta

TRACKER_DIR = "action_logs"
os.makedirs(TRACKER_DIR, exist_ok=True)


def _log_file(email: str) -> str:
    safe = email.replace("@","_").replace(".","_")
    return os.path.join(TRACKER_DIR, f"{safe}_actions.json")


def log_action(email: str, record_id: str, record_label: str, dataset: str,
               action: str, risk_before: float, cost: float, notes: str = ""):
    path = _log_file(email)
    logs = load_logs(email)
    entry_id = f"{record_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logs[entry_id] = {
        "record_id":    record_id,
        "record_label": record_label,
        "dataset":      dataset,
        "action":       action,
        "risk_before":  round(risk_before, 3),
        "risk_after":   None,
        "cost_rs":      cost,
        "notes":        notes,
        "status":       "Pending",
        "outcome":      None,
        "logged_at":    datetime.now().isoformat(),
        "followup_at":  (datetime.now() + timedelta(days=30)).isoformat(),
    }
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)
    return entry_id


def load_logs(email: str) -> dict:
    path = _log_file(email)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def update_outcome(email: str, entry_id: str, risk_after: float,
                   status: str, outcome: str):
    logs = load_logs(email)
    if entry_id in logs:
        logs[entry_id]["risk_after"]  = round(risk_after, 3)
        logs[entry_id]["status"]      = status
        logs[entry_id]["outcome"]     = outcome
        logs[entry_id]["resolved_at"] = datetime.now().isoformat()
    path = _log_file(email)
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)


def delete_log(email: str, entry_id: str):
    logs = load_logs(email)
    if entry_id in logs:
        del logs[entry_id]
    path = _log_file(email)
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)


def render(email: str):
    st.markdown("## 📌 Action Tracker")
    st.caption("Track every intervention — log actions, record outcomes, measure ROI")

    logs = load_logs(email)

    if not logs:
        st.info("No actions logged yet. Go to **Decision Engine**, select a record, and click **Log This Action**.")
        _render_empty_demo()
        return

    df_logs = pd.DataFrame(logs.values())
    df_logs["logged_at"] = pd.to_datetime(df_logs["logged_at"])
    df_logs = df_logs.sort_values("logged_at", ascending=False).reset_index(drop=True)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total        = len(df_logs)
    pending      = int((df_logs["status"] == "Pending").sum())
    resolved     = int((df_logs["status"] == "Resolved").sum())
    total_cost   = float(df_logs["cost_rs"].sum())
    resolved_df  = df_logs[df_logs["risk_after"].notna()]
    avg_reduction = 0.0
    if len(resolved_df) > 0:
        avg_reduction = float(
            ((resolved_df["risk_before"] - resolved_df["risk_after"]) /
             resolved_df["risk_before"] * 100).mean()
        )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Actions",    total)
    k2.metric("⏳ Pending",        pending)
    k3.metric("✅ Resolved",       resolved)
    k4.metric("💰 Total Spent",   f"₹{total_cost:,.0f}")
    k5.metric("📉 Avg Risk ↓",    f"{avg_reduction:.1f}%")

    st.divider()

    # ── Filter ────────────────────────────────────────────────────────────────
    f1, f2 = st.columns([2, 1])
    status_filter = f1.selectbox("Filter by status", ["All","Pending","Resolved","Failed"])
    if status_filter != "All":
        df_logs = df_logs[df_logs["status"] == status_filter]

    # ── Action cards ──────────────────────────────────────────────────────────
    for _, row in df_logs.iterrows():
        entry_id   = f"{row['record_id']}_{row['logged_at'].strftime('%Y%m%d%H%M%S')}"
        status_col = {"Pending":"#f59e0b","Resolved":"#10b981","Failed":"#ef4444"}.get(row["status"],"#8892a4")

        with st.expander(
            f"{'⏳' if row['status']=='Pending' else '✅' if row['status']=='Resolved' else '❌'} "
            f"{row['record_label']} — {row['action']} "
            f"({row['logged_at'].strftime('%d %b %Y')})",
            expanded=row["status"]=="Pending"
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risk Before", f"{round(row['risk_before']*100)}%")
            c2.metric("Risk After",  f"{round(row['risk_after']*100)}%" if row['risk_after'] else "—")
            c3.metric("Cost",        f"₹{row['cost_rs']:,.0f}")
            c4.metric("Status",      row["status"])

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                 border-radius:8px;padding:10px 14px;margin:8px 0;font-size:12px">
              <span style="color:#3d4f68">Dataset:</span>
              <span style="color:#dde3f0;margin-left:6px">{row['dataset']}</span>
              &nbsp;·&nbsp;
              <span style="color:#3d4f68">Record:</span>
              <span style="color:#dde3f0;margin-left:6px">{row['record_id']}</span>
              &nbsp;·&nbsp;
              <span style="color:#3d4f68">Follow-up:</span>
              <span style="color:#dde3f0;margin-left:6px">{row['followup_at'][:10]}</span>
            </div>
            """, unsafe_allow_html=True)

            if row["notes"]:
                st.markdown(f"**Notes:** {row['notes']}")

            if row["status"] == "Pending":
                st.markdown("**Update Outcome**")
                oc1, oc2, oc3 = st.columns(3)
                risk_after_val = oc1.slider(
                    "Risk after intervention",
                    0.0, 1.0,
                    float(row["risk_before"]) * 0.7,
                    0.01,
                    key=f"ra_{entry_id}"
                )
                new_status = oc2.selectbox(
                    "Outcome status",
                    ["Resolved","Failed"],
                    key=f"st_{entry_id}"
                )
                outcome_note = oc3.text_input(
                    "Outcome note",
                    placeholder="e.g. Customer retained",
                    key=f"on_{entry_id}"
                )
                if st.button("✅ Save Outcome", key=f"save_{entry_id}", type="primary"):
                    update_outcome(email, entry_id, risk_after_val, new_status, outcome_note)
                    st.success("Outcome recorded!")
                    st.rerun()

            if st.button("🗑️ Delete", key=f"del_{entry_id}"):
                delete_log(email, entry_id)
                st.rerun()

    st.divider()
    # ── Export ────────────────────────────────────────────────────────────────
    export_df = pd.DataFrame(logs.values())
    if len(export_df) > 0:
        st.download_button(
            "⬇️ Export Action Log CSV",
            export_df.to_csv(index=False).encode("utf-8"),
            file_name="nirnay_action_log.csv",
            mime="text/csv",
        )


def _render_empty_demo():
    st.markdown("#### How it works")
    steps = [
        ("1", "Go to Decision Engine", "Select any high-risk record"),
        ("2", "Choose an action",      "Pick from AI recommendations"),
        ("3", "Click Log Action",      "Action is saved to your tracker"),
        ("4", "Follow up in 30 days",  "Update the outcome — did it work?"),
        ("5", "See your ROI",          "Track cost spent vs risk reduced"),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
             border-bottom:1px solid rgba(255,255,255,0.05)">
          <div style="width:28px;height:28px;border-radius:50%;
               background:rgba(79,110,247,0.15);border:1px solid rgba(79,110,247,0.3);
               display:flex;align-items:center;justify-content:center;
               font-size:12px;font-weight:700;color:#818cf8;flex-shrink:0">{num}</div>
          <div>
            <div style="font-size:13px;font-weight:600;color:#dde3f0">{title}</div>
            <div style="font-size:11px;color:#3d4f68">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
