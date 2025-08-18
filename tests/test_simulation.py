from core.orchestrator import run_simulation


def test_run_simulation_without_builtwith(monkeypatch):
    def fake_generate_email_patterns(first_name, last_name, domain):
        return [f"{first_name}.{last_name}@{domain}"]

    def fake_fetch_mx_records(domain):
        return [{"host": f"mx1.{domain}", "priority": 10}]

    def fake_enumerate_accounts(emails):
        return {"found": {"github": True}, "checked_emails": list(emails)}

    monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
    monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
    monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)

    result = run_simulation("Ada", "Lovelace", "example.com", use_builtwith=False)

    assert result["domain"] == "example.com"
    assert result["generated_emails"] == ["Ada.Lovelace@example.com"]
    assert result["mx_records"] == [{"host": "mx1.example.com", "priority": 10}]
    assert result["accounts"]["found"]["github"] is True
    assert "technology_stack" not in result


def test_run_simulation_with_builtwith(monkeypatch):
    def fake_generate_email_patterns(first_name, last_name, domain):
        return [f"{first_name.lower()}_{last_name.lower()}@{domain}"]

    def fake_fetch_mx_records(domain):
        return []

    def fake_enumerate_accounts(emails):
        return {"found": {}, "checked_emails": list(emails)}

    def fake_fetch_technology_stack(domain):
        return {"cms": "WordPress", "analytics": ["Google Analytics"]}

    monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
    monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
    monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
    monkeypatch.setattr("core.builtwith_client.fetch_technology_stack", fake_fetch_technology_stack)

    result = run_simulation("Ada", "Lovelace", "example.org", use_builtwith=True)

    assert result["generated_emails"] == ["ada_lovelace@example.org"]
    assert result["technology_stack"]["cms"] == "WordPress"