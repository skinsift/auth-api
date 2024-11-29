from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginSchema, TokenResponse
from crud import create_user, get_user_by_email, get_user_by_username
from database import get_db
from utils import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User
from dotenv import load_dotenv
from jose import jwt, JWTError  # Pastikan `python-jose` sudah terinstal
import os

# Load .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # Convert to integer

router = APIRouter()

# =======================
# Authentication Routes
# =======================

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(user.dict())  # Debugging input user
    
    # Cek apakah email atau username sudah terdaftar
    existing_email = get_user_by_email(db, user.Email)
    existing_username = get_user_by_username(db, user.Username)
    
    error_messages = []
    if existing_email:
        error_messages.append("Email already registered")
    if existing_username:
        error_messages.append("Username already registered")
    
    if error_messages:
        raise HTTPException(status_code=400, detail=error_messages)
    
    return create_user(db, user)

@router.post("/login", response_model=TokenResponse)
async def login_user(payload: LoginSchema, db: Session = Depends(get_db)):
    identifier = payload.username_or_email
    user = None

    if "@" in identifier:
        user = get_user_by_email(db, identifier)
    else:
        user = get_user_by_username(db, identifier)
    
    if not user or not verify_password(payload.password, user.Password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"user_id": user.Users_ID})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.Users_ID
    }

# OAuth2PasswordBearer dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fungsi untuk memverifikasi token JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.Users_ID == user_id).first()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user
