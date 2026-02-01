"""
Reset database script for development.
Deletes and recreates the SQLite database with current schema.
WARNING: This will delete all data!
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings
from database import init_db, engine

def reset_database():
    """Reset the database by deleting and recreating it."""
    database_url = settings.get_database_url()
    
    if not database_url.startswith("sqlite"):
        print("⚠️  WARNING: This script only works with SQLite!")
        print(f"   Current database: {database_url}")
        response = input("   Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("   Cancelled.")
            return
    
    # Extract database file path
    if database_url.startswith("sqlite:///"):
        db_file = database_url.replace("sqlite:///", "")
    else:
        db_file = database_url.replace("sqlite://", "")
    
    # Check if database file exists
    if os.path.exists(db_file):
        print(f"📁 Found database file: {db_file}")
        response = input("🗑️  Delete and recreate? (yes/no): ")
        if response.lower() != "yes":
            print("   Cancelled.")
            return
        
        try:
            os.remove(db_file)
            print(f"✅ Deleted: {db_file}")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            return
    else:
        print(f"📁 Database file not found: {db_file}")
        print("   Will create new database.")
    
    # Recreate database
    try:
        print("🔄 Creating new database with current schema...")
        init_db()
        print("✅ Database created successfully!")
        print(f"   Location: {os.path.abspath(db_file)}")
        print("\n💡 Next steps:")
        print("   1. Run: python scripts/seed_data.py (to add sample data)")
        print("   2. Run: python scripts/create_admin.py (to create admin user)")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Reset Script")
    print("=" * 60)
    print()
    reset_database()
