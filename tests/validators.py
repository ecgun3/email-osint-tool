# tests/test_validators.py
import pytest
from utils.validators import is_valid_email, is_valid_domain

def test_valid_email():
    assert is_valid_email("user@example.com") is True

def test_invalid_email():
    assert is_valid_email("not-an-email") is False
    assert is_valid_email("@nouser.com") is False

def test_valid_domain():
    assert is_valid_domain("example.com") is True

def test_invalid_domain():
    assert is_valid_domain("http://example.com") is False
    assert is_valid_domain("not a domain") is False
