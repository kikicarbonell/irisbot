"""Tests for project change detection functionality."""

import pytest

from scrape_catalog_phase1 import compare_project_data, extract_project_id_from_url, format_change_message


class TestChangeDetection:
    """Tests for the compare_project_data function."""

    def test_compare_identical_projects_no_changes(self):
        """Test that identical projects are detected as having no changes."""
        existing = (
            235,  # project_id
            "/proyecto/235?operation=Venta",  # detail_url
            "Torre Vista",  # name
            "Pocitos",  # zone
            "INMEDIATA",  # delivery_type
            None,  # delivery_torres
            "A estrenar",  # project_status
            "USD 120.000",  # price_from
            "Developer Corp",  # developer
            "3%",  # commission
            1,  # has_ley_vp
            "Av. Brasil 2000",  # location
            None,  # image_url
            "2026-02-19 10:00:00",  # scraped_at
            "2026-02-19 10:00:00",  # updated_at
        )

        new_data = {
            "detail_url": "/proyecto/235?operation=Venta",
            "name": "Torre Vista",
            "zone": "Pocitos",
            "delivery_type": "INMEDIATA",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 120.000",
            "developer": "Developer Corp",
            "commission": "3%",
            "has_ley_vp": True,
            "location": "Av. Brasil 2000",
            "image_url": None,
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is False
        assert changes_dict == {}

    def test_compare_projects_with_name_change(self):
        """Test detection of name change."""
        existing = (
            235,
            "/proyecto/235?operation=Venta",
            "Torre Vista Old",
            "Pocitos",
            "INMEDIATA",
            None,
            "A estrenar",
            "USD 120.000",
            "Developer Corp",
            "3%",
            1,
            "Av. Brasil 2000",
            None,
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        new_data = {
            "detail_url": "/proyecto/235?operation=Venta",
            "name": "Torre Vista New",
            "zone": "Pocitos",
            "delivery_type": "INMEDIATA",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 120.000",
            "developer": "Developer Corp",
            "commission": "3%",
            "has_ley_vp": True,
            "location": "Av. Brasil 2000",
            "image_url": None,
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert "name" in changes_dict
        assert changes_dict["name"]["old"] == "Torre Vista Old"
        assert changes_dict["name"]["new"] == "Torre Vista New"

    def test_compare_projects_with_multiple_changes(self):
        """Test detection of multiple changes."""
        existing = (
            682,
            "/proyecto/682?operation=Venta",
            "Proyecto A",
            "Centro",
            "2026",
            None,
            "En construcción",
            "USD 200.000",
            "Old Developer",
            "4%",
            0,
            "Calle 1",
            None,
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        new_data = {
            "detail_url": "/proyecto/682?operation=Venta",
            "name": "Proyecto A Updated",
            "zone": "Centro",
            "delivery_type": "2025",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 250.000",
            "developer": "New Developer",
            "commission": "5%",
            "has_ley_vp": True,
            "location": "Calle 2",
            "image_url": "http://example.com/img.png",
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert len(changes_dict) == 9
        assert "name" in changes_dict
        assert "delivery_type" in changes_dict
        assert "price_from" in changes_dict
        assert "developer" in changes_dict
        assert "commission" in changes_dict
        assert "has_ley_vp" in changes_dict
        assert "project_status" in changes_dict
        assert "location" in changes_dict
        assert "image_url" in changes_dict

    def test_compare_projects_price_change(self):
        """Test detection of price change."""
        existing = (
            450,
            "/proyecto/450?operation=Venta",
            "Proyecto B",
            "Malvín",
            "INMEDIATA",
            None,
            "A estrenar",
            "USD 150.000",
            "Dev Inc",
            "3%",
            1,
            "Av. Acoyte",
            None,
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        new_data = {
            "detail_url": "/proyecto/450?operation=Venta",
            "name": "Proyecto B",
            "zone": "Malvín",
            "delivery_type": "INMEDIATA",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 175.000",
            "developer": "Dev Inc",
            "commission": "3%",
            "has_ley_vp": True,
            "location": "Av. Acoyte",
            "image_url": None,
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert "price_from" in changes_dict
        assert changes_dict["price_from"]["old"] == "USD 150.000"
        assert changes_dict["price_from"]["new"] == "USD 175.000"

    def test_compare_projects_null_to_value(self):
        """Test detection of change from NULL to value."""
        existing = (
            555,
            "/proyecto/555?operation=Venta",
            "Proyecto C",
            "Carrasco",
            "INMEDIATA",
            None,
            "A estrenar",
            None,
            "Developer XYZ",
            "2%",
            0,
            "Calle Mar",
            None,
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        new_data = {
            "detail_url": "/proyecto/555?operation=Venta",
            "name": "Proyecto C",
            "zone": "Carrasco",
            "delivery_type": "INMEDIATA",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 99.000",
            "developer": "Developer XYZ",
            "commission": "2%",
            "has_ley_vp": False,
            "location": "Calle Mar",
            "image_url": "http://example.com/img2.png",
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert "price_from" in changes_dict
        assert changes_dict["price_from"]["old"] is None
        assert changes_dict["price_from"]["new"] == "USD 99.000"
        assert "image_url" in changes_dict
        assert changes_dict["image_url"]["old"] is None

    def test_compare_projects_value_to_null(self):
        """Test detection of change from value to NULL."""
        existing = (
            890,
            "/proyecto/890?operation=Venta",
            "Proyecto D",
            "Centro",
            "2026",
            "Torre A, Torre B",
            "En construcción",
            "USD 300.000",
            "Development Co",
            "4%",
            1,
            "Calle Principal",
            "http://example.com/old.png",
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        new_data = {
            "detail_url": "/proyecto/890?operation=Venta",
            "name": "Proyecto D",
            "zone": "Centro",
            "delivery_type": "2026",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 300.000",
            "developer": "Development Co",
            "commission": "4%",
            "has_ley_vp": True,
            "location": "Calle Principal",
            "image_url": None,
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert "delivery_torres" in changes_dict
        assert changes_dict["delivery_torres"]["old"] == "Torre A, Torre B"
        assert changes_dict["delivery_torres"]["new"] is None
        assert "image_url" in changes_dict
        assert changes_dict["image_url"]["old"] == "http://example.com/old.png"

    def test_compare_projects_boolean_conversion(self):
        """Test boolean field comparison with type conversion."""
        existing = (
            999,
            "/proyecto/999?operation=Venta",
            "Proyecto E",
            "Punta Carretas",
            "INMEDIATA",
            None,
            "A estrenar",
            "USD 500.000",
            "Prestige Dev",
            "5%",
            1,
            "Rambla",
            None,
            "2026-02-19 10:00:00",
            "2026-02-19 10:00:00",
        )

        # Test True to False change
        new_data = {
            "detail_url": "/proyecto/999?operation=Venta",
            "name": "Proyecto E",
            "zone": "Punta Carretas",
            "delivery_type": "INMEDIATA",
            "delivery_torres": None,
            "project_status": "A estrenar",
            "price_from": "USD 500.000",
            "developer": "Prestige Dev",
            "commission": "5%",
            "has_ley_vp": False,
            "location": "Rambla",
            "image_url": None,
        }

        has_changes, changes_dict = compare_project_data(existing, new_data)
        assert has_changes is True
        assert "has_ley_vp" in changes_dict


class TestFormatChangeMessage:
    """Tests for the format_change_message function."""

    def test_format_no_changes(self):
        """Test formatting when there are no changes."""
        message = format_change_message(235, {})
        assert "Proyecto 235" in message
        assert "Sin cambios" in message

    def test_format_single_change(self):
        """Test formatting with a single change."""
        changes = {
            "price_from": {"old": "USD 100.000", "new": "USD 150.000"}
        }
        message = format_change_message(235, changes)
        assert "Proyecto 235" in message
        assert "1 cambio(s) detectado(s)" in message
        assert "price_from" in message
        assert "USD 100.000" in message
        assert "USD 150.000" in message

    def test_format_multiple_changes(self):
        """Test formatting with multiple changes."""
        changes = {
            "name": {"old": "Old Name", "new": "New Name"},
            "delivery_type": {"old": "2026", "new": "INMEDIATA"},
            "price_from": {"old": "USD 100.000", "new": "USD 200.000"},
        }
        message = format_change_message(682, changes)
        assert "Proyecto 682" in message
        assert "3 cambio(s) detectado(s)" in message
        assert "name" in message
        assert "delivery_type" in message
        assert "price_from" in message


class TestExtractProjectId:
    """Tests for extract_project_id_from_url to verify ID extraction works."""

    def test_extract_id_from_path_only(self):
        """Test extraction from path-only URL."""
        url = "/proyecto/235"
        project_id = extract_project_id_from_url(url)
        assert project_id == 235

    def test_extract_id_from_full_url(self):
        """Test extraction from full URL with parameters."""
        url = "https://iris.infocasas.com.uy/proyecto/682?operation=Venta"
        project_id = extract_project_id_from_url(url)
        assert project_id == 682

    def test_extract_id_none_on_invalid(self):
        """Test that None is returned for invalid URLs."""
        assert extract_project_id_from_url(None) is None
        assert extract_project_id_from_url("") is None
        assert extract_project_id_from_url("/invalid/url") is None
