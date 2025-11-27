#Login işlemleri
"""
Authentication Controller (English docstring)

Provides HTTP endpoints for user authentication and JWT token generation.

Flow:
1. Client POST /login with username and password.
2. Credentials are validated against the database via authenticate_user.
3. On success, a JWT bearer token is generated and stored (in-memory or Redis).
4. Token is returned to client for use in subsequent authenticated requests.

Endpoints:
- POST /login
    Authenticate a user by username/password and return a JWT bearer token.

Notes:
- Passwords should be hashed (bcrypt) before storage and comparison.
- Generated tokens are stored for later validation in subsequent requests.
- For production, use persistent token storage (Redis, database) instead of in-memory.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth_service import authenticate_user, create_token
from utils.mail_logger import MailLogger

router = APIRouter()

class LoginRequest(BaseModel):
    """Request model for user login.
    
    Attributes:
        username (str): Username of the user.
        password (str): Plaintext password of the user.
    """
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    """
    Authenticate a user and return a JWT bearer token.
    
    Validates the provided username and password against the database.
    If credentials are valid, generates a JWT bearer token and stores it
    for later validation. The token is required for all subsequent API requests.

    Args:
        req (LoginRequest): Login request containing username and password.

    Returns:
        dict: {
            "access_token": str,  # JWT bearer token
            "token_type": str     # Always "bearer"
        }

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    MailLogger.start("/auth/login")
    MailLogger.add(f"1) Login attempt with username: {req.username}")

    try:
        MailLogger.add("2) Authenticating user...")
        user = authenticate_user(req.username, req.password)
        
        if not user:
            MailLogger.add("❌ Authentication failed: Invalid credentials")
            MailLogger.send()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        MailLogger.add(f"3) User authenticated → User ID: {user['id']}")
        
        MailLogger.add("4) Generating JWT token...")
        token = create_token(user["id"])
        
        MailLogger.add("5) Token generated successfully")
        MailLogger.add("6) Login endpoint completed successfully")
        MailLogger.send()

        return {"access_token": token, "token_type": "bearer"}

    except HTTPException as e:
        MailLogger.add(f"❌ HTTP Exception: {str(e)}")
        MailLogger.send()
        raise

    except Exception as e:
        MailLogger.add(f"❌ Unexpected error: {str(e)}")
        MailLogger.send()
        raise HTTPException(status_code=500, detail="Internal server error")
