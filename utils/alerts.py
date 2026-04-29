"""
Nirnay — Alert System
WhatsApp alerts via Twilio + Email alerts via SMTP
"""
import streamlit as st
import smtplib, json, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

ALERTS_FILE = "alert_config.json"


def _load_config() -> dict:
    if not os.path.exists(ALERTS_FILE):
        return {}
    with open(ALERTS_FILE) as f:
        return json.load(f)


def _save_config(cfg: dict):
    with open(ALERTS_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def send_email_alert(to_email: str, subject: str, body: str,
                     smtp_host: str, smtp_port: int,
                     smtp_user: str, smtp_pass: str) -> tuple[bool, str]:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = smtp_user
        msg["To"]      = to_email
        html_body = f"""
        <html><body style="font-family:sans-serif;background:#07090f;color:#dde3f0;padding:24px">
          <div style="max-width:560px;margin:0 auto">
            <div style="background:linear-gradient(135deg,#4f6ef7,#7c3aed);
                 padding:16px 20px;border-radius:10px 10px 0 0">
              <h2 style="margin:0;color:#fff;font-size:18px">⚠️ निर्णय Risk Alert</h2>
            </div>
            <div style="background:#111827;padding:20px;border-radius:0 0 10px 10px;
                 border:1px solid rgba(255,255,255,0.07)">
              <pre style="color:#dde3f0;font-size:13px;white-space:pre-wrap">{body}</pre>
              <hr style="border:1px solid rgba(255,255,255,0.07);margin:16px 0"/>
              <p style="color:#3d4f68;font-size:11px;margin:0">
                Sent by Nirnay Decision Intelligence · {datetime.now().strftime('%d %b %Y %H:%M')}
              </p>
            </div>
          </div>
        </body></html>"""
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def send_whatsapp_alert(to_number: str, message: str,
                        account_sid: str, auth_token: str,
                        from_number: str) -> tuple[bool, str]:
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{to_number}"
        )
        return True, "WhatsApp message sent"
    except ImportError:
        return False, "Twilio not installed. Run: pip install twilio"
    except Exception as e:
        return False, str(e)


def build_alert_message(high_risk_cases: list, dataset_name: str) -> str:
    lines = [
        f"🚨 Nirnay Risk Alert — {dataset_name}",
        f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}",
        f"⚠️  {len(high_risk_cases)} HIGH RISK cases require immediate attention",
        "",
        "TOP CASES:",
    ]
    for i, case in enumerate(high_risk_cases[:5], 1):
        lines.append(
            f"  {i}. {case.get('label','—')} ({case.get('id','—')}) "
            f"— Risk: {round(case.get('risk_score',0)*100)}% "
            f"→ Action: {case.get('top_action','—')}"
        )
    lines += ["", "Login to Nirnay to take action → nirnay-decision-intelligence.streamlit.app"]
    return "\n".join(lines)


def render(email: str):
    st.markdown("## 🔔 Alert Settings")
    st.caption("Get notified instantly when high-risk cases are detected")

    cfg = _load_config()
    user_cfg = cfg.get(email, {})

    tab_email, tab_whatsapp, tab_test = st.tabs(["📧 Email Alerts", "💬 WhatsApp", "🧪 Test"])

    with tab_email:
        st.markdown("**Configure Email Alerts**")
        st.info("Use Gmail App Password for best results. Go to Google Account → Security → App Passwords.")

        smtp_host = st.text_input("SMTP Host", value=user_cfg.get("smtp_host","smtp.gmail.com"))
        smtp_port = st.number_input("SMTP Port", value=int(user_cfg.get("smtp_port",465)), step=1)
        smtp_user = st.text_input("SMTP Email (sender)", value=user_cfg.get("smtp_user",""))
        smtp_pass = st.text_input("SMTP Password / App Password", type="password", value=user_cfg.get("smtp_pass",""))
        alert_to  = st.text_input("Alert Recipient Email", value=user_cfg.get("alert_to", email))

        c1, c2 = st.columns(2)
        email_enabled = c1.toggle("Enable Email Alerts", value=user_cfg.get("email_enabled", False))
        risk_threshold = c2.slider("Alert when risk >", 0.5, 0.95, float(user_cfg.get("risk_threshold", 0.7)), 0.05)

        if st.button("💾 Save Email Config", type="primary"):
            cfg[email] = {**user_cfg,
                "smtp_host": smtp_host, "smtp_port": int(smtp_port),
                "smtp_user": smtp_user, "smtp_pass": smtp_pass,
                "alert_to": alert_to, "email_enabled": email_enabled,
                "risk_threshold": risk_threshold}
            _save_config(cfg)
            st.success("Email configuration saved!")

    with tab_whatsapp:
        st.markdown("**Configure WhatsApp Alerts via Twilio**")
        st.info("Sign up at twilio.com → Get a WhatsApp sandbox number → Paste credentials below.")

        wa_sid    = st.text_input("Twilio Account SID", value=user_cfg.get("wa_sid",""), type="password")
        wa_token  = st.text_input("Twilio Auth Token",  value=user_cfg.get("wa_token",""), type="password")
        wa_from   = st.text_input("Twilio WhatsApp Number", value=user_cfg.get("wa_from","+14155238886"),
                                  help="Format: +14155238886")
        wa_to     = st.text_input("Your WhatsApp Number", value=user_cfg.get("wa_to",""),
                                  help="Format: +919876543210")
        wa_enabled = st.toggle("Enable WhatsApp Alerts", value=user_cfg.get("wa_enabled", False))

        if st.button("💾 Save WhatsApp Config", type="primary"):
            cfg[email] = {**user_cfg,
                "wa_sid": wa_sid, "wa_token": wa_token,
                "wa_from": wa_from, "wa_to": wa_to, "wa_enabled": wa_enabled}
            _save_config(cfg)
            st.success("WhatsApp configuration saved!")

    with tab_test:
        st.markdown("**Send a Test Alert**")

        test_cases = [
            {"id":"TL1042","label":"Subscriber 43","risk_score":0.87,"top_action":"Retention Call"},
            {"id":"BK2156","label":"Borrower 157","risk_score":0.81,"top_action":"EMI Restructuring"},
            {"id":"EC3891","label":"Order 892","risk_score":0.76,"top_action":"Flag for Review"},
        ]
        test_msg = build_alert_message(test_cases, "Test Dataset")

        st.markdown("**Alert Preview:**")
        st.code(test_msg, language="text")

        tc1, tc2 = st.columns(2)

        with tc1:
            if st.button("📧 Send Test Email", use_container_width=True):
                ucfg = cfg.get(email, {})
                if not ucfg.get("smtp_user") or not ucfg.get("smtp_pass"):
                    st.error("Configure email settings first.")
                else:
                    with st.spinner("Sending..."):
                        ok, msg = send_email_alert(
                            ucfg.get("alert_to", email),
                            "🧪 Nirnay Test Alert",
                            test_msg,
                            ucfg.get("smtp_host","smtp.gmail.com"),
                            int(ucfg.get("smtp_port",465)),
                            ucfg.get("smtp_user",""),
                            ucfg.get("smtp_pass",""),
                        )
                    if ok: st.success("✅ " + msg)
                    else:  st.error("❌ " + msg)

        with tc2:
            if st.button("💬 Send Test WhatsApp", use_container_width=True):
                ucfg = cfg.get(email, {})
                if not ucfg.get("wa_sid") or not ucfg.get("wa_token"):
                    st.error("Configure WhatsApp settings first.")
                else:
                    with st.spinner("Sending..."):
                        ok, msg = send_whatsapp_alert(
                            ucfg.get("wa_to",""),
                            test_msg,
                            ucfg.get("wa_sid",""),
                            ucfg.get("wa_token",""),
                            ucfg.get("wa_from",""),
                        )
                    if ok: st.success("✅ " + msg)
                    else:  st.error("❌ " + msg)
