# CORS Fix for Vercel Deployment

## Problem
After deploying to Vercel, login and signup are failing with CORS errors:
- `Access to XMLHttpRequest ... has been blocked by CORS policy`
- `No 'Access-Control-Allow-Origin' header is present`

## Root Cause
The backend CORS configuration wasn't properly allowing requests from the Vercel deployment URL.

## Solution Applied

### 1. Updated CORS Configuration (`main.py`)
- Added regex pattern to allow all Vercel subdomains: `https://gebeya-alert.*\.vercel\.app`
- Improved origin matching to handle trailing slashes
- Added fallback to exact origin matches

### 2. Environment Variables Required on Render

**Set these environment variables in your Render dashboard:**

1. **FRONTEND_URL** (Required)
   ```
   https://gebeya-alert-gg73.vercel.app
   ```
   (Use your actual Vercel deployment URL)

2. **DATABASE_URL** (Required for PostgreSQL)
   ```
   postgresql://user:password@host:port/database
   ```

3. **SECRET_KEY** (Required)
   ```
   <generate-a-strong-random-key>
   ```
   Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

4. **ENVIRONMENT** (Set to production)
   ```
   production
   ```

5. **DEBUG** (Set to false)
   ```
   false
   ```

## Steps to Fix

### Step 1: Update Backend Code
The CORS configuration has been updated in `main.py`. Commit and push:
```bash
git add main.py
git commit -m "Fix CORS for Vercel deployment"
git push
```

### Step 2: Set Environment Variables on Render

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add/Update these variables:
   - `FRONTEND_URL=https://gebeya-alert-gg73.vercel.app` (your actual Vercel URL)
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `SECRET_KEY=<your-secret-key>`
   - `DATABASE_URL=<your-postgresql-url>`

### Step 3: Restart Render Service
After updating environment variables, restart your Render service:
- Go to "Manual Deploy" → "Deploy latest commit"
- Or wait for automatic deployment

### Step 4: Verify CORS is Working

After deployment, check the logs. You should see:
```
CORS allowed origins: ['http://localhost:3000', ..., 'https://gebeya-alert-gg73.vercel.app']
```

### Step 5: Test the Frontend

1. Open your Vercel deployment
2. Try to login/signup
3. Check browser console for CORS errors
4. Check Network tab to see if requests are going through

## Troubleshooting

### Still Getting CORS Errors?

1. **Check the exact origin being sent:**
   - Open browser DevTools → Network tab
   - Look at the request headers
   - Check the `Origin` header value
   - Make sure it matches what's in `FRONTEND_URL`

2. **Verify environment variables:**
   - Check Render logs to see if `FRONTEND_URL` is being read
   - Look for: `CORS allowed origins: ...`

3. **Check for trailing slashes:**
   - Vercel URLs might have or not have trailing slashes
   - The code now handles both cases

4. **Verify the regex pattern:**
   - The pattern `https://gebeya-alert.*\.vercel\.app` should match:
     - `https://gebeya-alert-gg73.vercel.app`
     - `https://gebeya-alert-xyz.vercel.app`
     - Any Vercel subdomain

### 500 Errors on Login/Register

If you're getting 500 errors (not CORS), check:

1. **Database connection:**
   - Verify `DATABASE_URL` is set correctly
   - Check Render logs for database connection errors

2. **Secret key:**
   - Make sure `SECRET_KEY` is set
   - It should be a strong random string

3. **Database tables:**
   - Tables should be created automatically on startup
   - Check logs for: `✓ Database initialized`

## Testing Locally

To test CORS locally:

1. Set `FRONTEND_URL` in your `.env`:
   ```env
   FRONTEND_URL=https://gebeya-alert-gg73.vercel.app
   ```

2. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

3. Check the console output for:
   ```
   CORS allowed origins: [..., 'https://gebeya-alert-gg73.vercel.app']
   ```

## Additional Notes

- The CORS middleware is configured to allow credentials (cookies/auth tokens)
- Preflight requests (OPTIONS) are handled automatically
- CORS headers are added to all responses, including error responses

## Quick Checklist

- [ ] Updated `main.py` with new CORS configuration
- [ ] Committed and pushed changes
- [ ] Set `FRONTEND_URL` on Render (your Vercel URL)
- [ ] Set `ENVIRONMENT=production` on Render
- [ ] Set `DEBUG=false` on Render
- [ ] Set `SECRET_KEY` on Render
- [ ] Set `DATABASE_URL` on Render (PostgreSQL)
- [ ] Restarted Render service
- [ ] Tested login/signup on Vercel deployment
