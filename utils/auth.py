"""
Nirnay — Authentication System
Login, Register, Role-based access (Admin / Analyst)
"""
import json, hashlib, os, streamlit as st
from datetime import datetime

AUTH_FILE = "users.json"

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _load():
    if not os.path.exists(AUTH_FILE):
        d = {"admin@nirnay.ai": {"name":"Admin User","password":_hash("admin123"),
             "role":"Admin","created":datetime.now().isoformat()}}
        _save(d); return d
    with open(AUTH_FILE) as f: return json.load(f)

def _save(u):
    with open(AUTH_FILE,"w") as f: json.dump(u,f,indent=2)

def login(email, password):
    u = _load(); e = email.strip().lower()
    if e in u and u[e]["password"] == _hash(password): return u[e]
    return None

def register(name, email, password, role="Analyst"):
    u = _load(); e = email.strip().lower()
    if e in u: return False
    u[e] = {"name":name,"password":_hash(password),"role":role,
             "created":datetime.now().isoformat()}
    _save(u); return True

def get_all_users(): return _load()
def delete_user(email):
    u = _load()
    if email in u: del u[email]; _save(u)

def is_logged_in(): return st.session_state.get("user") is not None
def current_user(): return st.session_state.get("user")
def is_admin():
    u = current_user()
    return u is not None and u.get("role") == "Admin"

def render_login_page():
    st.markdown("""
    <style>
    .stApp {background-color:#07090f;}
    #MainMenu,footer,header{visibility:hidden;}
    .block-container{max-width:420px !important;padding-top:80px !important;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:28px">
      <div style="width:52px;height:52px;border-radius:14px;
           background:linear-gradient(135deg,#4f6ef7,#7c3aed);
           display:flex;align-items:center;justify-content:center;
           font-size:22px;font-weight:900;color:#fff;margin:0 auto 12px auto">न</div>
      <div style="font-size:24px;font-weight:800;color:#dde3f0;letter-spacing:-0.5px">निर्णय</div>
      <div style="font-size:11px;color:#3d4f68;letter-spacing:2px;text-transform:uppercase;margin-top:2px">
        Decision Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "Register"])

    with tab1:
        email    = st.text_input("Email", placeholder="you@company.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")
        if st.button("Sign In", use_container_width=True, type="primary", key="li_btn"):
            if not email or not password:
                st.error("Enter email and password.")
            else:
                user = login(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.user_email = email.strip().lower()
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        st.markdown("""
        <div style="margin-top:10px;padding:10px 14px;background:rgba(79,110,247,0.07);
             border:1px solid rgba(79,110,247,0.18);border-radius:8px;font-size:12px;color:#8892a4">
          <b style="color:#818cf8">Demo login</b><br/>
          admin@nirnay.ai &nbsp;·&nbsp; admin123
        </div>""", unsafe_allow_html=True)

    with tab2:
        name  = st.text_input("Full Name", key="rg_name")
        email = st.text_input("Work Email", key="rg_email")
        pwd   = st.text_input("Password (min 6 chars)", type="password", key="rg_pass")
        role  = st.selectbox("Role", ["Analyst","Admin"], key="rg_role")
        if st.button("Create Account", use_container_width=True, type="primary", key="rg_btn"):
            if not name or not email or not pwd:
                st.error("All fields required.")
            elif len(pwd) < 6:
                st.error("Password too short.")
            elif register(name, email, pwd, role):
                st.success("Account created! Sign in now.")
            else:
                st.error("Email already registered.")
