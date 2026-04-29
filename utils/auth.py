"""
Nirnay — Authentication System
Supabase backend — production grade, persistent users
"""
import streamlit as st
import hashlib

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _get_client():
    from supabase import create_client
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def login(email: str, password: str):
    try:
        db     = _get_client()
        result = db.table("users").select("*").eq(
            "email", email.strip().lower()
        ).execute()
        if result.data and result.data[0]["password_hash"] == _hash(password):
            return result.data[0]
        return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def register(name: str, email: str, password: str, role: str = "Analyst") -> bool:
    try:
        db = _get_client()
        db.table("users").insert({
            "email":         email.strip().lower(),
            "name":          name.strip(),
            "password_hash": _hash(password),
            "role":          role,
        }).execute()
        return True
    except Exception as e:
        return False

def get_all_users() -> list:
    try:
        db     = _get_client()
        result = db.table("users").select("id,email,name,role,created_at").execute()
        return result.data or []
    except:
        return []

def delete_user(email: str):
    try:
        db = _get_client()
        db.table("users").delete().eq("email", email).execute()
    except:
        pass

def is_logged_in() -> bool:
    return st.session_state.get("user") is not None

def current_user() -> dict | None:
    return st.session_state.get("user")

def is_admin() -> bool:
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
           font-size:22px;font-weight:900;color:#fff;
           margin:0 auto 12px auto">न</div>
      <div style="font-size:24px;font-weight:800;color:#dde3f0;
           letter-spacing:-0.5px">निर्णय</div>
      <div style="font-size:11px;color:#3d4f68;letter-spacing:2px;
           text-transform:uppercase;margin-top:2px">
        Decision Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "Register"])

    with tab1:
        email    = st.text_input("Email",
                     placeholder="you@company.com", key="li_email")
        password = st.text_input("Password", type="password",
                     placeholder="••••••••", key="li_pass")

        if st.button("Sign In", use_container_width=True,
                     type="primary", key="li_btn"):
            if not email or not password:
                st.error("Enter email and password.")
            else:
                with st.spinner("Signing in..."):
                    user = login(email, password)
                if user:
                    st.session_state.user       = user
                    st.session_state.user_email = email.strip().lower()
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.markdown("""
        <div style="margin-top:10px;padding:10px 14px;
             background:rgba(79,110,247,0.07);
             border:1px solid rgba(79,110,247,0.18);
             border-radius:8px;font-size:12px;color:#8892a4">
          <b style="color:#818cf8">Demo login</b><br/>
          admin@nirnay.ai &nbsp;·&nbsp; admin123
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        name  = st.text_input("Full Name",   key="rg_name")
        email = st.text_input("Work Email",  key="rg_email")
        pwd   = st.text_input("Password (min 6 chars)",
                              type="password", key="rg_pass")
        role  = st.selectbox("Role", ["Analyst","Admin"], key="rg_role")

        if st.button("Create Account", use_container_width=True,
                     type="primary", key="rg_btn"):
            if not name or not email or not pwd:
                st.error("All fields required.")
            elif len(pwd) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with st.spinner("Creating account..."):
                    ok = register(name, email, pwd, role)
                if ok:
                    st.success("Account created! Sign in now.")
                else:
                    st.error("Email already registered or connection error.")