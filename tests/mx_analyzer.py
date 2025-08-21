# tests/test_mx_analyzer.py --> It checks whether it safely handles both successful and unsuccessful MX query cases.
import pytest
from unittest.mock import patch
from core import mx_analyzer

@patch("core.mx_analyzer.dns.resolver.resolve")
def test_get_mx_records_success(mock_resolve):
    mock_record = type("MX", (), {"exchange": "mail.example.com"})()
    mock_resolve.return_value = [mock_record]

    result = mx_analyzer.get_mx_records("example.com")
    assert "mail.example.com" in result

@patch("core.mx_analyzer.dns.resolver.resolve")
def test_get_mx_records_no_records(mock_resolve):
    mock_resolve.side_effect = Exception("No MX records found")
    result = mx_analyzer.get_mx_records("no-mx.com")
    assert result == []
