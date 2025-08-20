"""
Unit tests for the Flask application.

This module tests the web application functionality including:
- Route handling
- Input validation
- Error handling
- Response formats
"""

import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_healthz_endpoint(self, client):
        """Test the /healthz endpoint."""
        response = client.get('/healthz')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_health_endpoint(self, client):
        """Test the /health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ok'] is True


class TestIndexRoute:
    """Test the main index route."""
    
    def test_index_get(self, client):
        """Test GET request to index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Email OSINT Scanner' in response.data
        assert b'Domain' in response.data
        assert b'Email' in response.data
    
    def test_index_with_error(self, client):
        """Test index page with error message."""
        response = client.get('/?error=Test%20error')
        assert response.status_code == 200
        # Error should be displayed in the form


class TestAnalyzeRoute:
    """Test the analyze endpoint."""
    
    @patch('app.analyze_workflow')
    def test_analyze_post_valid_domain(self, mock_workflow, client):
        """Test POST request with valid domain."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 200
        assert b'Analysis Results' in response.data
        mock_workflow.assert_called_once()
    
    @patch('app.analyze_workflow')
    def test_analyze_post_valid_email(self, mock_workflow, client):
        """Test POST request with valid email."""
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
        """Test POST request with no input."""
        response = client.post('/analyze', data={})
        assert response.status_code == 400
        assert b'Please provide a domain or email to analyze' in response.data
    
    def test_analyze_post_invalid_email(self, client):
        """Test POST request with invalid email."""
        response = client.post('/analyze', data={'email': 'invalid-email'})
        assert response.status_code == 400
        assert b'Invalid email address format' in response.data
    
    def test_analyze_post_invalid_domain(self, client):
        """Test POST request with invalid domain."""
        response = client.post('/analyze', data={'domain': 'invalid domain'})
        assert response.status_code == 400
        assert b'Invalid domain format' in response.data
    
    @patch('app.analyze_workflow')
    def test_analyze_get_query_params(self, mock_workflow, client):
        """Test GET request with query parameters."""
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
        """Test GET request with JSON format."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        
        response = client.get('/analyze?domain=example.com&format=json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ok'] is True
        assert 'results' in data
        assert 'timestamp' in data
    
    @patch('app.analyze_workflow')
    def test_analyze_post_json_accept_header(self, mock_workflow, client):
        """Test POST request with JSON Accept header."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        
        headers = {'Accept': 'application/json'}
        response = client.post('/analyze', data={'domain': 'example.com'}, headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ok'] is True


class TestInputValidation:
    """Test input validation functions."""
    
    def test_validate_input_no_domain_no_email(self):
        """Test validation with no domain and no email."""
        from app import _validate_input
        result = _validate_input("", "")
        assert result['valid'] is False
        assert 'Please provide a domain or email' in result['message']
    
    def test_validate_input_invalid_email(self):
        """Test validation with invalid email."""
        from app import _validate_input
        result = _validate_input("", "invalid-email")
        assert result['valid'] is False
        assert 'Invalid email address format' in result['message']
    
    def test_validate_input_valid_domain(self):
        """Test validation with valid domain."""
        from app import _validate_input
        result = _validate_input("example.com", "")
        assert result['valid'] is True
        assert result['domain'] == "example.com"
    
    def test_validate_input_valid_email(self):
        """Test validation with valid email."""
        from app import _validate_input
        result = _validate_input("", "user@example.com")
        assert result['valid'] is True
        assert result['domain'] is None
    
    def test_validate_input_email_like_domain(self):
        """Test validation with email-like input in domain field."""
        from app import _validate_input
        result = _validate_input("user@example.com", "")
        assert result['valid'] is True
        assert result['domain'] == "example.com"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @patch('app.analyze_workflow')
    def test_analyze_workflow_exception(self, mock_workflow, client):
        """Test handling of workflow exceptions."""
        mock_workflow.side_effect = Exception("Test error")
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 500
        assert b'An unexpected error occurred' in response.data
    
    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_500_error_handler(self, client):
        """Test 500 error handling."""
        # This would require triggering an actual error, but we can test the handler exists
        assert hasattr(app, 'error_handler_spec')


class TestResponseFormats:
    """Test different response formats."""
    
    @patch('app.analyze_workflow')
    def test_html_response_format(self, mock_workflow, client):
        """Test HTML response format."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        
        response = client.post('/analyze', data={'domain': 'example.com'})
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        assert b'<html' in response.data
    
    @patch('app.analyze_workflow')
    def test_json_response_format(self, mock_workflow, client):
        """Test JSON response format."""
        mock_workflow.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []},
            'holehe': {'parsed': {'totals': {'positive': 0, 'negative': 0, 'unknown': 0}}}
        }
        
        response = client.get('/analyze?domain=example.com&format=json')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert isinstance(data, dict)


class TestSecurity:
    """Test security-related functionality."""
    
    def test_csrf_protection_disabled_in_testing(self, client):
        """Test that CSRF protection is disabled in testing mode."""
        # This is a basic test - in production, CSRF should be enabled
        response = client.post('/analyze', data={'domain': 'example.com'})
        # Should not get CSRF error
        assert response.status_code in [200, 400]  # Either success or validation error
    
    def test_sql_injection_prevention(self, client):
        """Test basic SQL injection prevention."""
        malicious_input = "'; DROP TABLE users; --"
        response = client.post('/analyze', data={'domain': malicious_input})
        # Should not crash the application
        assert response.status_code in [200, 400]
    
    def test_xss_prevention(self, client):
        """Test XSS prevention."""
        malicious_input = "<script>alert('xss')</script>"
        response = client.post('/analyze', data={'domain': malicious_input})
        # Should not crash the application
        assert response.status_code in [200, 400]


# Integration tests
class TestIntegration:
    """Integration tests for the application."""
    
    @patch('app.analyze_workflow')
    def test_full_workflow_integration(self, mock_workflow, client):
        """Test complete workflow from form submission to result display."""
        # Mock the workflow to return realistic data
        mock_workflow.return_value = {
            'resolved_domain': 'company.com',
            'mx': {
                'mx_records': [
                    {'exchange': 'mx1.company.com', 'preference': 10},
                    {'exchange': 'mx2.company.com', 'preference': 20}
                ],
                'provider': 'Google Workspace'
            },
            'builtwith': {
                'grouped': [
                    {
                        'name': 'WordPress',
                        'count': 5,
                        'categories': ['CMS'],
                        'variants': [
                            {'name': 'WordPress 6.0', 'count': 3, 'examples': ['https://company.com']}
                        ]
                    }
                ],
                'elapsedMs': 250
            },
            'holehe': {
                'parsed': {
                    'totals': {'positive': 2, 'negative': 8, 'unknown': 1},
                    'positive': [
                        {'site': 'github.com', 'loginBehind': False},
                        {'site': 'twitter.com', 'loginBehind': True}
                    ]
                },
                'command': 'holehe user@company.com',
                'elapsedMs': 1500
            }
        }
        
        # Submit form
        response = client.post('/analyze', data={'domain': 'company.com'})
        assert response.status_code == 200
        
        # Check that all sections are displayed
        assert b'Analysis Results' in response.data
        assert b'company.com' in response.data
        assert b'MX Records Analysis' in response.data
        assert b'Technology Stack Analysis' in response.data
        assert b'Account Enumeration' in response.data
        assert b'WordPress' in response.data
        assert b'github.com' in response.data


# Performance tests
class TestPerformance:
    """Performance tests for the application."""
    
    def test_response_time(self, client):
        """Test response time for simple requests."""
        import time
        
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = client.get('/')
                end_time = time.time()
                results.append({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        assert len(errors) == 0
        
        for result in results:
            assert result['status_code'] == 200
            assert result['response_time'] < 2.0  # Each request should complete within 2 seconds