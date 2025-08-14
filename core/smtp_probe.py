from typing import Any, Dict, List, Optional
import smtplib
import dns.resolver
import uuid


def _resolve_mx(domain: str, timeout_seconds: int = 10) -> List[str]:
	mx_hosts: List[str] = []
	answers = dns.resolver.resolve(domain, "MX", lifetime=timeout_seconds)
	for rdata in sorted(answers, key=lambda r: int(r.preference)):
		exchange = str(getattr(rdata, "exchange", "")).rstrip(".")
		mx_hosts.append(exchange)
	return mx_hosts


def _reply_to_str(reply: Any) -> str:
	if isinstance(reply, bytes):
		return reply.decode(errors="ignore")
	return str(reply)


def probe_mailbox_exists(
	email: str,
	mail_from: str,
	timeout_seconds: int = 15,
) -> Dict[str, Any]:
	"""
	Performs a conservative SMTP RCPT probe with catch-all detection.
	Returns a verdict and supporting codes. Does not send DATA.
	NOTE: Many providers accept RCPT for privacy or as catch-all; treat results as hints.
	"""
	try:
		recipient_domain = email.rsplit("@", 1)[1]
	except Exception:
		return {"ok": False, "error": "Invalid recipient email"}

	try:
		mx_hosts = _resolve_mx(recipient_domain, timeout_seconds)
		if not mx_hosts:
			return {"ok": False, "error": "No MX hosts for recipient domain"}
		summary_errors: List[str] = []
		for host in mx_hosts:
			server: Optional[smtplib.SMTP] = None
			try:
				server = smtplib.SMTP(host, 25, timeout=timeout_seconds)
				server.ehlo_or_helo_if_needed()
				code, _ = server.mail(mail_from)
				if code >= 400:
					summary_errors.append(f"MAIL FROM rejected on {host} ({code})")
					server.quit()
					continue
				# RCPT to target
				t_code, t_reply = server.rcpt(email)
				# RCPT to random to detect catch-all
				random_local = f"verify-{uuid.uuid4().hex[:16]}"
				random_addr = f"{random_local}@{recipient_domain}"
				r_code, r_reply = server.rcpt(random_addr)
				server.quit()

				# Evaluate
				if 250 <= t_code < 300 and 250 <= r_code < 300:
					return {
						"ok": True,
						"exists": None,
						"verdict": "catch_all",
						"mx_host": host,
						"target": {"code": t_code, "reply": _reply_to_str(t_reply)},
						"random": {"code": r_code, "reply": _reply_to_str(r_reply)},
						"catch_all": True,
					}
				if 250 <= t_code < 300 and (r_code >= 500 and r_code < 600):
					return {
						"ok": True,
						"exists": True,
						"verdict": "deliverable",
						"mx_host": host,
						"target": {"code": t_code, "reply": _reply_to_str(t_reply)},
						"random": {"code": r_code, "reply": _reply_to_str(r_reply)},
						"catch_all": False,
					}
				if (t_code >= 500 and t_code < 600):
					return {
						"ok": True,
						"exists": False,
						"verdict": "undeliverable",
						"mx_host": host,
						"target": {"code": t_code, "reply": _reply_to_str(t_reply)},
						"random": {"code": r_code, "reply": _reply_to_str(r_reply)},
						"catch_all": False,
					}
				# Indeterminate (4xx, or 2xx/2xx but policy unknown)
				return {
					"ok": False,
					"verdict": "unknown",
					"mx_host": host,
					"target": {"code": t_code, "reply": _reply_to_str(t_reply)},
					"random": {"code": r_code, "reply": _reply_to_str(r_reply)},
				}
			except Exception as exc:  # noqa: BLE001
				summary_errors.append(f"{host}: {str(exc)}")
				try:
					if server:
						server.quit()
				except Exception:
					pass
				continue
		return {"ok": False, "error": "; ".join(summary_errors) or "Unknown error"}
	except dns.resolver.NXDOMAIN:
		return {"ok": False, "error": "Recipient domain does not exist"}
	except dns.resolver.NoAnswer:
		return {"ok": False, "error": "No MX records for recipient domain"}
	except dns.exception.Timeout:
		return {"ok": False, "error": "DNS timeout while resolving MX"}
	except Exception as exc:  # noqa: BLE001
		return {"ok": False, "error": str(exc)}