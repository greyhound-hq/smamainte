import os
import jwt
from typing import Optional
from fastapi import Header, HTTPException
from fastapi import Depends
from .config import settings


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Verify Supabase JWT token from Authorization header (Bearer <token>).

    If `SUPABASE_JWT_SECRET` env var is set, the token will be verified.
    Otherwise this returns a development user.
    """
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ', 1)[1].strip()

    jwt_secret = os.environ.get('SUPABASE_JWT_SECRET')
    
    if jwt_secret and token:
        try:
            # Verify Supabase JWT token
            decoded = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )
            return {
                'uid': decoded.get('sub'),
                'email': decoded.get('email')
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid auth token')

    # Fallback for development: if token present, return a pseudo-user; otherwise anonymous dev user
    if token:
        return {'uid': f'dev-{token[:8]}', 'email': None}
    return {'uid': 'dev-anonymous', 'email': None}


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
