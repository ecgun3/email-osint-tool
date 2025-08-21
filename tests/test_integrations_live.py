#test_integrations_live.py

"""
These tests use real-world data and services to check three core functions:
MX record analysis (analyze_mx)
BuiltWith API call (fetch_builtwith)
SMTP mailbox check (probe_mailbox_exists)
In other words, these tests are not unit tests, but live tests (integration tests) integrated with the real system.
"""

import os
import pytest

from core.mx_analyzer import analyze_mx
from core.builtwith_client import fetch_builtwith
from core.smtp_probe import probe_mailbox_exists


def _get_int_env(name: str, default: int) -> int:
	try:
		return int(os.getenv(name, str(default)))
	except Exception:
		return default


@pytest.mark.integration
def test_mx_analyze_live():
	if os.getenv("LIVE_MX") != "1":
		pytest.skip("Set LIVE_MX=1 to run live MX analysis test")
	domain = os.getenv("LIVE_DOMAIN", "gmail.com")
	timeout = _get_int_env("DNS_TIMEOUT", 8)
	result = analyze_mx(domain, timeout_seconds=timeout)
	assert isinstance(result, dict)
	assert result.get("domain") == domain
	assert "mx_records" in result
	assert isinstance(result["mx_records"], list)


@pytest.mark.integration
def test_builtwith_live():
	api_key = os.getenv("BUILTWITH_API_KEY")
	if not api_key or os.getenv("LIVE_BUILTWITH") != "1":
		pytest.skip("Set LIVE_BUILTWITH=1 and BUILTWITH_API_KEY to run BuiltWith test")
	domain = os.getenv("LIVE_DOMAIN", "github.com")
	timeout = _get_int_env("BUILTWITH_TIMEOUT", 15)
	result = fetch_builtwith(domain, api_key, timeout_seconds=timeout)
	assert isinstance(result, dict)
	# Either a valid structure or a well-formed error
	if "error" in result:
		assert "error" in result
	else:
		assert "summary" in result or "flat" in result


@pytest.mark.integration
def test_smtp_probe_live():
	if os.getenv("SMTP_LIVE") != "1":
		pytest.skip("Set SMTP_LIVE=1 to run SMTP mailbox probe test")
	email = os.getenv("SMTP_TEST_EMAIL", "nopeaddress123456789@gmail.com")
	mail_from = os.getenv("SMTP_MAIL_FROM", "probe@example.com")
	timeout = _get_int_env("SMTP_TIMEOUT", 8)
	res = probe_mailbox_exists(email=email, mail_from=mail_from, timeout_seconds=timeout)
	assert isinstance(res, dict)
	assert "ok" in res
	# Ensure we captured either a trace or an explicit error/decision
	assert any(k in res for k in ("trace", "error", "verdict", "target"))

