"""
Nirnay — CSV Upload Engine
Upload your own business data, auto-detect columns, run risk scoring
"""
import streamlit as st
import pandas as pd
import numpy as np
import json, os
from datetime import datetime

UPLOADS_DIR = "uploaded_datasets"
os.makedirs(UPLOADS_DIR, exist_ok=True)


def _user_file(email: str) -> str:
    safe = email.replace("@","_").replace(".","_")
    return os.path.join(UPLOADS_DIR, f"{safe}_datasets.json")


def save_user_dataset(email: str, name: str, df: pd.DataFrame, risk_col: str):
    path = _user_file(email)
    datasets = load_user_datasets(email)
    datasets[name] = {
        "uploaded": datetime.now().isoformat(),
        "rows": len(df),
        "columns": list(df.columns),
        "risk_col": risk_col,
        "csv_path": os.path.join(UPLOADS_DIR, f"{email.replace('@','_').replace('.','_')}_{name}.csv"),
    }
    df.to_csv(datasets[name]["csv_path"], index=False)
    with open(path, "w") as f:
        json.dump(datasets, f, indent=2)


def load_user_datasets(email: str) -> dict:
    path = _user_file(email)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def load_dataset_df(email: str, name: str) -> pd.DataFrame | None:
    datasets = load_user_datasets(email)
    if name not in datasets:
        return None
    csv_path = datasets[name]["csv_path"]
    if not os.path.exists(csv_path):
        return None
    return pd.read_csv(csv_path)


def delete_user_dataset(email: str, name: str):
    datasets = load_user_datasets(email)
    if name in datasets:
        csv_path = datasets[name].get("csv_path","")
        if os.path.exists(csv_path):
            os.remove(csv_path)
        del datasets[name]
        path = _user_file(email)
        with open(path, "w") as f:
            json.dump(datasets, f, indent=2)


def auto_score(df: pd.DataFrame, risk_col: str | None) -> pd.DataFrame:
    """If no risk column, generate a synthetic risk score from numeric features."""
    df = df.copy()
    if risk_col and risk_col in df.columns:
        col = pd.to_numeric(df[risk_col], errors="coerce").fillna(0)
        mn, mx = col.min(), col.max()
        df["risk_score"] = ((col - mn) / (mx - mn + 1e-9)).round(3)
    else:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            scores = np.zeros(len(df))
            for c in num_cols[:6]:
                col = pd.to_numeric(df[c], errors="coerce").fillna(0)
                mn, mx = col.min(), col.max()
                norm = (col - mn) / (mx - mn + 1e-9)
                scores += norm.values
            scores = scores / len(num_cols[:6])
            df["risk_score"] = np.round(scores, 3)
        else:
            df["risk_score"] = np.round(np.random.uniform(0.1, 0.9, len(df)), 3)

    df["risk_level"] = df["risk_score"].apply(
        lambda v: "High" if v > 0.7 else ("Medium" if v > 0.4 else "Low")
    )
    if "id" not in df.columns:
        df.insert(0, "id", [f"REC{i+1:04d}" for i in range(len(df))])
    if "label" not in df.columns:
        df.insert(1, "label", df["id"])
    return df


def render(email: str):
    st.markdown("## 📂 Upload Your Data")
    st.caption("Upload your own CSV file and get AI risk scores and decisions instantly")

    user_datasets = load_user_datasets(email)

    # ── Upload section ────────────────────────────────────────────────────────
    with st.expander("➕ Upload New Dataset", expanded=len(user_datasets) == 0):
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Upload any business data — customers, loans, orders, patients, etc."
        )

        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded)
                st.success(f"✅ Loaded {len(df_raw):,} rows × {len(df_raw.columns)} columns")
                st.dataframe(df_raw.head(5), use_container_width=True, hide_index=True)

                col1, col2 = st.columns(2)
                with col1:
                    ds_name = st.text_input(
                        "Dataset name",
                        value=uploaded.name.replace(".csv","").replace("_"," ").title(),
                        key="ds_name_input"
                    )
                with col2:
                    risk_options = ["Auto-generate risk score"] + list(df_raw.columns)
                    risk_col_sel = st.selectbox(
                        "Which column is your risk/target column?",
                        risk_options,
                        key="risk_col_sel"
                    )

                risk_col = None if risk_col_sel == "Auto-generate risk score" else risk_col_sel

                st.markdown("**Column Overview**")
                col_info = pd.DataFrame({
                    "Column": df_raw.columns,
                    "Type": df_raw.dtypes.astype(str).values,
                    "Non-null": df_raw.count().values,
                    "Sample": [str(df_raw[c].iloc[0]) if len(df_raw) > 0 else "" for c in df_raw.columns],
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)

                if st.button("🚀 Process & Save Dataset", type="primary", use_container_width=True):
                    if not ds_name:
                        st.error("Enter a dataset name.")
                    else:
                        with st.spinner("Processing your data..."):
                            df_scored = auto_score(df_raw, risk_col)
                            save_user_dataset(email, ds_name, df_scored, risk_col or "auto")
                        st.success(f"✅ Dataset '{ds_name}' saved with {len(df_scored):,} records!")
                        st.rerun()

            except Exception as e:
                st.error(f"Error reading file: {e}")

    # ── Existing datasets ─────────────────────────────────────────────────────
    if user_datasets:
        st.divider()
        st.markdown("### Your Datasets")

        for ds_name, meta in user_datasets.items():
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03);
                         border:1px solid rgba(255,255,255,0.07);
                         border-radius:10px;padding:12px 16px;">
                      <div style="font-size:14px;font-weight:700;color:#dde3f0">{ds_name}</div>
                      <div style="font-size:11px;color:#3d4f68;margin-top:3px">
                        {meta['rows']:,} records · {len(meta['columns'])} columns ·
                        Uploaded {meta['uploaded'][:10]}
                      </div>
                      <div style="font-size:11px;color:#8892a4;margin-top:2px">
                        Columns: {', '.join(meta['columns'][:5])}{'...' if len(meta['columns'])>5 else ''}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    df_preview = load_dataset_df(email, ds_name)
                    if df_preview is not None:
                        csv = df_preview.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Export",
                            csv,
                            file_name=f"{ds_name}.csv",
                            mime="text/csv",
                            key=f"dl_{ds_name}"
                        )
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{ds_name}"):
                        delete_user_dataset(email, ds_name)
                        st.rerun()

    else:
        st.info("No datasets uploaded yet. Upload your first CSV above.")

    # ── Sample templates ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Download Sample Templates")
    st.caption("Don't have data? Download a template, fill it with your data, and upload.")

    tc1, tc2, tc3 = st.columns(3)

    templates = {
        "Customer Churn": pd.DataFrame({
            "customer_id": ["C001","C002","C003"],
            "monthly_spend": [1200, 450, 890],
            "tenure_months": [24, 6, 36],
            "complaints": [2, 0, 1],
            "plan_type": ["Premium","Basic","Standard"],
            "city": ["Mumbai","Delhi","Bangalore"],
            "churned": [1, 0, 0],
        }),
        "Loan Default": pd.DataFrame({
            "borrower_id": ["L001","L002","L003"],
            "loan_amount": [500000, 150000, 1200000],
            "income": [80000, 35000, 200000],
            "cibil_score": [720, 580, 800],
            "emi_ratio": [0.35, 0.55, 0.28],
            "employment_years": [5, 2, 12],
            "defaulted": [0, 1, 0],
        }),
        "Order Fraud": pd.DataFrame({
            "order_id": ["O001","O002","O003"],
            "order_value": [2500, 45000, 800],
            "payment_method": ["UPI","COD","Credit Card"],
            "seller_rating": [4.5, 2.1, 4.8],
            "returns_count": [0, 5, 1],
            "address_verified": [1, 0, 1],
            "is_fraud": [0, 1, 0],
        }),
    }

    for col, (name, tdf) in zip([tc1, tc2, tc3], templates.items()):
        with col:
            st.download_button(
                f"⬇️ {name}",
                tdf.to_csv(index=False).encode("utf-8"),
                file_name=f"template_{name.lower().replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"tpl_{name}"
            )
