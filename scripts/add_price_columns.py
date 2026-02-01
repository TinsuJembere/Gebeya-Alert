"""
Add missing columns to prices table.
This script adds 'source' and 'confidence_score' columns if they don't exist.
Works with both PostgreSQL and SQLite.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings
from database import engine
from sqlalchemy import text, inspect

def add_missing_columns():
    """Add source and confidence_score columns to prices table if they don't exist."""
    database_url = settings.get_database_url()
    is_sqlite = database_url.startswith("sqlite")
    
    print("=" * 60)
    print("Adding Missing Columns to Prices Table")
    print("=" * 60)
    print(f"Database: {'SQLite' if is_sqlite else 'PostgreSQL'}")
    print()
    
    # Check which columns exist
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('prices')]
    
    print(f"Existing columns: {', '.join(columns)}")
    print()
    
    with engine.connect() as conn:
        # Add source column if it doesn't exist
        if 'source' not in columns:
            print("➕ Adding 'source' column...")
            if is_sqlite:
                conn.execute(text("""
                    ALTER TABLE prices 
                    ADD COLUMN source VARCHAR(50) DEFAULT 'manual'
                """))
            else:
                conn.execute(text("""
                    ALTER TABLE prices 
                    ADD COLUMN source VARCHAR(50) DEFAULT 'manual'
                """))
            conn.commit()
            print("   ✅ Added 'source' column")
        else:
            print("   ✓ 'source' column already exists")
        
        # Add confidence_score column if it doesn't exist
        if 'confidence_score' not in columns:
            print("➕ Adding 'confidence_score' column...")
            if is_sqlite:
                conn.execute(text("""
                    ALTER TABLE prices 
                    ADD COLUMN confidence_score NUMERIC(3, 2) DEFAULT 1.0
                """))
            else:
                conn.execute(text("""
                    ALTER TABLE prices 
                    ADD COLUMN confidence_score NUMERIC(3, 2) DEFAULT 1.0
                """))
            conn.commit()
            print("   ✅ Added 'confidence_score' column")
        else:
            print("   ✓ 'confidence_score' column already exists")
        
        # Update existing rows to have default values
        print()
        print("🔄 Updating existing rows with default values...")
        if is_sqlite:
            conn.execute(text("""
                UPDATE prices 
                SET source = 'manual' 
                WHERE source IS NULL
            """))
            conn.execute(text("""
                UPDATE prices 
                SET confidence_score = 1.0 
                WHERE confidence_score IS NULL
            """))
        else:
            conn.execute(text("""
                UPDATE prices 
                SET source = 'manual' 
                WHERE source IS NULL
            """))
            conn.execute(text("""
                UPDATE prices 
                SET confidence_score = 1.0 
                WHERE confidence_score IS NULL
            """))
        conn.commit()
        print("   ✅ Updated existing rows")
    
    print()
    print("=" * 60)
    print("✅ Done! Columns added successfully.")
    print("=" * 60)
    print()
    print("💡 You can now restart your backend server.")

if __name__ == "__main__":
    try:
        add_missing_columns()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
