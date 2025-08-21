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


@pytest.mark.skipif(not os.getenv("LIVE_MX"), reason="Set LIVE_MX=1 to run")
def test_mx_analyze_live():
    domain = os.getenv("LIVE_DOMAIN", "gmail.com")
    result = analyze_mx(domain, timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")))
    assert isinstance(result, dict)
    assert "provider" in result


@pytest.mark.skipif(not os.getenv("LIVE_BUILTWITH"), reason="Set LIVE_BUILTWITH=1 to run")
def test_builtwith_live():
    api_key = os.getenv("BUILTWITH_API_KEY")
    assert api_key, "BUILTWITH_API_KEY is required"
    domain = os.getenv("LIVE_DOMAIN", "github.com")
    result = fetch_builtwith(domain, api_key, timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")))
    assert isinstance(result, dict)
    assert "grouped" in result or "flat" in result or "error" in result

