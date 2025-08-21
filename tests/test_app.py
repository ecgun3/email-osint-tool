"""
Unit tests for the Flask application.

This module tests the web application functionality including:
- Route handling
- Input validation (domain-only)
- Response formats
"""

import pytest
import json
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_healthz_endpoint(client):
    r = client.get('/healthz')
    assert r.status_code == 200
    assert json.loads(r.data)['status'] == 'ok'

@patch('app.analyze_workflow')
def test_analyze_post_valid_domain(mock_workflow, client):
    mock_workflow.return_value = {
        'resolved_domain': 'example.com',
        'mx': {'mx_records': []},
        'builtwith': {'grouped': []}
    }
    r = client.post('/analyze', data={'domain': 'example.com'})
    assert r.status_code == 200
    assert b'Analysis Results' in r.data


def test_analyze_post_no_input(client):
    r = client.post('/analyze', data={})
    assert r.status_code == 400
    assert b'Please provide a domain to analyze' in r.data or b'Please provide a domain' in r.data


def test_analyze_get_json_format(client):
    with patch('app.analyze_workflow') as mock_wf:
        mock_wf.return_value = {
            'resolved_domain': 'example.com',
            'mx': {'mx_records': []},
            'builtwith': {'grouped': []}
        }
        r = client.get('/analyze?domain=example.com&format=json')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['ok'] is True
        assert 'results' in data
        assert 'timestamp' in data