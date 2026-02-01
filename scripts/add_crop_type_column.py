"""
Script to add crop_type column to existing crops table.
Run this once to migrate existing database.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlmodel import Session, text
from database import engine


def add_crop_type_column():
    """Add crop_type column to crops table if it doesn't exist."""
    print("Adding crop_type column to crops table...")
    
    try:
        with Session(engine) as db:
            # Check if column exists (PostgreSQL syntax)
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
        print(f"✗ Error adding crop_type column: {e}")
        print("Note: If you're using SQLite, the column might need to be added differently")
        print("Or if the column already exists, you can ignore this error")
        raise


if __name__ == "__main__":
    add_crop_type_column()

