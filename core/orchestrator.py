from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional, List
import traceback
from time import perf_counter

from core.mx_analyzer import analyze_mx
from core.builtwith_client import fetch_builtwith
from core.email_patterns import generate_email_patterns
from utils.helpers import extract_domain, now_utc_iso
from core import email_patterns as email_patterns_module
from core import mx_analyzer as mx_analyzer_module
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
		# Holehe removed

		for name, future in futures.items():
			try:
				results[name] = future.result()
			except Exception as exc:  # noqa: BLE001
				results[name] = {"error": str(exc), "trace": traceback.format_exc()}
				errors.append({"component": name, "error": str(exc)})

	# Training email, SMTP probe and send removed

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

    Simplified: Only MX and optional BuiltWith are returned.
    """

    mx_records: List[Dict[str, Any]] = mx_analyzer_module.fetch_mx_records(domain)

    result: Dict[str, Any] = {
        "domain": domain,
        "mx_records": mx_records,
    }

    if use_builtwith:
        result["technology_stack"] = builtwith_client_module.fetch_technology_stack(domain)

    return result