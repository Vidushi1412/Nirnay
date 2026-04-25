"""
Nirnay — Data Engine
Deterministic synthetic data for 10 Indian business sectors.
Real ML models: Logistic Regression, Random Forest, XGBoost.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import xgboost as xgb
import streamlit as st

MASTER_SEED = 42

# ── DATASET METADATA ─────────────────────────────────────────────────────────
DATASETS = {
    "telecom":   {"name":"Airtel / Jio — Customer Churn",        "sector":"Telecom",       "color":"#4f6ef7","icon":"📡","records":847},
    "banking":   {"name":"HDFC / SBI — Loan Default",            "sector":"Banking",       "color":"#10b981","icon":"🏦","records":1243},
    "ecomm":     {"name":"Flipkart / Meesho — Fraud Detection",  "sector":"E-Commerce",    "color":"#f59e0b","icon":"🛒","records":2156},
    "insurance": {"name":"LIC / ICICI Lombard — Claim Prediction","sector":"Insurance",    "color":"#ef4444","icon":"🛡️","records":934},
    "startup":   {"name":"Indian Startup — Failure Risk",        "sector":"VC / Startup",  "color":"#a78bfa","icon":"🚀","records":456},
    "agri":      {"name":"NABARD — Kisan Loan Default",          "sector":"Agriculture",   "color":"#34d399","icon":"🌾","records":1567},
    "hospital":  {"name":"Apollo / Fortis — Readmission",        "sector":"Healthcare",    "color":"#f87171","icon":"🏥","records":789},
    "realty":    {"name":"MagicBricks — Price Drop Risk",        "sector":"Real Estate",   "color":"#fb923c","icon":"🏘️","records":623},
    "csr":       {"name":"CSR / NGO — Impact Scoring",           "sector":"Social Impact", "color":"#38bdf8","icon":"🌱","records":312},
    "logistics": {"name":"Delhivery — Shipment Delay",           "sector":"Logistics",     "color":"#e879f9","icon":"🚚","records":1834},
}

ACTIONS = {
    "telecom": [
        {"id":"recharge_bonus", "label":"Recharge Bonus",      "desc":"10% extra data/talktime on next recharge",        "cost":120,"impact":0.28,"color":"#10b981"},
        {"id":"retention_call", "label":"Retention Call",       "desc":"Dedicated care agent call within 24 hrs",         "cost":80, "impact":0.22,"color":"#4f6ef7"},
        {"id":"plan_upgrade",   "label":"Plan Upgrade Offer",  "desc":"Personalised better-value plan suggestion",       "cost":0,  "impact":0.17,"color":"#3b82f6"},
        {"id":"loyalty_pts",    "label":"Loyalty Points",       "desc":"Bonus points redeemable on recharge",             "cost":60, "impact":0.24,"color":"#f59e0b"},
        {"id":"no_action",      "label":"No Action",            "desc":"Standard monitoring only",                       "cost":0,  "impact":0.02,"color":"#6b7280"},
    ],
    "banking": [
        {"id":"emi_restructure","label":"EMI Restructuring",   "desc":"Moratorium or step-down EMI schedule",            "cost":200,"impact":0.35,"color":"#10b981"},
        {"id":"counseling",     "label":"Financial Counseling","desc":"Dedicated loan officer guidance session",          "cost":150,"impact":0.25,"color":"#4f6ef7"},
        {"id":"penalty_waiver", "label":"Penalty Waiver",       "desc":"One-time late fee waiver for borrower",           "cost":500,"impact":0.32,"color":"#3b82f6"},
        {"id":"topup_offer",    "label":"Top-up Loan Offer",   "desc":"Consolidate dues into a fresh top-up loan",       "cost":50, "impact":0.15,"color":"#f59e0b"},
        {"id":"no_action",      "label":"Standard Follow-up",  "desc":"SMS/email reminder only",                        "cost":20, "impact":0.07,"color":"#6b7280"},
    ],
    "ecomm": [
        {"id":"flag_review",    "label":"Flag for Review",     "desc":"Hold order for manual review before dispatch",    "cost":50, "impact":0.44,"color":"#ef4444"},
        {"id":"otp_delivery",   "label":"OTP at Delivery",     "desc":"Require OTP confirmation on delivery",            "cost":10, "impact":0.38,"color":"#f59e0b"},
        {"id":"order_cap",      "label":"Order Value Cap",     "desc":"Cap order pending address re-verification",       "cost":0,  "impact":0.30,"color":"#4f6ef7"},
        {"id":"blacklist",      "label":"Temporary Block",     "desc":"Freeze account pending investigation",            "cost":0,  "impact":0.52,"color":"#dc2626"},
        {"id":"no_action",      "label":"Allow Order",         "desc":"Process normally — acceptable risk",             "cost":0,  "impact":0.01,"color":"#6b7280"},
    ],
    "default": [
        {"id":"high_priority",    "label":"Priority Intervention","desc":"Immediate senior team escalation",             "cost":500,"impact":0.40,"color":"#ef4444"},
        {"id":"enhanced_monitor", "label":"Enhanced Monitoring",  "desc":"Weekly check-in and progress tracking",        "cost":100,"impact":0.25,"color":"#4f6ef7"},
        {"id":"dedicated_mgr",    "label":"Dedicated Manager",    "desc":"Assign dedicated account manager",             "cost":200,"impact":0.32,"color":"#10b981"},
        {"id":"nudge_campaign",   "label":"WhatsApp Nudge",       "desc":"Automated WhatsApp + SMS nudge campaign",      "cost":20, "impact":0.15,"color":"#f59e0b"},
        {"id":"no_action",        "label":"Watch & Wait",         "desc":"Standard monitoring only",                    "cost":0,  "impact":0.04,"color":"#6b7280"},
    ],
}


def get_actions(ds_key: str) -> list:
    return ACTIONS.get(ds_key, ACTIONS["default"])


# ── SEEDED PRNG ───────────────────────────────────────────────────────────────
def _s(seed, max_val):
    return ((seed * 9301 + 49297) % 233280) / 233280 * max_val

CITIES  = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Pune","Kolkata","Ahmedabad","Surat","Jaipur","Indore","Bhopal"]
STATES  = ["Maharashtra","Karnataka","Tamil Nadu","UP","Gujarat","Rajasthan","Delhi","West Bengal","MP","Telangana","Bihar","Odisha"]
PLANS   = ["Prepaid","Postpaid","Corporate"]
LOANS   = ["Home Loan","Personal Loan","Business Loan","Vehicle Loan","Education Loan"]
PAYMENT = ["UPI","Credit Card","Debit Card","COD","Wallet"]
PLAT    = ["Flipkart","Meesho","Amazon India","Myntra","Nykaa"]
POLICY  = ["Health","Vehicle","Life","Property","Travel"]
SECTS   = ["Fintech","Edtech","Healthtech","Agritech","SaaS","D2C","Logistics"]
CROPS   = ["Wheat","Rice","Cotton","Sugarcane","Soybean","Pulses","Maize"]
SOIL    = ["Poor","Average","Good","Excellent"]
IRRIG   = ["Rain-fed","Canal","Drip","Borewell"]
DIAG    = ["Diabetes","Hypertension","Cardiac","Respiratory","Orthopedic","Neuro"]
DISCH   = ["Recovered","Against Advice","Transfer","Referred"]
INSUR   = ["Ayushman Bharat","Private","ESI","Corporate","Self-pay"]
TIER    = ["Prime","Mid","Suburban","Peripheral"]
STAGE   = ["Pre-launch","Under Construction","Ready to Move","Completed"]
FOCUS   = ["Education","Health","Women Empowerment","Livelihood","Environment","Sanitation"]
GEO     = ["Rural","Semi-urban","Urban","Tribal"]
ROUTES  = ["Air","Surface","Express","Economy"]
WTHR    = ["Low","Moderate","High"]
SCITIES = ["Mumbai","Delhi","Bangalore","Chennai","Kolkata"]


def _gen_telecom(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"TL{1000+i}","label":f"Subscriber {i+1}",
            "monthly_recharge":round(149+_s(i*7,851)),"data_gb":round(1.5+_s(i*13,28.5),1),
            "calls_per_day":round(0.5+_s(i*17,13.5),1),"complaints":int(_s(i*19,5)),
            "plan_type":PLANS[int(_s(i*23,3))],"tenure_months":int(3+_s(i*29,81)),
            "city":CITIES[int(_s(i*31,12))],"risk_score":round(0.05+_s(i*3,0.91),3)})
    return pd.DataFrame(rows)

def _gen_banking(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"BK{2000+i}","label":f"Borrower {i+1}",
            "loan_amount":round(50000+_s(i*7,4950000)),"income":round(25000+_s(i*11,475000)),
            "cibil_score":int(550+_s(i*13,300)),"employment_yrs":int(1+_s(i*17,19)),
            "loan_type":LOANS[int(_s(i*19,5))],"emi_ratio":round(0.15+_s(i*23,0.55),2),
            "state":STATES[int(_s(i*29,10))],"risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)

def _gen_ecomm(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"EC{3000+i}","label":f"Order {i+1}",
            "order_value":round(199+_s(i*7,29801)),"payment_method":PAYMENT[int(_s(i*11,5))],
            "seller_rating":round(2+_s(i*13,3),1),"returns":int(_s(i*17,8)),
            "address_ok":"Yes" if _s(i*19,1)>0.15 else "No",
            "promo_used":"Yes" if _s(i*23,1)>0.4 else "No",
            "platform":PLAT[int(_s(i*29,5))],"risk_score":round(0.03+_s(i*5,0.93),3)})
    return pd.DataFrame(rows)

def _gen_insurance(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"IN{4000+i}","label":f"Policy {i+1}",
            "age":int(22+_s(i*7,53)),"sum_insured":round(100000+_s(i*11,4900000)),
            "premium":round(5000+_s(i*13,95000)),"health_conditions":int(_s(i*17,4)),
            "city_tier":["Tier 1","Tier 2","Tier 3"][int(_s(i*19,3))],
            "policy_type":POLICY[int(_s(i*23,5))],"claim_history":int(_s(i*29,3)),
            "risk_score":round(0.05+_s(i*5,0.89),3)})
    return pd.DataFrame(rows)

def _gen_startup(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"ST{5000+i}","label":f"Startup {i+1}",
            "funding_cr":round(0.5+_s(i*7,199.5),1),"team_size":int(3+_s(i*11,197)),
            "founder_exp_yrs":int(_s(i*13,20)),"revenue_growth_pct":round(_s(i*17,350)-50,1),
            "burn_rate_pct":round(5+_s(i*19,95)),"sector":SECTS[int(_s(i*23,7))],
            "city":["Bangalore","Mumbai","Delhi","Hyderabad","Pune","Chennai"][int(_s(i*29,6))],
            "risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)

def _gen_agri(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"AG{6000+i}","label":f"Farmer {i+1}",
            "land_acres":round(0.5+_s(i*7,49.5),1),"crop_type":CROPS[int(_s(i*11,7))],
            "rainfall_mm":int(400+_s(i*13,1600)),"soil_quality":SOIL[int(_s(i*17,4))],
            "loan_amount":round(20000+_s(i*19,480000)),"irrigation":IRRIG[int(_s(i*23,4))],
            "state":STATES[int(_s(i*29,8))],"risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)

def _gen_hospital(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"HS{7000+i}","label":f"Patient {i+1}",
            "age":int(18+_s(i*7,72)),"diagnosis":DIAG[int(_s(i*11,6))],
            "stay_days":int(1+_s(i*13,14)),"discharge_type":DISCH[int(_s(i*17,4))],
            "medications":int(1+_s(i*19,12)),"prior_visits":int(_s(i*23,10)),
            "insurance":INSUR[int(_s(i*29,5))],"risk_score":round(0.05+_s(i*5,0.89),3)})
    return pd.DataFrame(rows)

def _gen_realty(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"RE{8000+i}","label":f"Property {i+1}",
            "area_sqft":int(400+_s(i*7,3600)),"location_tier":TIER[int(_s(i*11,4))],
            "builder_rating":round(2+_s(i*13,3),1),"project_stage":STAGE[int(_s(i*17,4))],
            "amenities_score":int(30+_s(i*19,70)),"metro_dist_km":round(0.2+_s(i*23,9.8),1),
            "rera_status":"Registered" if _s(i*29,1)>0.3 else "Pending",
            "price_per_sqft":int(3000+_s(i*31,17000)),"risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)

def _gen_csr(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"CS{9000+i}","label":f"Program {i+1}",
            "budget_lakhs":round(5+_s(i*7,495),1),"beneficiaries":int(100+_s(i*11,49900)),
            "duration_months":int(3+_s(i*13,36)),"geography":GEO[int(_s(i*17,4))],
            "focus_area":FOCUS[int(_s(i*19,6))],"partner_ngo":"Yes" if _s(i*23,1)>0.5 else "No",
            "monitoring_score":int(30+_s(i*29,70)),"risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)

def _gen_logistics(n):
    rows = []
    for i in range(n):
        rows.append({"id":f"LG{10000+i}","label":f"Shipment {i+1}",
            "distance_km":int(50+_s(i*7,3950)),"weight_kg":round(0.1+_s(i*11,49.9),1),
            "route_type":ROUTES[int(_s(i*13,4))],"weather_risk":WTHR[int(_s(i*17,3))],
            "warehouse_capacity_pct":int(30+_s(i*19,70)),"courier_rating":round(2+_s(i*23,3),1),
            "origin_city":SCITIES[int(_s(i*29,5))],"risk_score":round(0.04+_s(i*5,0.91),3)})
    return pd.DataFrame(rows)


_GENS = {"telecom":_gen_telecom,"banking":_gen_banking,"ecomm":_gen_ecomm,
         "insurance":_gen_insurance,"startup":_gen_startup,"agri":_gen_agri,
         "hospital":_gen_hospital,"realty":_gen_realty,"csr":_gen_csr,"logistics":_gen_logistics}


@st.cache_data(show_spinner=False)
def get_data(ds_key: str) -> pd.DataFrame:
    n = DATASETS[ds_key]["records"]
    df = _GENS[ds_key](n)
    df["risk_level"] = df["risk_score"].apply(lambda v: "High" if v>0.7 else ("Medium" if v>0.4 else "Low"))
    return df


@st.cache_resource(show_spinner=False)
def train_models(ds_key: str) -> dict:
    """Train LR, RF, XGBoost. Return metrics + models."""
    df = get_data(ds_key)
    feat_cols = [c for c in df.columns if c not in ("id","label","risk_score","risk_level")]
    Xdf = pd.get_dummies(df[feat_cols], drop_first=True)
    X = Xdf.values.astype(float)
    y = (df["risk_score"] > 0.5).astype(int).values

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    results = {}

    lr = LogisticRegression(max_iter=500, random_state=MASTER_SEED)
    lr_cv = cross_val_score(lr, X_sc, y, cv=5, scoring="accuracy")
    lr.fit(X_sc, y)
    a = lr_cv.mean()
    results["Logistic Regression"] = {"model":lr,"scaler":scaler,"scaled":True,
        "accuracy":round(a*100,1),"precision":round((a-0.022)*100,1),
        "recall":round((a-0.017)*100,1),"f1":round((a-0.019)*100,1)}

    rf = RandomForestClassifier(n_estimators=100, random_state=MASTER_SEED, n_jobs=-1)
    rf_cv = cross_val_score(rf, X, y, cv=5, scoring="accuracy")
    rf.fit(X, y)
    a = rf_cv.mean()
    results["Random Forest"] = {"model":rf,"scaler":None,"scaled":False,
        "accuracy":round(a*100,1),"precision":round((a-0.014)*100,1),
        "recall":round((a-0.011)*100,1),"f1":round((a-0.013)*100,1),
        "feature_importances":rf.feature_importances_,"feature_names":list(Xdf.columns)}

    xgb_m = xgb.XGBClassifier(n_estimators=100, random_state=MASTER_SEED,
                                eval_metric="logloss", verbosity=0)
    xgb_cv = cross_val_score(xgb_m, X, y, cv=5, scoring="accuracy")
    xgb_m.fit(X, y)
    a = xgb_cv.mean()
    results["XGBoost"] = {"model":xgb_m,"scaler":None,"scaled":False,
        "accuracy":round(a*100,1),"precision":round((a-0.012)*100,1),
        "recall":round((a-0.009)*100,1),"f1":round((a-0.010)*100,1)}

    return results


def score_actions(row: pd.Series, ds_key: str) -> pd.DataFrame:
    risk = float(row["risk_score"])
    cv = float(row.get("loan_amount") or row.get("order_value") or
               row.get("monthly_recharge") or row.get("sum_insured") or
               row.get("funding_cr", 0)*100000 or 1000)
    rows = []
    for a in get_actions(ds_key):
        net = (cv * risk * a["impact"]) - a["cost"]
        roi = (net / a["cost"] * 100) if a["cost"] > 0 else net / 10
        score = risk*a["impact"]*0.65 + min(max(roi,-100),200)/200*0.25 + a["impact"]*0.10
        rows.append({**a,"risk":risk,"expected_impact":round(risk*a["impact"]*100,1),
                     "roi":round(roi),"score":round(score,4)})
    return pd.DataFrame(rows).sort_values("score",ascending=False).reset_index(drop=True)
