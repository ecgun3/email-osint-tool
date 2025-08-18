from typing import Any, Dict, List

from core import email_patterns, mx_analyzer, holehe_runner, builtwith_client


def run_simulation(
    first_name: str,
    last_name: str,
    domain: str,
    use_builtwith: bool = False,
) -> Dict[str, Any]:
    """Run the end-to-end OSINT email simulation pipeline.

    This function intentionally delegates to modules that can be mocked in tests.
    It returns a combined result dictionary that the web layer can render.
    """

    generated_emails: List[str] = email_patterns.generate_email_patterns(
        first_name, last_name, domain
    )
    mx_records: List[Dict[str, Any]] = mx_analyzer.fetch_mx_records(domain)
    accounts_summary: Dict[str, Any] = holehe_runner.enumerate_accounts(generated_emails)

    result: Dict[str, Any] = {
        "domain": domain,
        "generated_emails": generated_emails,
        "mx_records": mx_records,
        "accounts": accounts_summary,
    }

    if use_builtwith:
        result["technology_stack"] = builtwith_client.fetch_technology_stack(domain)

    return result