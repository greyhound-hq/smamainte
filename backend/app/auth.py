import os
import json
from typing import Optional
from fastapi import Header, HTTPException
from fastapi import Depends
from .config import settings

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials
    FIREBASE_AVAILABLE = True
except Exception:
    firebase_admin = None
    firebase_auth = None
    credentials = None
    FIREBASE_AVAILABLE = False


_initialized = False


def _init_firebase_admin():
    global _initialized
    if _initialized:
        return
    cred_json = os.environ.get('FIREBASE_ADMIN_CREDENTIALS_JSON')
    cred_path = os.environ.get('FIREBASE_ADMIN_CREDENTIALS_PATH')
    try:
        if cred_json and firebase_admin and credentials:
            data = json.loads(cred_json)
            cred = credentials.Certificate(data)
            firebase_admin.initialize_app(cred)
            _initialized = True
        elif cred_path and firebase_admin and credentials:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _initialized = True
    except Exception:
        # don't block startup if admin credentials are not provided
        _initialized = False


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Verify Firebase ID token from Authorization header (Bearer <token>).

    If `FIREBASE_ADMIN_CREDENTIALS_JSON` or `FIREBASE_ADMIN_CREDENTIALS_PATH` env var is set,
    the token will be verified using the Admin SDK. Otherwise this returns a development user.
    """
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ', 1)[1].strip()

    if FIREBASE_AVAILABLE:
        try:
            _init_firebase_admin()
            if _initialized and token:
                decoded = firebase_auth.verify_id_token(token)
                return {
                    'uid': decoded.get('uid'),
                    'email': decoded.get('email')
                }
        except Exception:
            raise HTTPException(status_code=401, detail='Invalid auth token')

    # Fallback for development: if token present, return a pseudo-user; otherwise anonymous dev user
    if token:
        return {'uid': f'dev-{token[:8]}'}
    return {'uid': 'dev-anonymous'}


def _is_admin_user(user: dict) -> bool:
    """Check whether the provided user dict is considered admin.

    This checks `settings.ADMIN_EMAILS` and `settings.ADMIN_UIDS` (comma-separated).
    """
    if not user:
        return False
    admin_emails = [e.strip().lower() for e in (settings.ADMIN_EMAILS or "").split(',') if e.strip()]
    admin_uids = [u.strip() for u in (settings.ADMIN_UIDS or "").split(',') if u.strip()]
    email = user.get('email')
    uid = user.get('uid')
    if email and email.lower() in admin_emails:
        return True
    if uid and uid in admin_uids:
        return True
    return False


def require_admin(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to require an admin user. Raises 403 if not admin.

    Use this in FastAPI endpoints as `Depends(require_admin)`.
    """
    user = get_current_user(authorization)
    if not _is_admin_user(user):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    return user
