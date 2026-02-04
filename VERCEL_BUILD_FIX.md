# Vercel Build Fix - Missing @/lib/api Module

## Problem
Vercel build fails with:
```
Module not found: Can't resolve '@/lib/api'
```

## Root Cause
The file `frontend/src/lib/api.ts` exists locally but may not be committed to git, so Vercel can't find it during the build.

## Solution

### Step 1: Verify the file exists locally
The file `frontend/src/lib/api.ts` should exist and export `apiClient`.

### Step 2: Commit the file to git
```bash
cd frontend
git add src/lib/api.ts
git commit -m "Add api.ts module"
git push
```

### Step 3: Verify all lib files are committed
Make sure all files in `frontend/src/lib/` are committed:
```bash
git status frontend/src/lib/
```

Files that should be committed:
- `frontend/src/lib/api.ts` ✅ (exports apiClient)
- `frontend/src/lib/apiClient.ts` ✅
- `frontend/src/lib/auth.ts` ✅
- `frontend/src/lib/server-auth.ts` ✅

### Step 4: Re-deploy on Vercel
After committing and pushing, Vercel should automatically trigger a new build. If not, manually trigger a deployment.

## Verification

The `api.ts` file should:
1. Export `apiClient` instance
2. Be located at `frontend/src/lib/api.ts`
3. Be committed to git

## Alternative: If file is missing

If the file doesn't exist in your repository, you can recreate it. The file should export `apiClient` from the ApiClient class.

## Files that import @/lib/api

These files need `@/lib/api`:
- `src/app/admin/page.tsx`
- `src/app/alerts/new/page.tsx`
- `src/app/alerts/page.tsx`
- `src/app/dashboard/page.tsx`
- `src/app/history/page.tsx`
- `src/components/BestTimeToSell.tsx`
- `src/components/PriceForecast.tsx`

All of these import: `import { apiClient } from '@/lib/api'`
