# Quick Start Guide

Get GebeyaAlert running locally in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Git (optional)

## Step 1: Backend Setup (2 minutes)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Windows:
copy env.example .env
# Linux/Mac:
cp env.example .env

# 5. Edit .env and set SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")

# 6. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

✅ Backend running at: http://localhost:8080
✅ API docs at: http://localhost:8080/docs

## Step 2: Frontend Setup (2 minutes)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Set up environment variables
# Windows:
copy env.example .env.local
# Linux/Mac:
cp env.example .env.local

# 4. Run the frontend
npm run dev
```

✅ Frontend running at: http://localhost:3000

## Step 3: Create Admin User (1 minute)

Open a new terminal and run:

```bash
# Make sure you're in the project root and venv is activated
python scripts/create_admin.py
```

Follow the prompts to create an admin account.

## Done! 🎉

- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

## Next Steps

1. Sign up as a regular user at http://localhost:3000/signup
2. Log in with your credentials
3. Explore the dashboard
4. Set up price alerts
5. Check out the admin dashboard (if you're an admin)

## Troubleshooting

**Backend won't start?**
- Check that port 8080 is not in use
- Verify `.env` file exists and has `SECRET_KEY` and `DATABASE_URL`

**Frontend won't start?**
- Check that port 3000 is not in use
- Verify `.env.local` exists with `NEXT_PUBLIC_API_URL=http://localhost:8080`

**Can't connect to backend?**
- Make sure backend is running first
- Check `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL

For more details, see [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md).

