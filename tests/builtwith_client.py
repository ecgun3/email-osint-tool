# tests/test_builtwith_client.py
import pytest
from unittest.mock import patch
from core import builtwith_client

@patch("core.builtwith_client.requests.get")
def test_get_technologies_by_domain_success(mock_get):
    mock_get.return_value.json.return_value = {
        "Technologies": [
            {"Name": "React", "Categories": [{"Name": "JavaScript Frameworks"}]},
            {"Name": "Nginx", "Categories": [{"Name": "Web Servers"}]},
        ]
    }
    result = builtwith_client.get_technologies_by_domain("example.com")
    assert "JavaScript Frameworks" in result
    assert "Web Servers" in result

@patch("core.builtwith_client.requests.get")
def test_get_technologies_by_domain_invalid_domain(mock_get):
    mock_get.side_effect = Exception("Invalid domain")
    result = builtwith_client.get_technologies_by_domain("invalid-domain")
    assert result == []
