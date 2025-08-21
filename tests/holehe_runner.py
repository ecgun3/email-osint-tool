# tests/test_holehe_runner.py
import pytest
from unittest.mock import patch
from core import holehe_runner

@patch("core.holehe_runner.subprocess.run")
def test_check_email_in_services_success(mock_run):
    mock_run.return_value.stdout = "gmail: FOUND\noutlook: FOUND"
    result = holehe_runner.check_email_in_services("user@example.com")
    assert "gmail" in result
    assert "outlook" in result

@patch("core.holehe_runner.subprocess.run")
def test_check_email_in_services_no_results(mock_run):
    mock_run.return_value.stdout = ""
    result = holehe_runner.check_email_in_services("user@unknown.com")
    assert result == []

@patch("core.holehe_runner.subprocess.run")
def test_check_email_in_services_error(mock_run):
    mock_run.side_effect = Exception("Holehe crashed")
    result = holehe_runner.check_email_in_services("bad-email")
    assert result == []
