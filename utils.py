from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from fastapi import Request
import jwt
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load file .env
load_dotenv()

# Ambil nilai dari .env
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")  # Default sebagai string "15"
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default ke HS256 jika tidak ada

# Pastikan nilai ACCESS_TOKEN_EXPIRE_MINUTES dikonversi ke integer dengan aman
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)
except ValueError:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES harus berupa angka valid dalam file .env")

def create_access_token(data: dict):
    """
    Membuat JWT access token dengan expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Tambahkan waktu expire ke payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Setup hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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