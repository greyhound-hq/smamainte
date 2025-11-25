import os
import json
from typing import Optional
from fastapi import Header, HTTPException

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
