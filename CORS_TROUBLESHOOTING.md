# CORS Error Troubleshooting Guide

## Understanding the Error

The CORS (Cross-Origin Resource Sharing) error occurs when:
1. Frontend (http://localhost:3000) tries to access backend (http://localhost:8080)
2. Backend doesn't send proper CORS headers
3. Browser blocks the request for security

## Common Causes & Solutions

### 1. Backend Not Running

**Symptom**: CORS error + Network Error

**Solution**: 
```bash
# Make sure backend is running
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Check: http://localhost:8080/health should return `{"status": "healthy"}`

### 2. Database Schema Mismatch (500 Error)

**Symptom**: CORS error + 500 Internal Server Error

**Cause**: Database missing new columns (`source`, `confidence_score`)

**Solution A - Recreate Database (Development):**
```bash
# Delete old database
rm gebeyaalert.db  # Linux/Mac
del gebeyaalert.db  # Windows

# Restart server - database will be recreated
uvicorn main:app --reload
```

**Solution B - Run Migrations:**
```bash
# Create migration for new columns
alembic revision --autogenerate -m "add_source_and_confidence_to_prices"

# Apply migration
alembic upgrade head
```

### 3. CORS Configuration Issue

**Symptom**: CORS error but backend is running

**Check**: Verify `.env` file has:
```env
FRONTEND_URL=http://localhost:3000
```

**Solution**: The code now includes CORS headers in all error responses. If still having issues:

1. Check backend logs for CORS allowed origins:
   ```
   CORS allowed origins: ['http://localhost:3000', ...]
   ```

2. Verify frontend URL matches exactly (no trailing slash)

### 4. Port Mismatch

**Symptom**: Connection refused

**Check**:
- Backend port: Check `PORT` in `.env` (default: 8080)
- Frontend API URL: Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`

**Solution**: Make sure they match:
```env
# Backend .env
PORT=8080

# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Quick Fix Checklist

1. ✅ Backend is running on port 8080
2. ✅ Frontend `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8080`
3. ✅ Backend `.env` has `FRONTEND_URL=http://localhost:3000`
4. ✅ Database exists and has correct schema (or delete and recreate)
5. ✅ No firewall blocking localhost connections
6. ✅ Browser console shows actual error (not just CORS)

## Testing CORS

Test the backend directly:
```bash
# Test CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8080/api/v1/prices/latest \
     -v
```

Should see `Access-Control-Allow-Origin: http://localhost:3000` in response.

## Still Having Issues?

1. **Check backend logs** - Look for error messages when request arrives
2. **Check browser Network tab** - See actual request/response headers
3. **Try direct API call** - Open http://localhost:8080/api/v1/prices/latest in browser
4. **Clear browser cache** - Sometimes cached CORS errors persist

## Production Notes

For production, make sure:
- `FRONTEND_URL` matches your actual frontend domain
- CORS middleware is configured correctly
- No hardcoded localhost URLs
