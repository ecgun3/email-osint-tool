from typing import Any, Dict, List
import smtplib
import dns.resolver


def _resolve_mx(domain: str, timeout_seconds: int = 10) -> List[str]:
	mx_hosts: List[str] = []
	answers = dns.resolver.resolve(domain, "MX", lifetime=timeout_seconds)
	for rdata in sorted(answers, key=lambda r: int(r.preference)):
		exchange = str(getattr(rdata, "exchange", "")).rstrip(".")
		mx_hosts.append(exchange)
	return mx_hosts


def probe_mailbox_exists(
	email: str,
	mail_from: str,
	timeout_seconds: int = 15,
) -> Dict[str, Any]:
	try:
		recipient_domain = email.rsplit("@", 1)[1]
	except Exception:
		return {"ok": False, "error": "Invalid recipient email"}

	try:
		mx_hosts = _resolve_mx(recipient_domain, timeout_seconds)
		if not mx_hosts:
			return {"ok": False, "error": "No MX hosts for recipient domain"}
		server = None
		last_error = None
		for host in mx_hosts:
			try:
				server = smtplib.SMTP(host, 25, timeout=timeout_seconds)
				server.helo("localhost")
				code, _ = server.mail(mail_from)
				if code >= 400:
					last_error = f"MAIL FROM rejected ({code})"
					server.quit()
					continue
				code, reply = server.rcpt(email)
				server.quit()
				if 250 <= code < 300:
					return {"ok": True, "exists": True, "mx_host": host, "code": code, "reply": reply.decode(errors='ignore') if isinstance(reply, bytes) else str(reply)}
				elif 500 <= code < 600:
					return {"ok": True, "exists": False, "mx_host": host, "code": code, "reply": reply.decode(errors='ignore') if isinstance(reply, bytes) else str(reply)}
				else:
					last_error = f"Indeterminate ({code})"
			except Exception as exc:  # noqa: BLE001
				last_error = str(exc)
				try:
					if server:
						server.quit()
				except Exception:
					pass
				continue
		return {"ok": False, "error": last_error or "Unknown error"}
	except dns.resolver.NXDOMAIN:
		return {"ok": False, "error": "Recipient domain does not exist"}
	except dns.resolver.NoAnswer:
		return {"ok": False, "error": "No MX records for recipient domain"}
	except dns.exception.Timeout:
		return {"ok": False, "error": "DNS timeout while resolving MX"}
	except Exception as exc:  # noqa: BLE001
		return {"ok": False, "error": str(exc)}