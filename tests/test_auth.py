"""Tests for auth.py authentication module"""
import pytest
from unittest.mock import AsyncMock, patch
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


def create_mock_locator():
    """Create a properly mocked Playwright locator"""
    locator = AsyncMock()
    locator.wait_for = AsyncMock()
    locator.fill = AsyncMock()
    locator.click = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    return locator


@pytest.mark.asyncio
async def test_authenticate_success():
    """Test successful authentication"""
    from auth import authenticate
    
    # Mock page and locators
    page = AsyncMock()
    email_input = create_mock_locator()
    password_input = create_mock_locator()
    submit_button = create_mock_locator()
    
    # Setup locator to return specific mocks based on selector
    def get_locator(selector):
        if 'email' in selector:
            return email_input
        elif 'password' in selector:
            return password_input
        elif 'submit' in selector:
            return submit_button
        return create_mock_locator()
    
    page.locator = get_locator
    page.wait_for_url = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.url = "https://iris.infocasas.com.uy/proyectos?country=1"
    
    # Execute
    result = await authenticate(page, email="test@example.com", password="testpass")
    
    # Assert
    assert result is True
    email_input.fill.assert_called_once_with("test@example.com")
    password_input.fill.assert_called_once_with("testpass")
    submit_button.click.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_no_credentials():
    """Test authentication fails when no credentials provided"""
    from auth import authenticate
    
    page = AsyncMock()
    
    # Mock config values to be None
    with patch('auth.IRIS_EMAIL', None), patch('auth.IRIS_PASSWORD', None):
        result = await authenticate(page)
    
    # Should return False when no credentials
    assert result is False


@pytest.mark.asyncio
async def test_authenticate_missing_email():
    """Test authentication fails when only password provided"""
    from auth import authenticate
    
    page = AsyncMock()
    
    # Only password, no email
    result = await authenticate(page, password="testpass")
    
    # Should return False
    assert result is False


@pytest.mark.asyncio
async def test_authenticate_stays_on_login_page():
    """Test authentication fails when staying on login page"""
    from auth import authenticate
    
    page = AsyncMock()
    email_input = create_mock_locator()
    password_input = create_mock_locator()
    submit_button = create_mock_locator()
    
    def get_locator(selector):
        if 'email' in selector:
            return email_input
        elif 'password' in selector:
            return password_input
        elif 'submit' in selector:
            return submit_button
        return create_mock_locator()
    
    page.locator = get_locator
    page.wait_for_url = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.url = "https://iris.infocasas.com.uy/iniciar-sesion"
    
    result = await authenticate(page, email="wrong@example.com", password="wrongpass")
    
    # Should return False
    assert result is False


@pytest.mark.asyncio
async def test_authenticate_redirect_to_feed():
    """Test authentication when redirects to feed page"""
    from auth import authenticate
    
    page = AsyncMock()
    email_input = create_mock_locator()
    password_input = create_mock_locator()
    submit_button = create_mock_locator()
    
    def get_locator(selector):
        if 'email' in selector:
            return email_input
        elif 'password' in selector:
            return password_input
        elif 'submit' in selector:
            return submit_button
        return create_mock_locator()
    
    page.locator = get_locator
    page.wait_for_url = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.url = "https://iris.infocasas.com.uy/feed"
    page.goto = AsyncMock()
    
    result = await authenticate(page, email="test@example.com", password="testpass")
    
    # Should still return True (logged in successfully)
    assert result is True


@pytest.mark.asyncio
async def test_authenticate_with_config_defaults():
    """Test authentication uses config values when not provided"""
    from auth import authenticate
    
    page = AsyncMock()
    email_input = create_mock_locator()
    password_input = create_mock_locator()
    submit_button = create_mock_locator()
    
    def get_locator(selector):
        if 'email' in selector:
            return email_input
        elif 'password' in selector:
            return password_input
        elif 'submit' in selector:
            return submit_button
        return create_mock_locator()
    
    page.locator = get_locator
    page.wait_for_url = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.url = "https://iris.infocasas.com.uy/proyectos"
    
    with patch('auth.IRIS_EMAIL', 'config@example.com'), patch('auth.IRIS_PASSWORD', 'configpass'):
        result = await authenticate(page)
    
    assert result is True
    email_input.fill.assert_called_once_with('config@example.com')
    password_input.fill.assert_called_once_with('configpass')


@pytest.mark.asyncio
async def test_authenticate_load_state_timeout():
    """Test authentication succeeds even if load state times out"""
    from auth import authenticate
    
    page = AsyncMock()
    email_input = create_mock_locator()
    password_input = create_mock_locator()
    submit_button = create_mock_locator()
    
    def get_locator(selector):
        if 'email' in selector:
            return email_input
        elif 'password' in selector:
            return password_input
        elif 'submit' in selector:
            return submit_button
        return create_mock_locator()
    
    page.locator = get_locator
    page.wait_for_url = AsyncMock()
    page.wait_for_load_state.side_effect = PlaywrightTimeoutError("Timeout")
    page.url = "https://iris.infocasas.com.uy/proyectos"
    
    result = await authenticate(page, email="test@example.com", password="testpass")
    
    # Should still succeed - load state timeout is just a warning
    assert result is True
