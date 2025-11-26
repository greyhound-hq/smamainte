# Firebase Setup Guide

This guide explains how to set up Firebase Authentication for production.

## 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select existing project
3. Enable Authentication > Sign-in method > Anonymous (if needed)
4. Enable Authentication > Sign-in method > Email/Password (optional)

## 2. Get Firebase Client Configuration

1. In Firebase Console, go to **Project Settings** (gear icon) > **General**
2. Scroll to "Your apps" section
3. Click "Add app" > Web (</>) if no web app exists
4. Copy the config values:
   - API Key
   - Auth Domain
   - Project ID
   - Storage Bucket
   - Messaging Sender ID
   - App ID

5. Create `frontend/.env.local` (gitignored):
   ```bash
   NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
   NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## 3. Generate Firebase Admin SDK Credentials

1. In Firebase Console, go to **Project Settings** > **Service accounts**
2. Click "Generate new private key"
3. Download the JSON file (e.g., `firebase-admin-key.json`)
4. **Keep this file secure** - never commit it to git

### For Local Development:

Create `backend/.env` (gitignored):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/cmms
GCS_BUCKET=your-gcs-bucket
GCP_SERVICE_ACCOUNT_JSON=/path/to/gcs-service-account.json
FIREBASE_ADMIN_CREDENTIALS_PATH=/path/to/firebase-admin-key.json
ADMIN_EMAILS=your-email@example.com
ADMIN_UIDS=
```

### For Production (Cloud Run / Docker):

Use the JSON content as an environment variable:

```bash
# Convert JSON file to single-line string
export FIREBASE_ADMIN_CREDENTIALS_JSON=$(cat firebase-admin-key.json | jq -c .)

# Or set directly in Cloud Run:
gcloud run services update YOUR_SERVICE \
  --set-env-vars="FIREBASE_ADMIN_CREDENTIALS_JSON=$(cat firebase-admin-key.json | jq -c .)" \
  --region=YOUR_REGION
```

## 4. Configure Admin Users

Add admin users to `.env`:

```bash
# Option 1: Use email addresses (recommended)
ADMIN_EMAILS=admin@example.com,manager@example.com

# Option 2: Use Firebase UIDs (for anonymous users or specific UIDs)
ADMIN_UIDS=abc123uid,xyz789uid
```

To find a user's UID:
1. Sign in to your app
2. Check Firebase Console > Authentication > Users
3. Copy the UID

## 5. Setup GitHub Actions Secrets

For CI/CD, add secrets to your GitHub repository:

1. Go to GitHub repo > **Settings** > **Secrets and variables** > **Actions**
2. Click "New repository secret"
3. Add the following secrets:

| Secret Name | Value |
|-------------|-------|
| `FIREBASE_ADMIN_CREDENTIALS_JSON` | Entire JSON content from step 3 (as single line) |
| `ADMIN_EMAILS` | `admin@example.com` |
| `GCS_BUCKET` | Your GCS bucket name |
| `DATABASE_URL` | PostgreSQL connection string for staging |

4. Update `.github/workflows/staging-verify.yml`:

```yaml
- name: Start backend (uvicorn) in background and capture logs
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    GCS_BUCKET: ${{ secrets.GCS_BUCKET }}
    FIREBASE_ADMIN_CREDENTIALS_JSON: ${{ secrets.FIREBASE_ADMIN_CREDENTIALS_JSON }}
    ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}
    ADMIN_UIDS: ${{ secrets.ADMIN_UIDS }}
  run: |
    # ... existing uvicorn startup
```

## 6. Test Authentication

### Test Anonymous Sign-In (Frontend):
1. Start frontend: `cd frontend && npm run dev`
2. Open browser to http://localhost:3000/login
3. Click "Anonymous Sign In"
4. Check browser console for token

### Test Token Verification (Backend):
```bash
# Get a token from frontend (check browser console after sign-in)
TOKEN="eyJhbGc..."

# Test protected endpoint
curl -X POST http://localhost:8000/equipments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Equipment"}'
```

Expected response:
- With valid admin token: `200 OK` with created equipment
- With invalid token: `401 Unauthorized`
- With non-admin token: `403 Forbidden`

## 7. Development Fallback

When Firebase Admin SDK is **not** configured (no credentials provided), the backend falls back to development mode:

- Any `Authorization: Bearer <token>` → Creates a dev user with `uid: "dev-<first8chars>"`
- No Authorization header → Creates anonymous dev user with `uid: "dev-anonymous"`

To enable admin privileges in dev mode, set:
```bash
ADMIN_UIDS=dev-faketoke  # Matches TEST_TOKEN=faketoken1234 in CI
```

## 8. Security Checklist

- [ ] Firebase Admin credentials file is in `.gitignore`
- [ ] Production credentials are stored in GitHub Secrets or Cloud Secret Manager
- [ ] `ADMIN_EMAILS` / `ADMIN_UIDS` are set correctly
- [ ] Frontend `.env.local` is gitignored
- [ ] Test token verification with real Firebase user
- [ ] Verify 403 response for non-admin users
- [ ] Verify 401 response for invalid tokens

## Troubleshooting

### "Invalid auth token" (401)
- Token might be expired (Firebase tokens expire after 1 hour)
- Refresh the token by calling `user.getIdToken(true)` in frontend
- Check that `FIREBASE_ADMIN_CREDENTIALS_JSON` is set correctly

### "Admin privileges required" (403)
- User is authenticated but not in `ADMIN_EMAILS` or `ADMIN_UIDS`
- Check the user's email/UID in Firebase Console > Authentication
- Update `.env` to include the user

### Firebase Admin SDK not initializing
- Check logs for initialization errors
- Verify JSON credentials are valid (test with `firebase-admin` locally)
- Ensure `firebase-admin` package is installed: `pip install firebase-admin`

## Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/admin/setup)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
