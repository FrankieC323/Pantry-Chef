"""
Password hashing + JWT session handling.

Standard FastAPI pattern: password hashed with bcrypt directly (NOT via
passlib -- passlib 1.7.4's bcrypt backend detection is broken against
bcrypt>=4.1 and raises spurious "password too long" errors even for short
passwords; calling the bcrypt package directly sidesteps that entirely), a
signed JWT handed to the client on login (python-jose), verified on every
protected request via the OAuth2PasswordBearer scheme below. No refresh
tokens or revocation list -- tokens just expire after jwt_expire_minutes
and the user logs in again. That's the right amount of complexity for a
handful of staff accounts; a full session-management system would be
over-building for what this needs.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.config import get_settings
from app.db.session import get_db

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# bcrypt's algorithm ignores bytes past 72 -- UserCreate already caps
# password length at 200 chars, so truncate defensively rather than let
# the bcrypt library raise on an unusually long paste.
_MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw_bytes = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))


def create_access_token(username: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    settings = get_settings()
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_error
    return user
