import streamlit as st
import pandas as pd
from utils.data_engine import DATASETS, get_data, score_actions


def render(ds_key: str):
    meta = DATASETS[ds_key]
    df   = get_data(ds_key)

    st.markdown(f"## {meta['icon']} {meta['name']}")
    st.caption(f"{meta['sector']} · {meta['records']:,} records · Risk monitoring dashboard")

    high = int((df["risk_score"] > 0.7).sum())
    med  = int(((df["risk_score"] > 0.4) & (df["risk_score"] <= 0.7)).sum())
    low  = int((df["risk_score"] <= 0.4).sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",  f"{len(df):,}")
    c2.metric("🔴 High Risk",   high,  delta=f"{round(high/len(df)*100)}% of portfolio", delta_color="inverse")
    c3.metric("🟡 Medium Risk", med)
    c4.metric("🟢 Low Risk",    low)

    st.divider()

    fc1, fc2, fc3 = st.columns([3, 2, 2])
    search  = fc1.text_input("🔍 Search ID or label", "")
    rl_filt = fc2.selectbox("Risk Level", ["All", "High", "Medium", "Low"])
    sort_by = fc3.selectbox("Sort by", ["Risk: High → Low", "Risk: Low → High"])

    filtered = df.copy()
    if search:
        filtered = filtered[
            filtered["id"].str.contains(search, case=False) |
            filtered["label"].str.contains(search, case=False)
        ]
    if rl_filt != "All":
        filtered = filtered[filtered["risk_level"] == rl_filt]
    if "High → Low" in sort_by:
        filtered = filtered.sort_values("risk_score", ascending=False)
    else:
        filtered = filtered.sort_values("risk_score", ascending=True)

    feat_cols = [c for c in df.columns if c not in ("id","label","risk_score","risk_level")]
    display_cols = feat_cols[:3]

    rows_display = []
    for _, row in filtered.head(200).iterrows():
        ranked = score_actions(row, ds_key)
        top_action = ranked.iloc[0]
        rows_display.append({
            "ID": row["id"],
            "Label": row["label"],
            "Risk Score": f"{round(row['risk_score']*100)}%",
            "Level": row["risk_level"],
            **{c: row[c] for c in display_cols},
            "Top Action": top_action["label"],
            "ROI": f"{top_action['roi']}%",
        })

    disp_df = pd.DataFrame(rows_display)

    def color_level(val):
        if val == "High":   return "color: #f87171; font-weight: 600"
        if val == "Medium": return "color: #fbbf24; font-weight: 600"
        return "color: #34d399; font-weight: 600"

    # Use .map() instead of deprecated .applymap()
    styled = disp_df.style.map(color_level, subset=["Level"])
    st.dataframe(styled, use_container_width=True, height=440, hide_index=True)

    st.caption(f"Showing {len(disp_df)} of {len(filtered)} filtered records")

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export Filtered CSV", csv,
                       file_name=f"nirnay_{ds_key}_risk_monitor.csv",
                       mime="text/csv")
