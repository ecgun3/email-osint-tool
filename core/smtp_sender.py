import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional, Dict, Any


def send_mail(
	smtp_host: str,
	smtp_port: int,
	smtp_username: Optional[str],
	smtp_password: Optional[str],
	smtp_use_tls: bool,
	smtp_use_ssl: bool,
	mail_from: str,
	mail_to: str,
	subject: str,
	body_text: str,
	body_html: Optional[str] = None,
	from_display_name: Optional[str] = None,
	timeout_seconds: int = 20,
) -> Dict[str, Any]:
	msg = MIMEText(body_html or body_text, "html" if body_html else "plain", "utf-8")
	from_header = formataddr((from_display_name or "Security Awareness", mail_from))
	msg["From"] = from_header
	msg["To"] = mail_to
	msg["Subject"] = subject

	server = None
	try:
		if smtp_use_ssl:
			server = smtplib.SMTP_SSL(host=smtp_host, port=smtp_port, timeout=timeout_seconds)
		else:
			server = smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=timeout_seconds)
			if smtp_use_tls:
				server.starttls()
		if smtp_username and smtp_password:
			server.login(smtp_username, smtp_password)
		response = server.sendmail(mail_from, [mail_to], msg.as_string())
		return {"ok": True, "response": response}
	except Exception as exc:  # noqa: BLE001
		return {"ok": False, "error": str(exc)}
	finally:
		try:
			if server:
				server.quit()
		except Exception:
			pass