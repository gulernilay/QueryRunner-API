"""
User Models

Pydantic models for user authentication and database representation.
These models enforce type safety, validate input data, and auto-generate OpenAPI documentation.

Models:
- UserLogin: Request model for user login with username and password.
- UserInDB: Database model representing a user record with hashed password.
"""
from pydantic import BaseModel

class UserLogin(BaseModel):
    """Request model for user login.
    
    Attributes:
        username (str): Username of the user attempting to log in.
        password (str): Plaintext password provided by the user.
    """
    username: str
    password: str

class UserInDB(BaseModel):
    """Database model representing a user record.
    
    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        hashed_password (str): Bcrypt-hashed password stored in the database.
    """
    id: int
    username: str
    hashed_password: str
