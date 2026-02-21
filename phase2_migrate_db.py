#!/usr/bin/env python3
"""
Phase 2 Database Schema Extension

Adds tables and columns needed for project detail scraping:
- units table: apartment/unit information
- developer_assets table: downloadable files
- projects table extensions: additional metadata
"""

import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("catalog_projects.db")


def migrate_to_phase2(db_path: Path = DB_PATH) -> bool:
    """Run Phase 2 migration on the database."""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        print("🔧 Starting Phase 2 Database Migration\n")

        # 1. Extend projects table with Phase 2 fields
        print("1️⃣  Extending projects table...")

        # Get existing columns
        c.execute("PRAGMA table_info(projects)")
        existing_columns = {row[1] for row in c.fetchall()}

        extensions = [
            ("description", "TEXT"),
            ("amenities", "TEXT"),  # JSON array of amenities
            ("delivery_date", "TEXT"),  # "Inmediata", "2025-Q2", etc
            ("developer_email", "TEXT"),
            ("developer_phone", "TEXT"),
            ("phase2_scraped_at", "TIMESTAMP"),
            ("phase2_updated_at", "TIMESTAMP"),
        ]

        for column, col_type in extensions:
            if column in existing_columns:
                print(f"  • Column already exists: {column}")
            else:
                try:
                    c.execute(f"ALTER TABLE projects ADD COLUMN {column} {col_type}")
                    print(f"  ✓ Added column: {column}")
                except sqlite3.OperationalError as e:
                    print(f"  ✗ Error adding {column}: {e}")

        # 2. Create units table
        print("\n2️⃣  Creating units table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id TEXT PRIMARY KEY,
                project_id INTEGER NOT NULL,
                typology TEXT NOT NULL,
                internal_sqm REAL,
                external_sqm REAL,
                total_sqm REAL,
                price_from INTEGER,
                price_to INTEGER,
                currency TEXT DEFAULT 'USD',
                rent_available BOOLEAN DEFAULT 0,
                rent_price INTEGER,
                has_360_view BOOLEAN DEFAULT 0,
                status TEXT,
                floor INTEGER,
                orientation TEXT,
                features TEXT,
                raw_data TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
        """)
        print("  ✓ Created units table")

        # Create index on project_id for faster queries
        try:
            c.execute("CREATE INDEX IF NOT EXISTS idx_units_project_id ON units(project_id)")
            print("  ✓ Created index on units.project_id")
        except:
            pass

        # 3. Create developer_assets table
        print("\n3️⃣  Creating developer_assets table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS developer_assets (
                id TEXT PRIMARY KEY,
                project_id INTEGER NOT NULL,
                asset_type TEXT NOT NULL,
                asset_name TEXT,
                file_url TEXT NOT NULL,
                local_path TEXT,
                file_size_bytes INTEGER,
                file_type TEXT,
                download_status TEXT DEFAULT 'pending',
                download_attempts INTEGER DEFAULT 0,
                error_message TEXT,
                downloaded_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
        """)
        print("  ✓ Created developer_assets table")

        # Create index
        try:
            c.execute("CREATE INDEX IF NOT EXISTS idx_assets_project_id ON developer_assets(project_id)")
            print("  ✓ Created index on developer_assets.project_id")
        except:
            pass

        # 4. Create developer_info table
        print("\n4️⃣  Creating developer_info table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS developer_info (
                id INTEGER PRIMARY KEY,
                project_id INTEGER UNIQUE NOT NULL,
                company_name TEXT,
                company_email TEXT,
                company_phone TEXT,
                company_website TEXT,
                logo_url TEXT,
                description TEXT,
                raw_data TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
        """)
        print("  ✓ Created developer_info table")

        # 5. Create scrapage_log table for audit trail
        print("\n5️⃣  Creating scrapage_log table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS scrapage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                phase TEXT,
                status TEXT,
                message TEXT,
                error TEXT,
                items_scraped INTEGER,
                duration_seconds REAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
        """)
        print("  ✓ Created scrapage_log table")

        # Commit changes
        conn.commit()
        conn.close()

        print("\n✅ Phase 2 Migration Complete!")
        print("\n📊 New tables created:")
        print("  • units (units/apartments in each project)")
        print("  • developer_assets (downloadable files)")
        print("  • developer_info (developer/company information)")
        print("  • scrapage_log (audit trail)")
        print("\n📝 Projects table extended with:")
        print("  • description, amenities, delivery_date")
        print("  • developer_email, developer_phone")
        print("  • phase2_scraped_at, phase2_updated_at")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_schema() -> Optional[dict]:
    """Verify the schema is correctly set up."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        schema_info = {}

        # Check tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        schema_info["tables"] = tables

        # Check columns in projects
        c.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in c.fetchall()]
        schema_info["projects_columns"] = sorted(columns)

        # Count rows in each table
        for table in ["projects", "units", "developer_assets", "developer_info"]:
            if table in tables:
                c.execute(f"SELECT COUNT(*) FROM {table}")
                count = c.fetchone()[0]
                schema_info[f"{table}_count"] = count

        conn.close()
        return schema_info

    except Exception as e:
        print(f"Error verifying schema: {e}")
        return None


def print_schema_info():
    """Print schema verification."""
    print("\n🔍 Database Schema Verification\n")
    print("=" * 80)

    info = verify_schema()
    if not info:
        print("Could not verify schema")
        return

    print(f"\n📋 Tables ({len(info.get('tables', []))} total):")
    for table in info.get('tables', []):
        count = info.get(f'{table}_count', 0)
        print(f"  • {table:<25} ({count:,} rows)")

    print(f"\n📌 Projects columns ({len(info.get('projects_columns', []))} total):")
    cols = info.get('projects_columns', [])
    for col in sorted(cols):
        print(f"  • {col}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    import os

    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run Phase 1 scraper first: python src/scrape_catalog_phase1.py")
        exit(1)

    # Run migration
    success = migrate_to_phase2()

    if success:
        print_schema_info()
    else:
        exit(1)
