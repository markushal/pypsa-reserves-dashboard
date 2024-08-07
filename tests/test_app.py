# -*- coding: utf-8 -*-
"""Tests for the streamlit app."""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def running_app():
    """Fixture that returns a fresh instance of a running app."""
    at = AppTest.from_file("dashboard.py")
    at.run(timeout=60)
    return at


def test_app_smoke(running_app):
    """Test if the app starts up without errors."""
    assert not running_app.exception
