# GebeyaAlert - Agricultural Price Alert System for African Farmers
watch live on: https://gebeya-alert-gg73.vercel.app
A production-ready, mobile-first platform designed to empower African farmers with real-time market intelligence and AI-powered selling recommendations. Built for low-bandwidth environments with offline support.

## Problem Statement

Smallholder farmers across Africa face significant challenges in accessing timely and accurate market price information. Without this data, farmers often:
- Sell crops at suboptimal prices, reducing their income
- Miss opportunities to maximize profits during price peaks
- Lack confidence in pricing decisions
- Struggle with limited internet connectivity in rural areas

**GebeyaAlert** addresses these challenges by providing:
- Real-time price tracking across multiple markets
- AI-powered price predictions and selling recommendations
- Offline-first design for unreliable connectivity
- SMS notifications for farmers without smartphones
- Simple, intuitive interface optimized for mobile devices

## AI Features

This platform uses practical AI/ML techniques to help farmers make better selling decisions:

### 1. **Price Prediction Service**
- Uses **moving averages** (7-day, 14-day, 30-day) to smooth price trends
- Implements **simple linear regression** to forecast future prices
- Calculates confidence scores based on data quality and volatility
- Provides 7-day ahead price predictions with trend indicators

### 2. **Best Time to Sell Recommendations**
- Analyzes historical price patterns to identify optimal selling windows
- Compares current prices to historical highs and lows
- Considers short-term and long-term trends
- Generates human-readable, actionable advice in local languages

### 3. **Confidence Scoring**
- Tracks data source reliability (manual entry, API, SMS, market officers)
- Adjusts confidence based on data completeness and volatility
- Helps farmers understand prediction reliability

**Note**: These are lightweight, interpretable models designed for real-world constraints. No complex deep learning - just practical statistical methods that work reliably with limited data.

## Features

- 🔐 **User Authentication**: JWT-based authentication with phone number registration
- 📊 **Real-time Price Tracking**: View current market prices for various crops with source tracking
- 🤖 **AI Price Predictions**: 7-day price forecasts using moving averages and regression
- 💡 **Selling Recommendations**: AI-powered "best time to sell" advice
- 🔔 **Price Alerts**: Set custom price alerts and receive SMS notifications
- 📈 **Price History**: View historical price trends with interactive charts
- 🌍 **Multi-language Support**: English and Amharic interface (extensible)
- 👨‍💼 **Admin Dashboard**: Manage crops, markets, prices, and users
- 📱 **Mobile-First Design**: Optimized for low-bandwidth, mobile devices
- 💾 **Offline Support**: IndexedDB/localStorage caching for unreliable connectivity
- 💬 **SMS Notifications**: Get notified via SMS when alerts trigger or prices change significantly
- 🎯 **Confidence Indicators**: Visual indicators showing data reliability
- ⏰ **Last Updated Timestamps**: Clear visibility of data freshness

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Celery + Redis** - Background task processing
- **Twilio** - SMS notification service
- **JWT** - Authentication tokens

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Recharts** - Chart visualization

## Project Structure

```
.
├── alembic/              # Database migrations
├── frontend/             # Next.js frontend application
│   ├── src/
│   │   ├── app/         # Next.js pages and routes
│   │   ├── components/  # React components
│   │   ├── contexts/    # React contexts (Auth, Language)
│   │   └── lib/         # API clients and utilities
│   └── package.json
├── models/               # SQLModel database models
├── routers/              # FastAPI route handlers
├── schemas/              # Pydantic validation schemas
├── services/             # Business logic services
├── scripts/              # Utility scripts (seeding, migration)
├── utils/                # Helper utilities
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Quick Start (Local Development)

**Get up and running in 5 minutes with SQLite (no database setup required!):**

```bash
# 1. Backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy env.example .env  # Windows
# cp env.example .env  # Linux/Mac
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# 2. Frontend (in a new terminal)
cd frontend
npm install
copy env.example .env.local  # Windows
# cp env.example .env.local  # Linux/Mac
npm run dev
```

That's it! The SQLite database will be created automatically. Visit `http://localhost:3000` to see the app.

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **SQLite** (included with Python - no installation needed for development)
- **PostgreSQL** (optional, only needed for production)
- **Redis** (optional, for Celery background tasks)
- **Twilio Account** (optional, for SMS notifications)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "farmer alert - Copy"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy `env.example` to `.env`:
   ```bash
   # Windows
   copy env.example .env
   
   # Linux/Mac
   cp env.example .env
   ```
   
   The `.env` file is already configured for local development with SQLite. 
   **No database setup required!** SQLite will automatically create `gebeyaalert.db` on first run.
   
   Minimum required `.env` configuration:
   ```env
   # Database - SQLite is used by default (no setup needed)
   DATABASE_URL=sqlite:///./gebeyaalert.db
   
   # JWT Secret - Generate a random key for security
   # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
   SECRET_KEY=your-secret-key-here-change-this-in-production
   
   # Application settings
   ENVIRONMENT=development
   DEBUG=True
   FRONTEND_URL=http://localhost:3000
   ```
   
   **Note**: SQLite is perfect for local development. The database file (`gebeyaalert.db`) will be created automatically in the project root when you first run the server.

5. **Run the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```
   
   The database (SQLite) will be **automatically created** on first run. No manual setup needed!
   
   The API will be available at:
   - **API**: `http://localhost:8080`
   - **API Docs**: `http://localhost:8080/docs`
   - **ReDoc**: `http://localhost:8080/redoc`

6. **If you see CORS or database errors:**
   
   If you have an old database without the new columns, reset it:
   ```bash
   python scripts/reset_db.py
   ```
   
   Or manually delete `gebeyaalert.db` and restart the server.

7. **Create an admin user (optional)**
   ```bash
   python scripts/create_admin.py
   ```
   
   This will prompt you to create an admin account for managing the system.

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   
   Copy `env.example` to `.env.local`:
   ```bash
   # Windows
   copy env.example .env.local
   
   # Linux/Mac
   cp env.example .env.local
   ```
   
   The `.env.local` file is already configured to connect to the local backend:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```
   
   **Important**: Make sure your backend is running on port 8080 before starting the frontend!

4. **Run the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`
   
   The frontend will automatically connect to `http://localhost:8080` (your local FastAPI backend).

## Deployment

### Free Deployment Options

This application can be deployed for free using the following platforms:

#### Option 1: Railway (Recommended - Easiest)

**Backend Deployment:**
1. Sign up at [Railway.app](https://railway.app) (free tier available)
2. Create a new project
3. Click "New" → "GitHub Repo" and connect your repository
4. Add a PostgreSQL database service
5. Set environment variables in the "Variables" tab:
   - `DATABASE_URL` (will be auto-set if you add PostgreSQL service)
   - `SECRET_KEY` (generate a random string)
   - `ENVIRONMENT=production`
   - `DEBUG=False`
   - `FRONTEND_URL=https://your-frontend-url.vercel.app`
   - Add Twilio credentials if using SMS
6. Railway will automatically detect it's a Python app and deploy

**Frontend Deployment (Vercel):**
1. Sign up at [Vercel.com](https://vercel.com) (free tier available)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app`
5. Deploy

**Cost:** Free for hobby projects (limited hours)

#### Option 2: Render

**Backend Deployment:**
1. Sign up at [Render.com](https://render.com) (free tier available)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add a PostgreSQL database (free tier available)
7. Set environment variables
8. Deploy

**Frontend Deployment:**
1. Create a new "Static Site" on Render
2. Connect repository, set root directory to `frontend`
3. Build command: `cd frontend && npm install && npm run build`
4. Publish directory: `frontend/.next`
5. Add environment variable: `NEXT_PUBLIC_API_URL`

**Note:** Render free tier spins down after inactivity (takes ~30s to wake up)

#### Option 3: Fly.io

1. Sign up at [Fly.io](https://fly.io)
2. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. Run `fly launch` in project root
4. Add PostgreSQL: `fly postgres create`
5. Set secrets: `fly secrets set SECRET_KEY=...`
6. Deploy: `fly deploy`

**Cost:** Free tier includes 3 VMs

#### Option 4: PythonAnywhere (Backend only)

1. Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com) (free tier available)
2. Upload your code via Git or file upload
3. Create a new web app
4. Configure virtual environment and dependencies
5. Set up PostgreSQL or use MySQL (included)
6. Configure environment variables
7. Point frontend to PythonAnywhere URL

**Limitations:** Free tier requires manual restarts daily

### Environment Variables for Production

When deploying to production, make sure to set these environment variables:

**Backend (.env):**
```env
# Use PostgreSQL for production
# Set DATABASE_URL to your PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:5432/dbname
# If DATABASE_URL is not set, SQLite will be used automatically (for local development)

SECRET_KEY=<generate-a-strong-random-key>
ENVIRONMENT=production
DEBUG=False
FRONTEND_URL=https://your-frontend-domain.com
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_PHONE_NUMBER=<your-twilio-number>
SMS_ENABLED=True
```

**Note**: For local development, SQLite is used automatically. Only set PostgreSQL URL when deploying to production.

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Generating SECRET_KEY

Generate a secure secret key:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
```

## Running Background Tasks (Celery)

For production, you'll want to run Celery workers to process price alerts:

```bash
# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery beat scheduler (for scheduled tasks)
celery -A celery_app beat --loglevel=info
```

On most platforms, you can run these as separate services or use process managers like Supervisor.

## Database Configuration

### Development (SQLite - Default)

**SQLite is used by default** for local development. No setup required!

- Database file: `gebeyaalert.db` (created automatically in project root)
- No installation needed - SQLite comes with Python
- Perfect for development and testing
- All AI prediction features work with SQLite

### Production (PostgreSQL)

When deploying to production, switch to PostgreSQL:

1. **Set DATABASE_URL environment variable:**
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ENVIRONMENT=production
   DEBUG=False
   ```

2. **The app automatically:**
   - Detects PostgreSQL from the `DATABASE_URL` connection string
   - Creates tables on startup (via `init_db()`)
   - Configures connection pooling for PostgreSQL

3. **Initialize data (after first deployment):**
   ```bash
   python scripts/seed_data.py
   python scripts/create_admin.py +1234567890 yourpassword
   ```

**Note:** If `DATABASE_URL` is not set, the app defaults to SQLite for local development. Set `DATABASE_URL` to use PostgreSQL in production.

The system automatically detects SQLite vs PostgreSQL and configures connection pooling accordingly.

## Database Migrations

Migrations work with both SQLite (development) and PostgreSQL (production):

**Create a new migration:**
```bash
alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Note**: When switching from SQLite to PostgreSQL, you may need to adjust some migration scripts. Test migrations in development first!

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## Testing

```bash
# Backend (if tests are added)
pytest

# Frontend
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`

## African Context & Design Decisions

### Mobile-First & Low-Bandwidth Optimization
- **Offline-first architecture**: Data cached locally using IndexedDB with localStorage fallback
- **Lightweight API responses**: Optimized queries with limits and efficient database indexing
- **Progressive loading**: Skeleton screens and cached data for instant perceived performance
- **Minimal dependencies**: Reduced bundle size for faster loading on 2G/3G networks

### User Experience for African Farmers
- **Simple, clear interface**: Large buttons, readable fonts, intuitive icons
- **Visual indicators**: Color-coded trends (green=rising, red=falling) with emoji support
- **Confidence badges**: Farmers can see how reliable each price prediction is
- **Source tracking**: Transparency about where price data comes from
- **Last updated timestamps**: Farmers know if data is fresh or stale

### Practical AI Implementation
- **No black boxes**: Simple, interpretable models (moving averages, regression)
- **Works with limited data**: Handles sparse datasets gracefully
- **Fast predictions**: No heavy computation, suitable for low-end devices
- **Human-readable output**: Recommendations in plain language, not technical jargon

### Technology Choices
- **FastAPI**: High performance, async support, perfect for mobile API
- **Next.js**: Server-side rendering for better initial load, static generation where possible
- **PostgreSQL**: Reliable, scalable, handles large price history datasets
- **IndexedDB**: Modern browser storage for offline support without external dependencies

## API Endpoints

### Price Predictions
- `GET /api/v1/prices/predictions/{crop_id}/{market_id}?days_ahead=7`
  - Returns price prediction with trend and confidence
  - Uses moving averages and simple regression

### Best Time to Sell
- `GET /api/v1/prices/best-time-to-sell/{crop_id}/{market_id}`
  - Returns actionable selling recommendation
  - Analyzes historical patterns and current trends

### Latest Prices (Enhanced)
- `GET /api/v1/prices/latest?limit=10`
  - Returns latest prices with source and confidence scores
  - Optimized query for large datasets

## Roadmap

- [x] Price predictions using statistical methods
- [x] Best time to sell recommendations
- [x] Offline caching support
- [x] Confidence scoring and source tracking
- [ ] Email notifications in addition to SMS
- [ ] Mobile app (React Native)
- [ ] Weather integration for crop planning
- [ ] Market comparison charts
- [ ] Export data to CSV/Excel
- [ ] More African languages (Swahili, Hausa, Yoruba)
- [ ] Voice-based interface for illiterate farmers

## Contributing

We welcome contributions! This project is designed to help African farmers, so:
- Keep code simple and maintainable
- Prioritize mobile and low-bandwidth users
- Test on real devices with slow connections
- Consider offline scenarios
- Write clear, human-readable recommendations

## License

This project is open source and available under the MIT License.

---

Made with ❤️ for African farmers

