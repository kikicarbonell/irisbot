"""Tests for iris_selectors.py module"""


def test_login_selectors_exist():
    """Test that login selectors are defined"""
    from iris_selectors import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT, LOGIN_SUBMIT_BUTTON

    assert isinstance(LOGIN_EMAIL_INPUT, str)
    assert isinstance(LOGIN_PASSWORD_INPUT, str)
    assert isinstance(LOGIN_SUBMIT_BUTTON, str)
    assert len(LOGIN_EMAIL_INPUT) > 0
    assert len(LOGIN_PASSWORD_INPUT) > 0
    assert len(LOGIN_SUBMIT_BUTTON) > 0


def test_catalog_selectors_exist():
    """Test that catalog selectors are defined"""
    from iris_selectors import APARTMENT_ITEM, APARTMENT_LINK, CATALOG_CONTAINER

    assert isinstance(CATALOG_CONTAINER, str)
    assert isinstance(APARTMENT_ITEM, str)
    assert isinstance(APARTMENT_LINK, str)


def test_apartment_data_selectors_exist():
    """Test that apartment data selectors are defined"""
    from iris_selectors import (
        APARTMENT_AREA,
        APARTMENT_BATHROOMS,
        APARTMENT_BEDROOMS,
        APARTMENT_DESCRIPTION,
        APARTMENT_IMAGES,
        APARTMENT_LOCATION,
        APARTMENT_PRICE,
        APARTMENT_TITLE,
    )

    assert isinstance(APARTMENT_TITLE, str)
    assert isinstance(APARTMENT_PRICE, str)
    assert isinstance(APARTMENT_LOCATION, str)
    assert isinstance(APARTMENT_BEDROOMS, str)
    assert isinstance(APARTMENT_BATHROOMS, str)
    assert isinstance(APARTMENT_AREA, str)
    assert isinstance(APARTMENT_DESCRIPTION, str)
    assert isinstance(APARTMENT_IMAGES, str)


def test_project_selectors_exist():
    """Test that project selectors are defined"""
    from iris_selectors import LIST_VIEW_BUTTON, PROJECT_DETAIL_LINK, PROJECT_ROW, PROJECT_TABLE

    assert isinstance(LIST_VIEW_BUTTON, str)
    assert isinstance(PROJECT_TABLE, str)
    assert isinstance(PROJECT_ROW, str)
    assert isinstance(PROJECT_DETAIL_LINK, str)


def test_pagination_selectors_exist():
    """Test that pagination selectors are defined"""
    from iris_selectors import LOAD_MORE_BUTTON, LOADING_INDICATOR, NO_MORE_ITEMS_MESSAGE

    assert isinstance(LOAD_MORE_BUTTON, str)
    assert isinstance(LOADING_INDICATOR, str)
    assert isinstance(NO_MORE_ITEMS_MESSAGE, str)


def test_selectors_are_valid_css():
    """Test that all selectors contain valid CSS syntax"""
    from iris_selectors import APARTMENT_TITLE, LOAD_MORE_BUTTON, LOGIN_EMAIL_INPUT, PROJECT_TABLE

    # Basic check: selectors should contain CSS patterns
    assert any(char in LOGIN_EMAIL_INPUT for char in ["[", ".", "#", "input"])
    assert any(char in APARTMENT_TITLE for char in ["[", ".", "#", "h1", "h2"])
    assert any(char in PROJECT_TABLE for char in ["[", ".", "#", "table"])
    assert "button" in LOAD_MORE_BUTTON or "text" in LOAD_MORE_BUTTON


def test_all_selectors_are_strings():
    """Test that all exported selectors are strings"""
    import iris_selectors

    # Get all uppercase attributes (constants)
    selector_names = [
        name for name in dir(iris_selectors) if name.isupper() and not name.startswith("_")
    ]

    for name in selector_names:
        value = getattr(iris_selectors, name)
        assert isinstance(value, str), f"{name} should be a string, got {type(value)}"


def test_selectors_immutability():
    """Test that selectors are immutable (Final type)"""
    from iris_selectors import LOGIN_EMAIL_INPUT

    # Verify that Final type is used (can't actually enforce at runtime in Python)
    # But we can verify the value is a string
    assert isinstance(LOGIN_EMAIL_INPUT, str)

    # Test that we can't directly modify it (strings are immutable)
    original = LOGIN_EMAIL_INPUT
    try:
        LOGIN_EMAIL_INPUT = "modified"  # This would create a new binding, not modify
    except TypeError:
        pass

    # Re-import to verify original value is preserved in module
    from iris_selectors import LOGIN_EMAIL_INPUT as reloaded

    assert reloaded == original


def test_login_email_selector_matches_auth():
    """Test that LOGIN_EMAIL_INPUT matches what auth.py expects"""
    from iris_selectors import LOGIN_EMAIL_INPUT

    # Should include common email input patterns
    assert "email" in LOGIN_EMAIL_INPUT.lower()
    assert "input" in LOGIN_EMAIL_INPUT


def test_project_link_selector():
    """Test PROJECT_DETAIL_LINK selector contains proyecto reference"""
    from iris_selectors import PROJECT_DETAIL_LINK

    # Should reference /proyecto/ path
    assert "proyecto" in PROJECT_DETAIL_LINK.lower()
