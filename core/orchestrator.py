from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional, List
import traceback
from time import perf_counter

from core.mx_analyzer import analyze_mx
from core.builtwith_client import fetch_builtwith
from core.holehe_runner import run_holehe
from core.email_patterns import generate_email_patterns
from core.training_template import generate_training_email_template
from utils.helpers import extract_domain, now_utc_iso
from core.smtp_probe import probe_mailbox_exists
from core.smtp_sender import send_mail
from core import email_patterns as email_patterns_module
from core import mx_analyzer as mx_analyzer_module
from core import holehe_runner as holehe_runner_module
from core import builtwith_client as builtwith_client_module


def analyze_workflow(
	domain: Optional[str],
	email: Optional[str],
	first_name: Optional[str],
	last_name: Optional[str],
	request_timeout: int,
	builtwith_api_key: Optional[str],
) -> Dict[str, Any]:
	results: Dict[str, Any] = {
		"input": {
			"domain": domain,
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
		},
		"meta": {"started_at": now_utc_iso()},
	}
	start_ts = perf_counter()

	resolved_domain = domain or (extract_domain(email) if email else None)
	results["resolved_domain"] = resolved_domain
	errors = []

	futures = {}
	with ThreadPoolExecutor(max_workers=4) as executor:
		if resolved_domain:
			futures["mx"] = executor.submit(analyze_mx, resolved_domain, request_timeout)
			if builtwith_api_key:
				futures["builtwith"] = executor.submit(
					fetch_builtwith, resolved_domain, builtwith_api_key, request_timeout
				)
		if email:
			futures["holehe"] = executor.submit(run_holehe, email, request_timeout)

		for name, future in futures.items():
			try:
				results[name] = future.result()
			except Exception as exc:  # noqa: BLE001
				results[name] = {"error": str(exc), "trace": traceback.format_exc()}
				errors.append({"component": name, "error": str(exc)})

	# Email patterns are local and cheap; compute synchronously
	if first_name or last_name:
		patterns = generate_email_patterns(first_name or "", last_name or "", resolved_domain)
		results["email_patterns"] = patterns
		# Kick off limited parallel Holehe runs for top-N candidates
		candidates = [p["email"] for p in patterns.get("patterns", []) if p.get("email")]
		max_candidates = 10
		cand_to_check = candidates[:max_candidates]
		pattern_hits: Dict[str, Any] = {"checked": cand_to_check, "results": []}
		if cand_to_check:
			with ThreadPoolExecutor(max_workers=4) as executor:
				future_map = {executor.submit(run_holehe, email_addr, request_timeout): email_addr for email_addr in cand_to_check}
				for future in as_completed(future_map):
					email_addr = future_map[future]
					try:
						pattern_hits["results"].append({"email": email_addr, "holehe": future.result()})
					except Exception as exc:  # noqa: BLE001
						pattern_hits["results"].append({"email": email_addr, "holehe": {"error": str(exc)}})
		results["pattern_holehe"] = pattern_hits
	# Training email template is always generated for awareness use
	provider = None
	if isinstance(results.get("mx"), dict):
		provider = results["mx"].get("provider")
	builtwith_summary = None
	if isinstance(results.get("builtwith"), dict):
		builtwith_summary = results["builtwith"].get("summary")
	training = generate_training_email_template(
		first_name,
		last_name,
		resolved_domain,
		provider,
		builtwith_summary,
	)
	results["training_email"] = training

	# Optional mailbox probe (does not send email)
	if email:
		try:
			results["mailbox_probe"] = probe_mailbox_exists(
				email=email,
				mail_from=f"probe@{resolved_domain or 'example.com'}",
				timeout_seconds=request_timeout,
			)
		except Exception as exc:  # noqa: BLE001
			results["mailbox_probe"] = {"error": str(exc)}

	# Optional send (if SMTP configured and email present)
	try:
		from config import get_config  # local import to avoid circular at module load
		cfg = get_config()
		if not email:
			results["mail_send"] = {"skipped": True, "reason": "no_email"}
		elif not (cfg.smtp_host and cfg.smtp_from):
			results["mail_send"] = {"skipped": True, "reason": "smtp_not_configured"}
		else:
			results["mail_send"] = send_mail(
				smtp_host=cfg.smtp_host,
				smtp_port=cfg.smtp_port,
				smtp_username=cfg.smtp_username,
				smtp_password=cfg.smtp_password,
				smtp_use_tls=cfg.smtp_use_tls,
				smtp_use_ssl=cfg.smtp_use_ssl,
				mail_from=cfg.smtp_from,
				mail_to=email,
				subject=training["subject"],
				body_text=training["body_text"],
				body_html=training.get("body_html"),
				from_display_name="Security Awareness",
				timeout_seconds=request_timeout,
			)
	except Exception as exc:  # noqa: BLE001
		results["mail_send"] = {"ok": False, "error": str(exc)}

	results["meta"]["finished_at"] = now_utc_iso()
	results["meta"]["elapsed_seconds"] = round(perf_counter() - start_ts, 3)
	results["meta"]["errors"] = errors

	return results


def run_simulation(
    first_name: str,
    last_name: str,
    domain: str,
    use_builtwith: bool = False,
) -> Dict[str, Any]:
    """Lightweight simulation wrapper for unit tests.

    Accepts either dict-based output from generate_email_patterns (HEAD) or a list (tests).
    Delegates to wrapper helpers in modules for MX and account enumeration to keep tests simple.
    """

    generated = email_patterns_module.generate_email_patterns(first_name, last_name, domain)
    if isinstance(generated, dict):
        generated_emails: List[str] = [p.get("email") for p in generated.get("patterns", []) if p.get("email")]
    else:
        generated_emails = list(generated)

    mx_records: List[Dict[str, Any]] = mx_analyzer_module.fetch_mx_records(domain)
    accounts_summary: Dict[str, Any] = holehe_runner_module.enumerate_accounts(generated_emails)

    result: Dict[str, Any] = {
        "domain": domain,
        "generated_emails": generated_emails,
        "mx_records": mx_records,
        "accounts": accounts_summary,
    }

    if use_builtwith:
        result["technology_stack"] = builtwith_client_module.fetch_technology_stack(domain)

    return result
