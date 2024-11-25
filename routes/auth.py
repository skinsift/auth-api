from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginSchema, TokenResponse
from crud import create_user, get_user_by_email, get_user_by_username, get_user_by_password
from database import get_db
from utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User
from utils import verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(user.dict()) 
    existing_user = get_user_by_email(db, user.Email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@router.post("/login", response_model=TokenResponse)
async def login_user(payload: LoginSchema, db: Session = Depends(get_db)):
    username = payload.username
    password = payload.password

    # Panggil get_user_by_username secara synchronous tanpa await
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.Password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Buat token JWT
    access_token = create_access_token(data={"user_id": user.User_ID})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.User_ID
    }
