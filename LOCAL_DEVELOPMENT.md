# Local Development Guide

This guide explains how to run GebeyaAlert locally with SQLite (zero database setup required).

## Quick Start

### Backend (FastAPI + SQLite)

1. **Install dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   copy env.example .env  # Windows
   # cp env.example .env  # Linux/Mac
   ```
   
   The `.env` file is already configured for SQLite. **No changes needed!**

3. **Run the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```

   The database (`gebeyaalert.db`) will be **automatically created** in the project root on first run.

4. **Verify it's working:**
   - API: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - Health Check: http://localhost:8080/health

### Frontend (Next.js)

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   copy env.example .env.local  # Windows
   # cp env.example .env.local  # Linux/Mac
   ```
   
   The `.env.local` file is already configured to connect to `http://localhost:8080`.

4. **Run the frontend:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   - Frontend: http://localhost:3000

## How It Works

### Database Configuration

- **Development**: Uses SQLite (default, no setup needed)
  - Database file: `gebeyaalert.db` (auto-created)
  - Location: Project root directory
  - No installation required - SQLite comes with Python

- **Production**: Uses PostgreSQL (optional)
  - Set `ENVIRONMENT=production` and `DATABASE_URL_PROD=...`
  - Or set `DATABASE_URL=postgresql://...` directly

### Frontend-Backend Connection

The frontend automatically connects to the backend using:
- Environment variable: `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8080`)
- All API calls use this variable (no hardcoded URLs)

### AI Features with SQLite

All AI prediction features work perfectly with SQLite:
- ✅ Price predictions (moving averages, regression)
- ✅ Best time to sell recommendations
- ✅ Historical price analysis
- ✅ Trend calculations

SQLModel queries are database-agnostic, so everything works the same with SQLite and PostgreSQL.

## Troubleshooting

### Database Issues

**Problem**: Database file not created
- **Solution**: Make sure you have write permissions in the project directory
- The database is created automatically on first server start

**Problem**: Migration errors
- **Solution**: SQLite migrations work the same as PostgreSQL. If you see errors, try:
  ```bash
  alembic upgrade head
  ```

### Connection Issues

**Problem**: Frontend can't connect to backend
- **Solution**: 
  1. Make sure backend is running on port 8080
  2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
  3. Check browser console for CORS errors

**Problem**: CORS errors
- **Solution**: Backend is configured to allow `http://localhost:3000` by default. Check `FRONTEND_URL` in backend `.env`

### Port Conflicts

**Problem**: Port 8080 already in use
- **Solution**: Change port in `.env`:
  ```env
  PORT=8081
  ```
  Then update frontend `.env.local`:
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8081
  ```

## Switching to PostgreSQL (Production)

When ready to deploy:

1. **Set environment variables:**
   ```env
   ENVIRONMENT=production
   DATABASE_URL_PROD=postgresql://user:password@host:5432/dbname
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Restart server** - it will automatically use PostgreSQL

The code automatically detects SQLite vs PostgreSQL and configures connection pooling accordingly.

## Development Tips

- **Database file location**: `gebeyaalert.db` in project root
- **Reset database**: Delete `gebeyaalert.db` and restart server
- **View database**: Use SQLite browser tools or `sqlite3 gebeyaalert.db` in terminal
- **Hot reload**: Backend uses `--reload` flag, changes auto-reload
- **API testing**: Use http://localhost:8080/docs for interactive API testing
