"""
test_simulation.py:

Unit tests for the simulation module.

This module tests the core simulation functionality including:
- Email pattern generation
- MX record analysis
- Account enumeration
- Technology stack detection
"""

import pytest
from unittest.mock import Mock, patch
from core.orchestrator import run_simulation


class TestRunSimulation:
    """Test cases for the run_simulation function."""
    
    def test_run_simulation_without_builtwith(self, monkeypatch):
        """Test simulation without BuiltWith integration."""
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return [f"{first_name}.{last_name}@{domain}"]
        
        def fake_fetch_mx_records(domain):
            return [{"host": f"mx1.{domain}", "priority": 10}]
        
        def fake_enumerate_accounts(emails):
            return {"found": {"github": True}, "checked_emails": list(emails)}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        
        # Execute test
        result = run_simulation("Ada", "Lovelace", "example.com", use_builtwith=False)
        
        # Assertions
        assert result["domain"] == "example.com"
        assert result["generated_emails"] == ["Ada.Lovelace@example.com"]
        assert result["mx_records"] == [{"host": "mx1.example.com", "priority": 10}]
        assert result["accounts"]["found"]["github"] is True
        assert "technology_stack" not in result
    
    def test_run_simulation_with_builtwith(self, monkeypatch):
        """Test simulation with BuiltWith integration."""
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return [f"{first_name.lower()}_{last_name.lower()}@{domain}"]
        
        def fake_fetch_mx_records(domain):
            return []
        
        def fake_enumerate_accounts(emails):
            return {"found": {}, "checked_emails": list(emails)}
        
        def fake_fetch_technology_stack(domain):
            return {"cms": "WordPress", "analytics": ["Google Analytics"]}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        monkeypatch.setattr("core.builtwith_client.fetch_technology_stack", fake_fetch_technology_stack)
        
        # Execute test
        result = run_simulation("Ada", "Lovelace", "example.org", use_builtwith=True)
        
        # Assertions
        assert result["generated_emails"] == ["ada_lovelace@example.org"]
        assert result["technology_stack"]["cms"] == "WordPress"
        assert "technology_stack" in result
    
    def test_run_simulation_empty_inputs(self, monkeypatch):
        """Test simulation with empty inputs."""
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return []
        
        def fake_fetch_mx_records(domain):
            return []
        
        def fake_enumerate_accounts(emails):
            return {"found": {}, "checked_emails": list(emails)}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        
        # Execute test
        result = run_simulation("", "", "example.com", use_builtwith=False)
        
        # Assertions
        assert result["domain"] == "example.com"
        assert result["generated_emails"] == []
        assert result["mx_records"] == []
    
    def test_run_simulation_special_characters(self, monkeypatch):
        """Test simulation with special characters in names."""
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return [f"{first_name}-{last_name}@{domain}"]
        
        def fake_fetch_mx_records(domain):
            return [{"host": f"mx.{domain}", "priority": 5}]
        
        def fake_enumerate_accounts(emails):
            return {"found": {}, "checked_emails": list(emails)}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        
        # Execute test
        result = run_simulation("Jean-Pierre", "O'Connor", "test.org", use_builtwith=False)
        
        # Assertions
        assert result["generated_emails"] == ["Jean-Pierre-O'Connor@test.org"]
        assert len(result["mx_records"]) == 1
        assert result["mx_records"][0]["host"] == "mx.test.org"


class TestSimulationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_run_simulation_none_values(self, monkeypatch):
        """Test simulation with None values."""
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return []
        
        def fake_fetch_mx_records(domain):
            return []
        
        def fake_enumerate_accounts(emails):
            return {"found": {}, "checked_emails": list(emails)}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        
        # Execute test
        result = run_simulation(None, None, "example.com", use_builtwith=False)
        
        # Assertions
        assert result["domain"] == "example.com"
        assert result["generated_emails"] == []
    
    def test_run_simulation_long_domain(self, monkeypatch):
        """Test simulation with very long domain names."""
        long_domain = "a" * 63 + ".b" * 63 + ".c" * 63 + ".com"
        
        # Mock dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            return [f"test@{domain}"]
        
        def fake_fetch_mx_records(domain):
            return []
        
        def fake_enumerate_accounts(emails):
            return {"found": {}, "checked_emails": list(emails)}
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        
        # Execute test
        result = run_simulation("Test", "User", long_domain, use_builtwith=False)
        
        # Assertions
        assert result["domain"] == long_domain
        assert len(result["generated_emails"]) == 1


class TestSimulationIntegration:
    """Integration-style tests for simulation workflow."""
    
    @pytest.mark.integration
    def test_full_simulation_workflow(self, monkeypatch):
        """Test complete simulation workflow with all components."""
        # Mock all dependencies
        def fake_generate_email_patterns(first_name, last_name, domain):
            patterns = []
            if first_name and last_name:
                patterns.extend([
                    f"{first_name}.{last_name}@{domain}",
                    f"{first_name.lower()}_{last_name.lower()}@{domain}",
                    f"{first_name[0]}{last_name}@{domain}"
                ])
            return patterns
        
        def fake_fetch_mx_records(domain):
            return [
                {"host": f"mx1.{domain}", "priority": 10},
                {"host": f"mx2.{domain}", "priority": 20}
            ]
        
        def fake_enumerate_accounts(emails):
            return {
                "found": {"github": True, "twitter": False},
                "checked_emails": list(emails)
            }
        
        def fake_fetch_technology_stack(domain):
            return {
                "cms": "WordPress",
                "analytics": ["Google Analytics", "Facebook Pixel"],
                "hosting": "AWS"
            }
        
        # Apply mocks
        monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
        monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
        monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
        monkeypatch.setattr("core.builtwith_client.fetch_technology_stack", fake_fetch_technology_stack)
        
        # Execute test
        result = run_simulation("John", "Doe", "company.com", use_builtwith=True)
        
        # Comprehensive assertions
        assert result["domain"] == "company.com"
        assert len(result["generated_emails"]) == 3
        assert len(result["mx_records"]) == 2
        assert result["accounts"]["found"]["github"] is True
        assert result["technology_stack"]["cms"] == "WordPress"
        assert "analytics" in result["technology_stack"]
        assert "hosting" in result["technology_stack"]


# Fixtures for common test data
@pytest.fixture
def sample_domain():
    """Sample domain for testing."""
    return "example.com"


@pytest.fixture
def sample_names():
    """Sample names for testing."""
    return ("Alice", "Johnson")


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock all dependencies for testing."""
    def fake_generate_email_patterns(first_name, last_name, domain):
        return [f"{first_name}.{last_name}@{domain}"]
    
    def fake_fetch_mx_records(domain):
        return [{"host": f"mx.{domain}", "priority": 10}]
    
    def fake_enumerate_accounts(emails):
        return {"found": {}, "checked_emails": list(emails)}
    
    def fake_fetch_technology_stack(domain):
        return {"cms": "WordPress"}
    
    monkeypatch.setattr("core.email_patterns.generate_email_patterns", fake_generate_email_patterns)
    monkeypatch.setattr("core.mx_analyzer.fetch_mx_records", fake_fetch_mx_records)
    monkeypatch.setattr("core.holehe_runner.enumerate_accounts", fake_enumerate_accounts)
    monkeypatch.setattr("core.builtwith_client.fetch_technology_stack", fake_fetch_technology_stack)
    
    return {
        "generate_email_patterns": fake_generate_email_patterns,
        "fetch_mx_records": fake_fetch_mx_records,
        "enumerate_accounts": fake_enumerate_accounts,
        "fetch_technology_stack": fake_fetch_technology_stack
    }


# Performance tests
class TestSimulationPerformance:
    """Performance tests for simulation functions."""
    
    def test_simulation_performance_large_inputs(self, mock_dependencies):
        """Test simulation performance with large inputs."""
        import time
        
        start_time = time.time()
        result = run_simulation("A" * 100, "B" * 100, "example.com", use_builtwith=False)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete within 1 second
        assert result["domain"] == "example.com"
    
    def test_simulation_memory_usage(self, mock_dependencies):
        """Test simulation memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run multiple simulations
        for _ in range(10):
            run_simulation("Test", "User", "example.com", use_builtwith=False)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024
