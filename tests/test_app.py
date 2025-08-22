"""
test_app.py:
Unit tests for the Flask application.

This module tests the web application functionality including:
- Route handling
- Input validation (domain-only)
- Response formats
- Error handling
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    def test_healthz_endpoint(self, client):
        """Test the healthz endpoint."""
        response = client.get('/healthz')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_health_endpoint(self, client):
        """Test the health endpoint for Render compatibility."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'


class TestIndexRoute:
    def test_index_get(self, client):
        """Test the main index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Domain OSINT Scanner' in response.data
        assert b'Domain' in response.data
        assert b'Analyze' in response.data

    def test_index_contains_search_form(self, client):
        """Test that the index page contains the search form."""
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'form' in html
        assert 'domain' in html
        assert 'osint-form' in html


class TestAnalyzeRoute:
    """Test the analyze endpoint."""

    @patch('app.analyze_workflow')
    def test_analyze_post_valid_domain(self, mock_workflow, client):
        """Test POST with valid domain."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {
                'mx_records': [{'exchange': 'mx1.example.com', 'preference': 10}],
                'provider': 'Google Workspace',
                'warnings': []
            },
            'builtwith': {
                'grouped': [
                    {
                        'name': 'WordPress',
                        'count': 3,
                        'categories': ['CMS'],
                        'variants': [{'name': 'WordPress 6.0', 'count': 2}]
                    }
                ],
                'elapsedMs': 450
            }
        }
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Analysis Results' in html
        assert 'example.com' in html
        assert 'WordPress' in html
        mock_workflow.assert_called_once()

    def test_analyze_post_no_input(self, client):
        """Test POST with no input."""
        response = client.post('/analyze', data={})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert 'Please provide a domain to analyze' in html

    def test_analyze_post_empty_domain(self, client):
        """Test POST with empty domain."""
        response = client.post('/analyze', data={'domain': ''})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert 'Please provide a domain to analyze' in html

    def test_analyze_post_invalid_domain(self, client):
        """Test POST with invalid domain format."""
        response = client.post('/analyze', data={'domain': 'invalid-domain'})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert 'Invalid domain format' in html

    @patch('app.analyze_workflow')
    def test_analyze_get_json_format(self, mock_workflow, client):
        """Test GET with JSON format."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []}
        }
        
        response = client.get('/analyze?domain=example.com&format=json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        assert 'timestamp' in data
        assert 'results' in data
        assert data['results']['resolved_domain'] == 'example.com'

    @patch('app.analyze_workflow')
    def test_analyze_get_without_format(self, mock_workflow, client):
        """Test GET without format parameter."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []}
        }
        
        response = client.get('/analyze?domain=example.com')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Analysis Results' in html

    @patch('app.analyze_workflow')
    def test_analyze_workflow_error_handling(self, mock_workflow, client):
        """Test error handling when workflow fails."""
        mock_workflow.side_effect = Exception("Workflow error")
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 500
        html = response.get_data(as_text=True)
        assert 'An unexpected error occurred' in html


class TestInputValidation:
    """Test input validation logic."""

    def test_domain_validation_valid(self, client):
        """Test valid domain formats."""
        valid_domains = [
            'example.com',
            'sub.example.com',
            'example.co.uk',
            'test-domain.com'
        ]
        
        for domain in valid_domains:
            response = client.post('/analyze', data={'domain': domain})
            # Should not return 400 for valid domains (assuming mock workflow)
            assert response.status_code in [200, 500]  # 500 if mock not set up

    def test_domain_validation_invalid(self, client):
        """Test invalid domain formats."""
        invalid_domains = [
            'invalid',
            '.example.com',
            'example.',
            'example..com',
            'example_com'
        ]
        
        for domain in invalid_domains:
            response = client.post('/analyze', data={'domain': domain})
            assert response.status_code == 400


class TestResponseFormats:
    """Test different response formats."""

    @patch('app.analyze_workflow')
    def test_html_response_structure(self, mock_workflow, client):
        """Test HTML response structure."""
        mock_workflow.return_value = {
            'resolved_domain': 'test.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []}
        }
        
        response = client.post('/analyze', data={'domain': 'test.com'})
        html = response.get_data(as_text=True)
        
        # Check for expected HTML elements
        assert '<html' in html
        assert 'Analysis Results' in html
        assert 'test.com' in html

    @patch('app.analyze_workflow')
    def test_json_response_structure(self, mock_workflow, client):
        """Test JSON response structure."""
        mock_workflow.return_value = {
            'resolved_domain': 'test.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []}
        }
        
        response = client.get('/analyze?domain=test.com&format=json')
        data = response.get_json()
        
        # Check JSON structure
        assert 'ok' in data
        assert 'timestamp' in data
        assert 'results' in data
        assert data['ok'] is True


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.put('/analyze')
        assert response.status_code == 405

    @patch('app.analyze_workflow')
    def test_workflow_exception(self, mock_workflow, client):
        """Test workflow exception handling."""
        mock_workflow.side_effect = Exception("Test exception")
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 500
        html = response.get_data(as_text=True)
        assert 'unexpected error' in html.lower()


if __name__ == '__main__':
    pytest.main([__file__])
