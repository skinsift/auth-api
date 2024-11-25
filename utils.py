from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from fastapi import Request
import logging

# Setup hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Error handling
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

from datetime import datetime, timedelta

# Mengatur durasi token (dalam menit)
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token berlaku selama 30 menit

def create_access_token(data: dict):
    """
    Membuat JWT access token dengan expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Tambahkan waktu expire ke payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
