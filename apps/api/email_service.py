"""
ZeptoMail Transactional Email Service
Supports REST API sending via ZeptoMail (Zoho) with responsive HTML templates.
"""
import os
import json
import logging
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """Check if ZeptoMail API Key is set in environment."""
    return bool(os.getenv("ZEPTOMAIL_API_KEY", "").strip())


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    to_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a transactional email using ZeptoMail REST API.
    
    Environment variables:
    - ZEPTOMAIL_API_KEY: Send Mail Token
    - ZEPTOMAIL_URL: e.g. https://api.zeptomail.com/v1.1/email
    - MAIL_FROM_ADDRESS: e.g. asysyuuraa-noreply@nootif.com
    - MAIL_FROM_NAME: e.g. Yayasan Asy-Syuuraa Batam
    """
    api_key = os.getenv("ZEPTOMAIL_API_KEY", "").strip()
    if not api_key:
        logger.warning(f"ZeptoMail not configured. Skipping email to {to_email}")
        return {"status": "skipped", "message": "ZeptoMail API Key not configured"}

    # ZeptoMail requires Authorization header to start with "Zoho-enczapikey "
    if not api_key.startswith("Zoho-enczapikey "):
        auth_header = f"Zoho-enczapikey {api_key}"
    else:
        auth_header = api_key

    api_url = os.getenv("ZEPTOMAIL_URL", "https://api.zeptomail.com/v1.1/email").strip()
    from_address = os.getenv("MAIL_FROM_ADDRESS", "asysyuuraa-noreply@nootif.com").strip()
    from_name = os.getenv("MAIL_FROM_NAME", "Yayasan Asy-Syuuraa Batam").strip()

    payload = {
        "from": {
            "address": from_address,
            "name": from_name
        },
        "to": [
            {
                "email_address": {
                    "address": to_email.strip(),
                    "name": (to_name or to_email).strip()
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=req_data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AsySyuuraa-ERP/1.0"
        },
        method="POST"
    )

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            resp_body = resp.read().decode("utf-8")
            data = json.loads(resp_body) if resp_body else {}
            logger.info(f"Email successfully sent to {to_email} via ZeptoMail.")
            return {"status": "success", "data": data}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"ZeptoMail HTTPError {e.code}: {err_body}")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = {"raw": err_body}
        raise RuntimeError(f"ZeptoMail Error ({e.code}): {err_json}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise RuntimeError(f"Gagal mengirim email: {str(e)}")


def _get_base_email_template(title: str, content_html: str) -> str:
    """Generate a clean, responsive HTML email wrapper with Asy-Syuuraa branding."""
    current_year = datetime.now().year
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f1f5f9;
      color: #334155;
    }}
    .email-wrapper {{
      width: 100%;
      background-color: #f1f5f9;
      padding: 30px 12px;
    }}
    .email-container {{
      max-width: 580px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
      border: 1px solid #e2e8f0;
    }}
    .email-header {{
      background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);
      padding: 28px 24px;
      text-align: center;
      color: #ffffff;
    }}
    .email-header h1 {{
      margin: 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .email-header p {{
      margin: 6px 0 0 0;
      font-size: 12px;
      opacity: 0.9;
    }}
    .email-body {{
      padding: 32px 28px;
      line-height: 1.6;
      font-size: 14px;
    }}
    .btn-primary {{
      display: inline-block;
      background-color: #059669;
      color: #ffffff !important;
      text-decoration: none;
      padding: 13px 28px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 14px;
      margin: 20px 0;
      text-align: center;
      box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2);
    }}
    .email-footer {{
      background-color: #f8fafc;
      padding: 20px 24px;
      text-align: center;
      border-top: 1px solid #e2e8f0;
      font-size: 11px;
      color: #64748b;
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <div class="email-container">
      <div class="email-header">
        <h1>YAYASAN ASY-SYUURAA BATAM</h1>
        <p>Sistem Informasi Manajemen Terpadu</p>
      </div>
      <div class="email-body">
        {content_html}
      </div>
      <div class="email-footer">
        <p style="margin: 0 0 4px 0;">Email ini dikirim secara otomatis oleh sistem notifikasi <b>Asy-Syuuraa Batam</b> via <b>nootif.com</b>.</p>
        <p style="margin: 0;">&copy; {current_year} Yayasan Asy-Syuuraa Batam. Hak cipta dilindungi.</p>
      </div>
    </div>
  </div>
</body>
</html>"""


def send_password_reset_email(
    to_email: str,
    reset_token: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send a secure password reset link to user."""
    frontend_url = os.getenv("FRONTEND_URL", "https://asy-syuuraabatam.or.id").rstrip("/")
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    display_name = user_name or "Pengguna"

    subject = "Permintaan Reset Kata Sandi — Asy-Syuuraa Batam"
    content = f"""
      <p style="margin-top: 0;"><b>Assalamu'alaikum wr. wb.,</b></p>
      <p>Halo <b>{display_name}</b>,</p>
      <p>Kami menerima permintaan untuk mengatur ulang kata sandi (reset password) akun Anda di portal <b>Asy-Syuuraa Batam</b>.</p>
      
      <div style="text-align: center; margin: 28px 0;">
        <a href="{reset_url}" class="btn-primary" target="_blank">Atur Ulang Kata Sandi Saya</a>
      </div>

      <p style="font-size: 12px; color: #64748b; background-color: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
        <b>Catatan Keamanan:</b> Tautan reset kata sandi ini hanya berlaku selama <b>30 menit</b>. Jika Anda tidak pernah meminta reset kata sandi, abaikan email ini dengan aman. Kata sandi akun Anda tidak akan berubah.
      </p>

      <p style="font-size: 11px; color: #94a3b8; word-break: break-all; margin-top: 20px;">
        Jika tombol di atas tidak dapat diklik, salin dan tempel tautan berikut ke peramban (browser) Anda:<br>
        <a href="{reset_url}" style="color: #059669;">{reset_url}</a>
      </p>
    """

    html = _get_base_email_template("Reset Kata Sandi", content)
    return send_email(to_email, subject, html, to_name=display_name)


def send_test_email(to_email: str) -> Dict[str, Any]:
    """Send a verification test email to verify ZeptoMail integration."""
    wib_now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    from_address = os.getenv("MAIL_FROM_ADDRESS", "asysyuuraa-noreply@nootif.com")

    subject = "✅ Uji Coba Konfigurasi Email ZeptoMail Berhasil — Asy-Syuuraa Batam"
    content = f"""
      <div style="text-align: center; margin-bottom: 20px;">
        <div style="display: inline-block; width: 56px; height: 56px; line-height: 56px; background-color: #d1fae5; border-radius: 50%; font-size: 28px;">
          🚀
        </div>
        <h2 style="color: #065f46; margin: 12px 0 4px 0; font-size: 18px;">Koneksi ZeptoMail Berhasil!</h2>
        <p style="margin: 0; color: #64748b; font-size: 13px;">Pengiriman email transaksional via domain <b>nootif.com</b> telah aktif.</p>
      </div>

      <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin: 20px 0; font-size: 13px;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 4px 0; color: #64748b; width: 140px;">Pengirim (Sender):</td>
            <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">{from_address}</td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #64748b;">Penerima (To):</td>
            <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">{to_email}</td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #64748b;">Waktu Server:</td>
            <td style="padding: 4px 0; font-weight: 600; color: #1e293b;">{wib_now}</td>
          </tr>
          <tr>
            <td style="padding: 4px 0; color: #64748b;">Layanan:</td>
            <td style="padding: 4px 0; font-weight: 600; color: #059669;">ZeptoMail REST API (v1.1)</td>
          </tr>
        </table>
      </div>

      <p style="margin-bottom: 0;">Sistem kini siap digunakan untuk pengiriman notifikasi lupa password, penugasan baru, rekap kehadiran, dan notifikasi sekolah lainnya.</p>
    """

    html = _get_base_email_template("Tes Konfigurasi Email", content)
    return send_email(to_email, subject, html)
