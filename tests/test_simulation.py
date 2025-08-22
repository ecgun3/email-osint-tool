"""
test_simulation.py:

Unit tests for the simulation module.

This module tests the core simulation functionality including:
- MX record analysis
- Technology stack detection via BuiltWith
- Core orchestration workflow
"""

import pytest
from unittest.mock import patch, MagicMock
from core.orchestrator import analyze_workflow


class TestAnalyzeWorkflow:
    """Test the main analyze_workflow function."""

    @patch('core.mx_analyzer.analyze_mx_records')
    @patch('core.builtwith_client.fetch_builtwith')
    def test_analyze_workflow_basic(self, mock_builtwith, mock_mx, monkeypatch):
        """Test basic workflow with both MX and BuiltWith."""
        # Mock MX analysis
        mock_mx.return_value = {
            'mx_records': [{'exchange': 'mx1.example.com', 'preference': 10}],
            'provider': 'Google Workspace',
            'warnings': []
        }
        
        # Mock BuiltWith
        mock_builtwith.return_value = {
            'grouped': [
                {
                    'name': 'WordPress',
                    'count': 2,
                    'categories': ['CMS'],
                    'variants': [{'name': 'WordPress 6.0', 'count': 2}]
                }
            ],
            'elapsedMs': 300
        }
        
        # Mock environment
        monkeypatch.setenv('BUILTWITH_API_KEY', 'test_key')
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=30,
            builtwith_api_key='test_key'
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert 'mx' in result
        assert 'builtwith' in result
        assert result['mx']['provider'] == 'Google Workspace'
        assert len(result['builtwith']['grouped']) == 1
        assert result['builtwith']['grouped'][0]['name'] == 'WordPress'

    @patch('core.mx_analyzer.analyze_mx_records')
    @patch('core.builtwith_client.fetch_builtwith')
    def test_analyze_workflow_mx_only(self, mock_builtwith, mock_mx, monkeypatch):
        """Test workflow with only MX analysis (no BuiltWith API key)."""
        mock_mx.return_value = {
            'mx_records': [{'exchange': 'mx2.example.com', 'preference': 20}],
            'provider': 'Microsoft 365',
            'warnings': ['Low priority MX record']
        }
        
        # Mock BuiltWith to return None (no API key)
        mock_builtwith.return_value = None
        
        # No API key
        monkeypatch.delenv('BUILTWITH_API_KEY', raising=False)
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=30,
            builtwith_api_key=None
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert 'mx' in result
        assert result['mx']['provider'] == 'Microsoft 365'
        assert 'builtwith' not in result or result['builtwith'] is None

    @patch('core.mx_analyzer.analyze_mx_records')
    def test_analyze_workflow_mx_error(self, mock_mx):
        """Test workflow when MX analysis fails."""
        mock_mx.side_effect = Exception("DNS lookup failed")
        
        with pytest.raises(Exception, match="DNS lookup failed"):
            analyze_workflow(
                domain='example.com',
                email=None,
                first_name=None,
                last_name=None,
                request_timeout=30,
                builtwith_api_key=None
            )

    @patch('core.mx_analyzer.analyze_mx_records')
    @patch('core.builtwith_client.fetch_builtwith')
    def test_analyze_workflow_builtwith_error(self, mock_builtwith, mock_mx):
        """Test workflow when BuiltWith fails but MX succeeds."""
        mock_mx.return_value = {
            'mx_records': [{'exchange': 'mx1.example.com', 'preference': 10}],
            'provider': 'Google Workspace',
            'warnings': []
        }
        
        mock_builtwith.side_effect = Exception("API rate limit exceeded")
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=30,
            builtwith_api_key='test_key'
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert 'mx' in result
        assert result['mx']['provider'] == 'Google Workspace'
        # BuiltWith should be None due to error
        assert result['builtwith'] is None

    def test_analyze_workflow_invalid_domain(self):
        """Test workflow with invalid domain."""
        with pytest.raises(ValueError):
            analyze_workflow(
                domain='',
                email=None,
                first_name=None,
                last_name=None,
                request_timeout=30,
                builtwith_api_key=None
            )

    @patch('core.mx_analyzer.analyze_mx_records')
    @patch('core.builtwith_client.fetch_builtwith')
    def test_analyze_workflow_timeout_handling(self, mock_builtwith, mock_mx):
        """Test workflow timeout handling."""
        mock_mx.return_value = {
            'mx_records': [{'exchange': 'mx1.example.com', 'preference': 10}],
            'provider': 'Google Workspace',
            'warnings': []
        }
        
        mock_builtwith.return_value = {
            'grouped': [],
            'elapsedMs': 5000  # 5 seconds
        }
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=10,  # 10 second timeout
            builtwith_api_key='test_key'
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert 'mx' in result
        assert 'builtwith' in result


class TestWorkflowEdgeCases:
    """Test edge cases and error scenarios."""

    @patch('core.mx_analyzer.analyze_mx_records')
    def test_workflow_empty_mx_results(self, mock_mx):
        """Test workflow with empty MX results."""
        mock_mx.return_value = {
            'mx_records': [],
            'provider': 'Unknown',
            'warnings': ['No MX records found']
        }
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=30,
            builtwith_api_key=None
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert result['mx']['mx_records'] == []
        assert result['mx']['provider'] == 'Unknown'
        assert 'No MX records found' in result['mx']['warnings']

    @patch('core.mx_analyzer.analyze_mx_records')
    @patch('core.builtwith_client.fetch_builtwith')
    def test_workflow_large_builtwith_results(self, mock_builtwith, mock_mx):
        """Test workflow with large BuiltWith results."""
        mock_mx.return_value = {
            'mx_records': [{'exchange': 'mx1.example.com', 'preference': 10}],
            'provider': 'Google Workspace',
            'warnings': []
        }
        
        # Large BuiltWith result
        mock_builtwith.return_value = {
            'grouped': [
                {
                    'name': f'Technology_{i}',
                    'count': i,
                    'categories': ['Category'],
                    'variants': [{'name': f'Variant_{i}', 'count': i}]
                }
                for i in range(1, 101)  # 100 technologies
            ],
            'elapsedMs': 1200
        }
        
        result = analyze_workflow(
            domain='example.com',
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=30,
            builtwith_api_key='test_key'
        )
        
        assert result['resolved_domain'] == 'example.com'
        assert 'mx' in result
        assert 'builtwith' in result
        assert len(result['builtwith']['grouped']) == 100
        assert result['builtwith']['elapsedMs'] == 1200


if __name__ == '__main__':
    pytest.main([__file__])
