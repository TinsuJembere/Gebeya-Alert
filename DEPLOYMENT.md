# Deployment Guide

This guide covers deploying the GebeyaAlert FastAPI backend with PostgreSQL support.

## Prerequisites

- PostgreSQL database (free tier available on Render, Supabase, Railway, etc.)
- Python 3.8+ environment
- Environment variables configured

## Database Configuration

The application supports both SQLite (local development) and PostgreSQL (production).

### Local Development (SQLite)

For local development, **no configuration needed**! The app defaults to SQLite:
- Database file: `./gebeyaalert.db` (created automatically)
- No setup required

### Production (PostgreSQL)

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

**Example formats:**
- Render: `postgresql://user:pass@dpg-xxxxx-a.oregon-postgres.render.com/gebeyaalert`
- Supabase: `postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres`
- Railway: `postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

## Environment Variables

### Required for Production

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=<generate-a-strong-random-key>
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"

# Application
ENVIRONMENT=production
DEBUG=False
FRONTEND_URL=https://your-frontend-domain.com
```

### Optional

```bash
# SMS Configuration (if using Twilio)
SMS_PROVIDER=twilio
SMS_ENABLED=True
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Celery/Redis (for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Server Port (usually set by hosting platform)
PORT=8080
```

## Deployment Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `psycopg2-binary` for PostgreSQL support.

### 2. Set Environment Variables

Create a `.env` file or set environment variables in your hosting platform:

```bash
# Copy example file
cp env.example .env

# Edit .env with your PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=False
```

### 3. Initialize Database

The application automatically creates tables on startup via `init_db()` in `main.py`.

**First-time setup:**
1. Start the application - tables will be created automatically
2. Seed initial data (crops and markets):
   ```bash
   python scripts/seed_data.py
   ```
3. Create an admin user:
   ```bash
   python scripts/create_admin.py +1234567890 yourpassword
   ```

### 4. Run the Application

**Local testing with PostgreSQL:**
```bash
# Set DATABASE_URL environment variable
export DATABASE_URL=postgresql://user:password@host:port/database

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Production (using gunicorn recommended):**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Platform-Specific Deployment

### Render

1. **Create a PostgreSQL Database:**
   - Go to Render Dashboard → New → PostgreSQL
   - Copy the Internal Database URL

2. **Deploy Web Service:**
   - New → Web Service
   - Connect your repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     - `DATABASE_URL` (from PostgreSQL service)
     - `SECRET_KEY` (generate a random key)
     - `ENVIRONMENT=production`
     - `DEBUG=False`
     - `FRONTEND_URL` (your frontend URL)

3. **Initialize Database:**
   After first deployment, run:
   ```bash
   # Via Render Shell or locally with DATABASE_URL set
   python scripts/seed_data.py
   python scripts/create_admin.py +1234567890 adminpassword
   ```

### Supabase

1. **Get Connection String:**
   - Go to Supabase Dashboard → Project Settings → Database
   - Copy the Connection String (URI format)

2. **Set Environment Variables:**
   ```bash
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

3. **Deploy:**
   - Use Supabase Functions or deploy to another platform (Render, Railway, etc.)
   - Set all required environment variables

### Railway

1. **Add PostgreSQL:**
   - Railway Dashboard → New → Database → Add PostgreSQL
   - Railway automatically provides `DATABASE_URL`

2. **Deploy:**
   - New → GitHub Repo → Select your repo
   - Railway auto-detects Python and installs dependencies
   - Add environment variables:
     - `SECRET_KEY`
     - `ENVIRONMENT=production`
     - `DEBUG=False`
     - `FRONTEND_URL`

3. **Initialize Database:**
   ```bash
   railway run python scripts/seed_data.py
   railway run python scripts/create_admin.py +1234567890 adminpassword
   ```

## Database Initialization

The app automatically creates tables on startup. However, you may want to:

1. **Seed initial data** (crops and markets):
   ```bash
   python scripts/seed_data.py
   ```

2. **Create admin user**:
   ```bash
   python scripts/create_admin.py <phone_number> [password]
   # Example: python scripts/create_admin.py +1234567890 admin123
   ```

## Troubleshooting

### Database Connection Issues

**Error: "could not connect to server"**
- Verify `DATABASE_URL` is correct
- Check if database allows connections from your IP (some services require IP whitelisting)
- Ensure database is running and accessible

**Error: "relation does not exist"**
- Tables may not be created yet
- Restart the application (tables are created on startup)
- Or manually run: `python -c "from database import init_db; init_db()"`

**Error: "psycopg2 not found"**
- Install dependencies: `pip install -r requirements.txt`
- Verify `psycopg2-binary` is in `requirements.txt`

### Environment Variables

**App still using SQLite in production:**
- Ensure `DATABASE_URL` is set correctly
- Check environment variables are loaded (some platforms require restart)
- Verify `.env` file is in the correct location

**Secret key warnings:**
- Generate a strong secret key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Set `SECRET_KEY` environment variable
- Never commit secrets to version control

## Testing Database Connection

Test your PostgreSQL connection:

```bash
# Set DATABASE_URL
export DATABASE_URL=postgresql://user:password@host:port/database

# Test connection
python -c "from database import engine; from sqlmodel import text; with engine.connect() as conn: print('Connected!')"
```

Or use the API endpoint:
```bash
curl http://your-api-url/api/v1/test/db
```

## Migration Notes

### From SQLite to PostgreSQL

If migrating existing SQLite data to PostgreSQL:

1. Export data from SQLite (if needed)
2. Set `DATABASE_URL` to PostgreSQL connection string
3. Restart application (tables will be created)
4. Re-seed data: `python scripts/seed_data.py`
5. Re-create admin users: `python scripts/create_admin.py ...`

**Note:** SQLModel's `create_all()` will create tables automatically. For schema migrations, consider using Alembic (already configured in this project).

## Security Checklist

- [ ] `SECRET_KEY` is set to a strong random value
- [ ] `DEBUG=False` in production
- [ ] `ENVIRONMENT=production` in production
- [ ] Database credentials are secure (use environment variables, not hardcoded)
- [ ] `DATABASE_URL` is not committed to version control
- [ ] CORS is configured correctly (`FRONTEND_URL` set)
- [ ] Admin users have strong passwords

## Support

For issues or questions:
- Check application logs
- Verify environment variables
- Test database connection
- Review platform-specific documentation
