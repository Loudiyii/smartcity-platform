"""Authentication API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.dependencies import get_supabase_client

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """User login."""
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        return TokenResponse(access_token=response.session.access_token)

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout")
async def logout():
    """User logout."""
    supabase = get_supabase_client()
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}
