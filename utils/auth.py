"""
Nirnay — Authentication with Supabase + demo login fallback
"""
import streamlit as st
import hashlib

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Demo accounts that always work even without Supabase
DEMO_USERS = {
    "vidushibksharma@gmail.com": {
        "password": "vidushi1412",
        "name": "Vidushi",
        "role": "Admin",
    },
    "admin@nirnay.ai": {
        "password": "admin123",
        "name": "Admin User",
        "role": "Admin",
    },
    "demo@nirnay.ai": {
        "password": "demo123",
        "name": "Demo Analyst",
        "role": "Analyst",
    },
}

def _get_client():
    try:
        from supabase import create_client
        cfg = st.secrets.get("supabase", {})
        url = cfg.get("url", "").strip().rstrip("/")
        key = cfg.get("key", "").strip()
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None

def login(email: str, password: str):
    email = email.strip().lower()

    # Check demo users first — always works
    for demo_email, info in DEMO_USERS.items():
        if email == demo_email and password == info["password"]:
            return {"name": info["name"], "role": info["role"], "email": email}

    # Try Supabase
    try:
        db = _get_client()
        if db:
            result = db.table("users").select("*").eq("email", email).execute()
            if result.data and result.data[0]["password_hash"] == _hash(password):
                return result.data[0]
    except Exception as e:
        st.warning(f"Database unavailable, using local auth only.")

    return None

def register(name: str, email: str, password: str, role: str = "Analyst") -> bool:
    try:
        db = _get_client()
        if db:
            db.table("users").insert({
                "email":         email.strip().lower(),
                "name":          name.strip(),
                "password_hash": _hash(password),
                "role":          role,
            }).execute()
            return True
    except Exception:
        pass
    return False

def get_all_users() -> list:
    try:
        db = _get_client()
        if db:
            result = db.table("users").select(
                "id,email,name,role,created_at"
            ).execute()
            return result.data or []
    except Exception:
        pass
    return []

def delete_user(email: str):
    try:
        db = _get_client()
        if db:
            db.table("users").delete().eq("email", email).execute()
    except Exception:
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
    .block-container{max-width:440px !important;padding-top:80px !important;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:28px">
      <div style="width:56px;height:56px;border-radius:14px;
           background:linear-gradient(135deg,#4f6ef7,#7c3aed);
           display:flex;align-items:center;justify-content:center;
           font-size:24px;font-weight:900;color:#fff;
           margin:0 auto 12px auto">न</div>
      <div style="font-size:26px;font-weight:800;color:#dde3f0;
           letter-spacing:-0.5px">निर्णय</div>
      <div style="font-size:11px;color:#3d4f68;letter-spacing:2px;
           text-transform:uppercase;margin-top:3px">
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

        # Demo accounts box
        st.markdown("""
        <div style="margin-top:12px;padding:12px 14px;
             background:rgba(79,110,247,0.07);
             border:1px solid rgba(79,110,247,0.18);
             border-radius:8px;font-size:12px;color:#8892a4">
          <b style="color:#818cf8">Demo accounts</b><br/><br/>
          <b style="color:#dde3f0">Admin</b><br/>
          vidushibksharma@gmail.com &nbsp;·&nbsp; vidushi1412<br/><br/>
          <b style="color:#dde3f0">Analyst</b><br/>
          demo@nirnay.ai &nbsp;·&nbsp; demo123
        </div>
        """, unsafe_allow_html=True)

        # Quick login buttons
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚡ Login as Admin", use_container_width=True, key="quick_admin"):
                user = login("vidushibksharma@gmail.com", "vidushi1412")
                st.session_state.user       = user
                st.session_state.user_email = "vidushibksharma@gmail.com"
                st.rerun()
        with c2:
            if st.button("⚡ Login as Analyst", use_container_width=True, key="quick_analyst"):
                user = login("demo@nirnay.ai", "demo123")
                st.session_state.user       = user
                st.session_state.user_email = "demo@nirnay.ai"
                st.rerun()

    with tab2:
        name  = st.text_input("Full Name",  key="rg_name")
        email = st.text_input("Work Email", key="rg_email")
        pwd   = st.text_input("Password (min 6 chars)",
                              type="password", key="rg_pass")
        role  = st.selectbox("Role", ["Analyst", "Admin"], key="rg_role")

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
                    st.error("Could not create account. Try again.")