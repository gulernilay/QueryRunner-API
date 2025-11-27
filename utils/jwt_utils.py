"""
JWT Utilities (English docstring)

Provides helper functions to generate, decode and verify JWT (JSON Web Tokens)
for user authentication and authorization.

Exports:
- generate_jwt(data: dict, expires_delta: int) -> str
    Generate a signed JWT bearer token with optional expiration.

- decode_jwt(token: str) -> dict | None
    Decode a JWT token without validation (for debugging only).

- verify_jwt(token: str) -> dict | None
    Verify and decode a JWT token, returning the payload on success.

Security Notes:
- SECRET_KEY should be stored in environment variables (.env), not hardcoded.
- Use HTTPS in production to prevent token interception.
- Tokens include an expiration time (exp claim) to limit their lifetime.
"""

import jwt
from datetime import datetime, timedelta
import os

# TODO: Move to .env file
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

def generate_jwt(data: dict, expires_delta: int = 30):
    """
    Generate a signed JWT bearer token.
    
    Creates a JWT token containing the provided data and an expiration timestamp.
    The token is signed using the SECRET_KEY with the HS256 algorithm.

    Args:
        data (dict): Payload data to encode in the token (e.g., {"user_id": 1}).
        expires_delta (int): Token expiration time in minutes. Default is 30 minutes.

    Returns:
        str: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str):
    """
    Decode a JWT token without verification (for debugging only).
    
    Decodes the token and returns its payload. Does NOT validate the signature
    or expiration. Use verify_jwt() for production code that requires validation.

    Args:
        token (str): JWT token string to decode.

    Returns:
        dict | None: Decoded payload dict on success, None on decode failure.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    except Exception as e:
        return None

def verify_jwt(token: str):
    """
    Verify and decode a JWT token.
    
    Validates the token signature, expiration time and other claims.
    Returns the payload only if the token is valid and not expired.

    Args:
        token (str): JWT token string to verify.

    Returns:
        dict | None: Decoded payload dict (contains user_id, exp, etc.) on success.
                     Returns None if token is invalid, expired or malformed.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        return None