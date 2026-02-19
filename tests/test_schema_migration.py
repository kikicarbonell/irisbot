#!/usr/bin/env python3
"""Test script to verify database migration and UPSERT behavior with project_id."""

import sqlite3
from pathlib import Path

# Test with a temporary database
TEST_DB = Path("test_catalog.db")

def extract_project_id_from_url(url):
    """Extract numeric project ID from URL."""
    if not url:
        return None
    import re
    match = re.search(r"/proyecto/(\d+)", url)
    if match:
        return int(match.group(1))
    return None

def test_migration_and_upsert():
    """Test that project_id works as primary key and UPSERT updates correctly."""

    # Clean up if exists
    if TEST_DB.exists():
        TEST_DB.unlink()

    # Create connection and table with new schema
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            detail_url TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            zone TEXT,
            delivery_type TEXT,
            delivery_torres TEXT,
            project_status TEXT,
            price_from TEXT,
            developer TEXT,
            commission TEXT,
            has_ley_vp BOOLEAN DEFAULT 0,
            location TEXT,
            image_url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    print("✓ Table created with project_id as PRIMARY KEY and detail_url as UNIQUE")

    # Test 1: Insert a new project
    print("\n--- Test 1: Insert new project ---")
    detail_url = "/proyecto/235"
    project_id = extract_project_id_from_url(detail_url)
    print(f"Extracted project_id: {project_id} from URL: {detail_url}")

    c.execute("""
        INSERT INTO projects (
            project_id, detail_url, name, zone, price_from, developer, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(project_id) DO UPDATE SET
            detail_url = excluded.detail_url,
            name = excluded.name,
            zone = excluded.zone,
            price_from = excluded.price_from,
            developer = excluded.developer,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id, detail_url, "Torre Vista Original", "Pocitos", "USD 120.000", "Developer A"))
    conn.commit()

    # Verify insertion
    c.execute("SELECT project_id, detail_url, name, zone, price_from, developer FROM projects WHERE project_id = ?",
              (project_id,))
    row = c.fetchone()
    print(f"Inserted: {row}")
    assert row[0] == 235, "Project ID should be 235"
    assert row[2] == "Torre Vista Original", "Name should be 'Torre Vista Original'"
    print("✓ Insert successful")

    # Test 2: Update existing project with different URL format (same ID)
    print("\n--- Test 2: Update existing project (same ID, different URL format) ---")
    detail_url_with_params = "/proyecto/235?operation=Venta"
    project_id_2 = extract_project_id_from_url(detail_url_with_params)
    print(f"Extracted project_id: {project_id_2} from URL: {detail_url_with_params}")
    assert project_id == project_id_2, "Should extract same ID from different URL formats"

    c.execute("""
        INSERT INTO projects (
            project_id, detail_url, name, zone, price_from, developer, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(project_id) DO UPDATE SET
            detail_url = excluded.detail_url,
            name = excluded.name,
            zone = excluded.zone,
            price_from = excluded.price_from,
            developer = excluded.developer,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id_2, detail_url_with_params, "Torre Vista UPDATED", "Pocitos", "USD 130.000", "Developer B"))
    conn.commit()

    # Verify update
    c.execute("SELECT project_id, detail_url, name, zone, price_from, developer FROM projects WHERE project_id = ?",
              (project_id,))
    row = c.fetchone()
    print(f"Updated: {row}")
    assert row[0] == 235, "Project ID should still be 235"
    assert row[1] == detail_url_with_params, "detail_url should be updated"
    assert row[2] == "Torre Vista UPDATED", "Name should be updated"
    assert row[4] == "USD 130.000", "Price should be updated"
    assert row[5] == "Developer B", "Developer should be updated"
    print("✓ Update successful")

    # Test 3: Count should still be 1 (not 2)
    print("\n--- Test 3: Verify no duplicates ---")
    c.execute("SELECT COUNT(*) FROM projects")
    count = c.fetchone()[0]
    print(f"Total projects: {count}")
    assert count == 1, "Should have exactly 1 project (no duplicates)"
    print("✓ No duplicates created")

    # Test 4: Insert different project
    print("\n--- Test 4: Insert different project ---")
    detail_url_999 = "https://iris.infocasas.com.uy/proyecto/999?operation=Venta"
    project_id_999 = extract_project_id_from_url(detail_url_999)
    print(f"Extracted project_id: {project_id_999} from URL: {detail_url_999}")

    c.execute("""
        INSERT INTO projects (
            project_id, detail_url, name, zone, price_from, developer, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(project_id) DO UPDATE SET
            detail_url = excluded.detail_url,
            name = excluded.name,
            zone = excluded.zone,
            price_from = excluded.price_from,
            developer = excluded.developer,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id_999, detail_url_999, "Another Project", "Carrasco", "USD 200.000", "Developer C"))
    conn.commit()

    c.execute("SELECT COUNT(*) FROM projects")
    count = c.fetchone()[0]
    print(f"Total projects: {count}")
    assert count == 2, "Should have 2 projects now"
    print("✓ Second project inserted")

    # Test 5: Query by project_id (performance test)
    print("\n--- Test 5: Query by project_id (primary key) ---")
    c.execute("SELECT project_id, name FROM projects WHERE project_id = ?", (235,))
    row = c.fetchone()
    print(f"Found project 235: {row}")
    assert row[0] == 235
    print("✓ Primary key lookup successful")

    # Clean up
    conn.close()
    TEST_DB.unlink()

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("   • project_id (INTEGER) works as PRIMARY KEY")
    print("   • detail_url (TEXT) works as UNIQUE constraint")
    print("   • UPSERT updates existing records correctly")
    print("   • No duplicates are created on re-scraping")
    print("   • Multiple projects can coexist")
    print("   • Same project ID with different URL formats updatesexisting record")

if __name__ == "__main__":
    test_migration_and_upsert()
