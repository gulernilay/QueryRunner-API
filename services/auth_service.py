#Token üretme ve doğrulama işlemleri
"""Authentication service (English docstrings).

Provides helper functions to authenticate users, create JWT tokens and validate them.
This module relies on `get_user_by_username` from the database layer and `generate_jwt`
from the JWT utilities.

Notes:
- token_store is an in-memory store for demo purposes. Use Redis or another persistent
  store in production.
- There is a duplicate `authenticate_user` definition retained for backward compatibility;
  consider removing one during refactor.
"""

from utils.jwt_utils import generate_jwt
from database import get_user_by_username
import bcrypt

# Memory dict (örnek, prod'da Redis tercih edilir)
token_store = {}

def authenticate_user(username: str, password: str):
    """Authenticate a user by username and password.

    Calls the database accessor to retrieve a user record and returns it if found.
    Password verification (e.g. bcrypt) is currently commented out; enable it when
    stored passwords are hashed.

    Args:
        username (str): Username provided by the client.
        password (str): Plaintext password provided by the client.

    Returns:
        dict | None: User record dict when authentication succeeds, otherwise None.
    """
    user = get_user_by_username(username ,password)
    if not user:
        return None
    #if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
    #    return None
    return user

def create_token(user_id: int):
    """Generate a JWT token for the given user and store it in memory.

    Args:
        user_id (int): Identifier of the authenticated user.

    Returns:
        str: Generated JWT token.
    """
    token = generate_jwt({"user_id": user_id})
    token_store[user_id] = token
    return token

def validate_token(user_id: int, token: str):
    """Validate the provided token against the in-memory token store.

    Args:
        user_id (int): Identifier of the user.
        token (str): JWT token to validate.

    Returns:
        bool: True if the token matches the stored token for the user, otherwise False.
    """
    return token_store.get(user_id) == token

def authenticate_user(username: str, password: str):
    """Duplicate authenticate_user kept for backward compatibility.

    This simply calls the database accessor and returns the user or None.
    Consider removing this duplicate and consolidating logic.

    Args:
        username (str): Username.
        password (str): Password.

    Returns:
        dict | None: User record or None.
    """
    user = get_user_by_username(username, password)
    if not user:
        return None
    return user
