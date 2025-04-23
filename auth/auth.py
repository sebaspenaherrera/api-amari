import jwt
from jwt import InvalidTokenError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone


SECRET_KEY = "5a6a3d12b34d62006fa989d1ca11c80b72e2a02d78ed46960b50c3c88e466a17"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# TODO: Implement a real database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admi Nistrator",
        "email": "mobilenettelma@gmail.com",
        "hashed_password": "$2a$12$1tPWMprSKGQ2Gg9mClG91ecTea/48GCfR5vk4Pgv8HaDPywYU9.ma",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ************************************************************************************************************************************************
# Authorization models
# ************************************************************************************************************************************************

"""
Models for user authentication and authorization.
These models are used to define the structure of the data.
- Token: Represents the access token and its type.
- TokenData: Represents the data contained in the token.
- User: Represents a user with username, email, full name, and disabled status.
- UserInDB: Represents a user in the database with hashed password.

TODO: User creation model
"""

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str


# ************************************************************************************************************************************************
# Authentication functions
# ************************************************************************************************************************************************

def verify_password(plain_password, hashed_password):
    """
    Verify the password by comparing the plain password with the hashed password.
    
    Parameters:
    - plain_password (str): The plain password to verify.
    - hashed_password (str): The hashed password to compare against.
    
    Returns:
    - bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash the password using bcrypt.

    Parameters:
    - password (str): The password to hash.

    Returns:
    - str: The hashed password.
    """
    return pwd_context.hash(password)


def get_user(db, username: str):
    """
    Extract the user from the database by username.

    Parameters:
    - db: The database to search in.
    - username (str): The username to search for.

    Returns:
    - UserInDB: The user object if found, None otherwise.
    """

    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    

def authenticate_user(fake_db, username: str, password: str):
    """
    Authenticate a user by checking the username and password.
    If the user is found and the password matches, return the user object.
    Otherwise, return False.

    Parameters:
    - fake_db: The database to check against.
    - username (str): The username to authenticate.
    - password (str): The password to authenticate.
    """

    user = fake_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return UserInDB(**user)


def create_access_token(data: dict, expires_delta: int | None = None):
    """
    Create a JWT token with an expiration time.

    Parameters:
    - data (dict): The data to encode in the token.
    - expires_delta (int | None): The expiration time in minutes. If None, defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get the current user from the token.

    Parameters:
    - token (str): The JWT token.
    
    Returns:
    - User: The user object if the token is valid.

    Raises:
    - credentials_exception: If the token is invalid or expired.
    - InvalidTokenError: If the token is invalid.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]):
    """
    Check if the current user is enabled or disabled

    Parameters:
    - current_user (User): The current user object.

    Returns:
    - User: The current user object if the user is enabled.
    Raises:
    - HTTPException: If the user is disabled.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user