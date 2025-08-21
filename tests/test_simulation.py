"""
<<<<<<< HEAD
test_simulation.py:

Unit tests for the simulation module.

This module tests the core simulation functionality including:
- Email pattern generation
- MX record analysis
- Account enumeration
- Technology stack detection
=======
Unit tests for the simulation module (simplified: MX + BuiltWith only).
>>>>>>> feature/remove-holehe-and-email
"""

from core.orchestrator import run_simulation


def test_run_simulation_without_builtwith(monkeypatch):
    def fake_fetch_mx_records(domain):
        return [{"host": f"mx1.{domain}", "priority": 10}]

    monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)

    result = run_simulation("Ada", "Lovelace", "example.com", use_builtwith=False)

    assert result["domain"] == "example.com"
    assert result["mx_records"] == [{"host": "mx1.example.com", "priority": 10}]
    assert "technology_stack" not in result


def test_run_simulation_with_builtwith(monkeypatch):
    def fake_fetch_mx_records(domain):
        return []

    def fake_fetch_technology_stack(domain):
        return {"cms": "WordPress", "analytics": ["Google Analytics"]}

    monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
    monkeypatch.setattr("core.builtwith_client.fetch_technology_stack", fake_fetch_technology_stack)

    result = run_simulation("Ada", "Lovelace", "example.org", use_builtwith=True)

    assert result["domain"] == "example.org"
    assert result["mx_records"] == []
    assert result["technology_stack"]["cms"] == "WordPress"
