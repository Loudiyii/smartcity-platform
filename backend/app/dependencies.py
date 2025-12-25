"""
Dependency injection for FastAPI
"""

from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

settings = get_settings()

security = HTTPBearer()


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token and return current user."""
    supabase = get_supabase_client()

    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
