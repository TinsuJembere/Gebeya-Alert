# Fix Missing Database Columns

## Problem
Your PostgreSQL database is missing the `source` and `confidence_score` columns in the `prices` table.

## Quick Fix Options

### Option 1: Run SQL Script Directly (Fastest)

1. Connect to your PostgreSQL database:
   ```bash
   psql -U your_username -d your_database_name
   ```

2. Run the SQL script:
   ```sql
   \i scripts/add_price_columns.sql
   ```
   
   Or copy-paste the contents of `scripts/add_price_columns.sql` into your psql session.

### Option 2: Use Python Script (Recommended)

Make sure your virtual environment is activated, then:

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Run the script
python scripts/add_price_columns.py
```

### Option 3: Use Alembic Migration

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows

# Run the migration
alembic upgrade head
```

If the migration file doesn't exist yet, create it:
```bash
alembic revision --autogenerate -m "add source and confidence_score to prices"
alembic upgrade head
```

### Option 4: Manual SQL (If you have database access)

Run these SQL commands directly:

```sql
-- Add source column
ALTER TABLE prices ADD COLUMN source VARCHAR(50) DEFAULT 'manual';

-- Add confidence_score column  
ALTER TABLE prices ADD COLUMN confidence_score NUMERIC(3, 2) DEFAULT 1.0;

-- Update existing rows
UPDATE prices SET source = 'manual' WHERE source IS NULL;
UPDATE prices SET confidence_score = 1.0 WHERE confidence_score IS NULL;
```

## Verify Columns Were Added

Check that columns exist:
```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'prices' 
ORDER BY ordinal_position;
```

You should see:
- `source` (VARCHAR)
- `confidence_score` (NUMERIC)

## After Fixing

1. Restart your backend server
2. The error should be resolved
3. Frontend should now connect successfully

## Switch to SQLite for Development (Alternative)

If you want to use SQLite instead of PostgreSQL for local development:

1. Update `.env`:
   ```env
   DATABASE_URL=sqlite:///./gebeyaalert.db
   ENVIRONMENT=development
   ```

2. Delete the old database file if it exists

3. Restart server - it will create a new SQLite database automatically
