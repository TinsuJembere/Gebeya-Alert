# PostgreSQL Migration Summary

This document summarizes the changes made to migrate from SQLite-only to PostgreSQL support with SQLite fallback for local development.

## Changes Made

### 1. Database Configuration (`config.py`)

**Before:**
- Used `DATABASE_URL` with SQLite default
- Had separate `DATABASE_URL_PROD` for production
- Required `ENVIRONMENT=production` to use PostgreSQL

**After:**
- `DATABASE_URL` is now optional (defaults to `None`)
- If `DATABASE_URL` is set, it's used (PostgreSQL or any other database)
- If `DATABASE_URL` is not set, defaults to SQLite for local development
- Removed `DATABASE_URL_PROD` (simplified configuration)

**Key Changes:**
```python
# Old approach
DATABASE_URL: str = "sqlite:///./gebeyaalert.db"
DATABASE_URL_PROD: Optional[str] = None

# New approach
DATABASE_URL: Optional[str] = None  # Set via environment variable
# Defaults to SQLite if not set
```

### 2. Database Engine (`database.py`)

**Improvements:**
- Automatically detects PostgreSQL connection strings (`postgresql://` or `postgres://`)
- Converts connection strings to use explicit driver: `postgresql+psycopg2://`
- Configures connection pooling for PostgreSQL:
  - `pool_pre_ping=True` - Verifies connections before use
  - `pool_size=10` - Base connection pool size
  - `max_overflow=20` - Maximum overflow connections
  - `pool_recycle=3600` - Recycle connections after 1 hour
- Maintains SQLite compatibility for local development

### 3. Dependencies (`requirements.txt`)

**Added:**
- `psycopg2-binary==2.9.9` - PostgreSQL adapter (widely compatible)
- Commented out `psycopg[binary]` (psycopg3) as alternative

**Note:** `psycopg2-binary` is more widely compatible with deployment platforms.

### 4. Environment Configuration (`env.example`)

**Updated:**
- Clear instructions for SQLite (local) vs PostgreSQL (production)
- Examples of PostgreSQL connection string formats
- Notes about platform-specific `DATABASE_URL` formats

### 5. Documentation

**Created:**
- `DEPLOYMENT.md` - Comprehensive deployment guide with:
  - Platform-specific instructions (Render, Supabase, Railway)
  - Environment variable setup
  - Database initialization steps
  - Troubleshooting guide

**Updated:**
- `README.md` - Removed references to `DATABASE_URL_PROD`
- Clarified PostgreSQL setup process

## Usage

### Local Development (SQLite)

**No configuration needed!** Just run:
```bash
uvicorn main:app --reload
```

The app will automatically use SQLite (`./gebeyaalert.db`).

### Production (PostgreSQL)

**Set environment variable:**
```bash
export DATABASE_URL=postgresql://user:password@host:port/database
```

Or in `.env` file:
```env
DATABASE_URL=postgresql://user:password@host:port/database
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secret-key-here
```

The app will:
1. Detect PostgreSQL from `DATABASE_URL`
2. Create tables automatically on startup (`init_db()`)
3. Use connection pooling for better performance

## Database Initialization

Tables are created automatically on startup via `init_db()` in `main.py`.

**After first deployment, initialize data:**
```bash
# Seed crops and markets
python scripts/seed_data.py

# Create admin user
python scripts/create_admin.py +1234567890 yourpassword
```

## Testing

**Test PostgreSQL connection locally:**
```bash
# Set DATABASE_URL
export DATABASE_URL=postgresql://user:password@host:port/database

# Run server
uvicorn main:app --reload

# Test connection
curl http://localhost:8080/api/v1/test/db
```

## Key Benefits

1. **Simplified Configuration** - Single `DATABASE_URL` environment variable
2. **Automatic Detection** - App detects database type from connection string
3. **Local Development** - No setup needed (SQLite default)
4. **Production Ready** - PostgreSQL with connection pooling
5. **Platform Compatible** - Works with Render, Supabase, Railway, etc.

## Migration Notes

If you have existing SQLite data:
1. Export data if needed (optional)
2. Set `DATABASE_URL` to PostgreSQL
3. Restart application (tables created automatically)
4. Re-seed data: `python scripts/seed_data.py`
5. Re-create admin users: `python scripts/create_admin.py ...`

## Files Modified

- ✅ `config.py` - Updated database URL handling
- ✅ `database.py` - Added PostgreSQL detection and connection pooling
- ✅ `requirements.txt` - Added `psycopg2-binary`
- ✅ `env.example` - Updated with PostgreSQL instructions
- ✅ `README.md` - Updated deployment instructions
- ✅ `DEPLOYMENT.md` - Created comprehensive deployment guide

## Next Steps

1. **Set up PostgreSQL database** on your preferred platform (Render, Supabase, etc.)
2. **Get connection string** from your database provider
3. **Set `DATABASE_URL`** environment variable
4. **Deploy application** - tables will be created automatically
5. **Initialize data** using seed scripts
6. **Create admin user** for access

For detailed deployment instructions, see `DEPLOYMENT.md`.
