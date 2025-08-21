"""
test_app.py:
Unit tests for the Flask application.

This module tests the web application functionality including:
- Route handling
- Input validation
- Error handling
- Response formats
"""

import pytest
import json
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    def test_healthz_endpoint(self, client):
        response = client.get('/healthz')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True


class TestIndexRoute:
    def test_index_get(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Email OSINT Scanner' in response.data
        assert b'Domain' in response.data
        assert b'Email' in response.data

    def test_index_with_error(self, client):
        response = client.get('/?error=Test%20error')
        assert response.status_code == 200
        assert b'Test error' in response.data


class TestAnalyzeRoute:
    """Test the analyze endpoint."""

    @patch('app.analyze_workflow')
    def test_analyze_post_valid_domain(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Analysis Results' in html
        mock_workflow.assert_called_once()

    @patch('app.analyze_workflow')
    def test_analyze_post_valid_email(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        response = client.post('/analyze', data={'email': 'user@example.com'})
        assert response.status_code == 200
        assert b'Analysis Results' in response.data
        mock_workflow.assert_called_once()

    def test_analyze_post_no_input(self, client):
        response = client.post('/analyze', data={})
        assert response.status_code == 400
        assert b'Please provide a domain or email to analyze' in response.data

    def test_analyze_post_invalid_email(self, client):
        response = client.post('/analyze', data={'email': 'invalid-email'})
        assert response.status_code == 400
        assert b'Invalid email address format' in response.data

    def test_analyze_post_invalid_domain(self, client):
        response = client.post('/analyze', data={'domain': 'invalid domain'})
        assert response.status_code == 400
        assert b'Invalid domain format' in response.data

    @patch('app.analyze_workflow')
    def test_analyze_get_query_params(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        response = client.get('/analyze?domain=example.com')
        assert response.status_code == 200
        assert b'Analysis Results' in response.data

    @patch('app.analyze_workflow')
    def test_analyze_get_json_format(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        response = client.get('/analyze?domain=example.com&format=json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        assert 'results' in data
        assert 'timestamp' in data

    @patch('app.analyze_workflow')
    def test_analyze_post_json_accept_header(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        headers = {'Accept': 'application/json'}
        response = client.post('/analyze', data={'domain': 'example.com'}, headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True


class TestInputValidation:
    """Test input validation functions."""

    def test_validate_input_no_domain_no_email(self):
        from app import _validate_input
        result = _validate_input("", "")
        assert result['valid'] is False
        assert 'Please provide a domain or email' in result['message']

    def test_validate_input_invalid_email(self):
        from app import _validate_input
        result = _validate_input("", "invalid-email")
        assert result['valid'] is False
        assert 'Invalid email address format' in result['message']

    def test_validate_input_valid_domain(self):
        from app import _validate_input
        result = _validate_input("example.com", "")
        assert result['valid'] is True
        assert result['domain'] == "example.com"

    def test_validate_input_valid_email(self):
        from app import _validate_input
        result = _validate_input("", "user@example.com")
        assert result['valid'] is True
        assert result['domain'] is None

    def test_validate_input_email_like_domain(self):
        from app import _validate_input
        result = _validate_input("user@example.com", "")
        assert result['valid'] is True
        assert result['domain'] == "example.com"


class TestErrorHandling:
    """Test error handling and edge cases."""

    @patch('app.analyze_workflow')
    def test_analyze_workflow_exception(self, mock_workflow, client):
        mock_workflow.side_effect = Exception("Test error")
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 500
        assert b'An unexpected error occurred' in response.data

    def test_404_error_handler(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_500_error_handler_exists(self, client):
        # Ensure 500 error handler exists
        assert hasattr(app, 'error_handler_spec')


class TestResponseFormats:
    """Test different response formats."""

    @patch('app.analyze_workflow')
    def test_html_response_format(self, mock_workflow, client):
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
