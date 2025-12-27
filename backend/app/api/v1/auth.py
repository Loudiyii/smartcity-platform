"""Authentication API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.dependencies import get_supabase_client

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MessageResponse(BaseModel):
    message: str


@router.post("/register", response_model=TokenResponse)
async def register(user_data: RegisterRequest):
    """
    Register a new user account.

    Creates a new user in Supabase Auth and sends a verification email.
    """
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })

        if not response.user:
            raise HTTPException(
                status_code=400,
                detail="Registration failed. Email may already be in use."
            )

        return TokenResponse(
            access_token=response.session.access_token if response.session else "",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": user_data.full_name
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    User login with email and password.

    Returns an access token for authenticated requests.
    """
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return TokenResponse(
            access_token=response.session.access_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata
            }
        )

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Send password reset email.

    Sends an email with a password reset link to the user's email address.
    """
    supabase = get_supabase_client()

    try:
        # Supabase sends reset email automatically
        supabase.auth.reset_password_email(request.email)

        return MessageResponse(
            message=f"Password reset email sent to {request.email}. Please check your inbox."
        )

    except Exception as e:
        # Don't reveal if email exists for security
        return MessageResponse(
            message=f"If an account exists for {request.email}, a password reset email has been sent."
        )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password with token from email.

    Uses the token from the reset email to set a new password.
    """
    supabase = get_supabase_client()

    try:
        response = supabase.auth.update_user({
            "password": request.new_password
        })

        if not response.user:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        return MessageResponse(message="Password reset successfully")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Password reset failed: {str(e)}"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """User logout - invalidates the current session."""
    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
        return MessageResponse(message="Logged out successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")
