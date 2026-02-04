"""
GebeyaAlert - Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import time

from config import settings
from database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="GebeyaAlert",
    description="Production-ready alert system",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware - Fixed to properly handle frontend requests
# Note: Cannot use allow_origins=["*"] with allow_credentials=True
# So we allow common development origins explicitly
allowed_origins = [
    "https://gebeya-alert-gg73.vercel.app/",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add frontend URL from config if specified (for production)
if settings.FRONTEND_URL:
    if settings.FRONTEND_URL not in allowed_origins:
        allowed_origins.append(settings.FRONTEND_URL)
    # Also add without trailing slash
    frontend_no_slash = settings.FRONTEND_URL.rstrip('/')
    if frontend_no_slash not in allowed_origins:
        allowed_origins.append(frontend_no_slash)

# Debug: Print allowed origins
if settings.DEBUG:
    print(f"CORS allowed origins: {allowed_origins}")

# Request logging middleware for debugging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.DEBUG:
            start_time = time.time()
            print(f"\n{'='*60}")
            print(f"Request: {request.method} {request.url}")
            print(f"Origin: {request.headers.get('origin', 'N/A')}")
            print(f"Content-Type: {request.headers.get('content-type', 'N/A')}")
        
        try:
            response = await call_next(request)
            if settings.DEBUG:
                process_time = time.time() - start_time
                print(f"Response: {response.status_code} ({process_time:.3f}s)")
                print(f"{'='*60}\n")
            return response
        except Exception as e:
            if settings.DEBUG:
                print(f"ERROR in middleware: {type(e).__name__}: {e}")
                print(traceback.format_exc())
                print(f"{'='*60}\n")
            # Return error response with CORS headers
            origin = request.headers.get("origin", "http://localhost:3000")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Internal server error: {str(e)}"},
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )

# Use specific origins to allow credentials (needed for cookies/auth tokens)
# CORS middleware must be added BEFORE other middleware to handle preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add request logging middleware after CORS
if settings.DEBUG:
    app.add_middleware(RequestLoggingMiddleware)

# Exception handlers to prevent connection resets
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors gracefully."""
    # Include CORS headers
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers=headers,
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions gracefully."""
    # Include CORS headers
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions to prevent connection resets."""
    # Always include CORS headers even on errors
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }
    
    if settings.DEBUG:
        # In debug mode, show full traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc()
            },
            headers=headers,
        )
    else:
        # In production, hide internal errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
            headers=headers,
        )


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("\n" + "=" * 60)
    print("FastAPI Server Starting...")
    print("=" * 60)

    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise

    # Migrate crop_type column if needed
    try:
        from scripts.migrate_crop_type import migrate_crop_type
        migrate_crop_type()
    except Exception as e:
        # Log error but don't fail startup
        print(f"⚠ Warning: Could not migrate crop_type column: {e}")
    
    # Seed initial data (crops and markets)
    try:
        from scripts.seed_data import seed_all
        seed_all()
        print("✓ Initial data seeded")
    except Exception as e:
        # Log error but don't fail startup
        print(f"⚠ Warning: Could not seed initial data: {e}")
    
    print("="*60)
    print("Server is ready and listening for requests!")
    print(f"CORS enabled for origins: {allowed_origins}")
    print("="*60 + "\n")


# Include API routers
from routers import auth_router
from routers.crops import router as crops_router
from routers.markets import router as markets_router
from routers.prices import router as prices_router
from routers.alerts import router as alerts_router
from routers.admin import router as admin_router
from routers.users import router as users_router

app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(crops_router, prefix=f"{settings.API_V1_PREFIX}/crops", tags=["crops"])
app.include_router(markets_router, prefix=f"{settings.API_V1_PREFIX}/markets", tags=["markets"])
app.include_router(prices_router, prefix=f"{settings.API_V1_PREFIX}/prices", tags=["prices"])
app.include_router(alerts_router, prefix=f"{settings.API_V1_PREFIX}/alerts", tags=["alerts"])
app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])
app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])


@app.get("/")
async def root():
    """Root endpoint."""
    print("[ROOT] Root endpoint called")
    return {"message": "GebeyaAlert API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    print("[HEALTH] Health check called")
    return {"status": "healthy"}


@app.get("/simple-test")
async def simple_test():
    """Very simple test endpoint with no dependencies."""
    print("[SIMPLE-TEST] Simple test endpoint called!")
    return {"message": "Simple test works!", "timestamp": time.time()}


@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify CORS and server are working."""
    return {"message": "Server is working!", "cors": "enabled"}


@app.post("/api/v1/test")
async def test_post_endpoint(request: Request):
    """Test POST endpoint to verify CORS and server are working."""
    try:
        body = await request.json()
        return {"message": "POST request received!", "data": body}
    except Exception as e:
        return {"message": "POST request received (no body)", "error": str(e)}


@app.get("/api/v1/test/db")
async def test_db_connection():
    """Test database connection."""
    try:
        from database import engine
        from sqlmodel import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        return {"status": "success", "message": "Database connection working"}
    except Exception as e:
        if settings.DEBUG:
            print(f"Database connection error: {e}")
            print(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

