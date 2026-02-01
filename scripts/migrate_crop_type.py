"""
Migration script to add crop_type column to existing crops table.
This script checks the database type and adds the column appropriately.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlmodel import Session, text
from database import engine
from config import settings


def migrate_crop_type():
    """Add crop_type column to crops table if it doesn't exist."""
    print("Checking if crop_type column migration is needed...")
    
    db_url = settings.DATABASE_URL.lower()
    
    try:
        with Session(engine) as db:
            # Try to query crop_type to see if column exists
            try:
                test_query = text("SELECT crop_type FROM crops LIMIT 1")
                db.exec(test_query).first()
                print("✓ crop_type column already exists")
                return
            except Exception:
                # Column doesn't exist, try to add it
                pass
            
            if 'sqlite' in db_url:
                # SQLite - add column
                try:
                    # SQLite doesn't support ALTER TABLE ADD COLUMN with NOT NULL default
                    # So we add it as nullable first, then update existing rows
                    db.exec(text("ALTER TABLE crops ADD COLUMN crop_type VARCHAR(50)"))
                    db.exec(text("UPDATE crops SET crop_type = 'Grain' WHERE crop_type IS NULL"))
                    db.commit()
                    print("✓ crop_type column added to SQLite database")
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'duplicate column name' in error_msg or 'already exists' in error_msg:
                        print("✓ crop_type column already exists")
                    else:
                        print(f"⚠ Warning: Could not add crop_type column to SQLite: {e}")
                        db.rollback()
                        
            elif 'postgresql' in db_url or 'postgres' in db_url:
                # PostgreSQL
                try:
                    add_column = text("""
                        ALTER TABLE crops 
                        ADD COLUMN IF NOT EXISTS crop_type VARCHAR(50) NOT NULL DEFAULT 'Grain'
                    """)
                    db.exec(add_column)
                    db.commit()
                    print("✓ crop_type column added to PostgreSQL database")
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'duplicate' in error_msg:
                        print("✓ crop_type column already exists")
                    else:
                        print(f"⚠ Warning: Could not add crop_type column to PostgreSQL: {e}")
                        db.rollback()
            else:
                # MySQL or other
                try:
                    check_column = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='crops' AND column_name='crop_type'
                    """)
                    result = db.exec(check_column).first()
                    
                    if result:
                        print("✓ crop_type column already exists")
                        return
                    
                    # Add column with default value
                    add_column = text("""
                        ALTER TABLE crops 
                        ADD COLUMN crop_type VARCHAR(50) NOT NULL DEFAULT 'Grain'
                    """)
                    db.exec(add_column)
                    db.commit()
                    print("✓ crop_type column added successfully")
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'duplicate' in error_msg:
                        print("✓ crop_type column already exists")
                    else:
                        print(f"⚠ Warning: Could not add crop_type column: {e}")
                        db.rollback()
                
    except Exception as e:
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            print("✓ crop_type column already exists")
        else:
            print(f"⚠ Warning: Could not migrate crop_type column: {e}")
            print("The app will still work, but crop_type will default to 'Grain'")
            print("You may need to manually add the column or recreate the database")


if __name__ == "__main__":
    migrate_crop_type()

