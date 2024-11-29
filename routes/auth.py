from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginSchema, TokenResponse, AddNoteRequest, UserNotesResponse, IngredientDetailResponse
from crud import create_user, get_user_by_email, get_user_by_username
from database import get_db
from utils import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User, Ingredient, Notes
from dotenv import load_dotenv
from jose import jwt, JWTError  # Pastikan `python-jose` sudah terinstal
import os

# Load .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAY", "1"))

router = APIRouter()

# =======================
# Authentication Routes
# =======================

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Debugging input user
    print(user.dict())

    # Check if email or username is already registered
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
    """
    Login a user and return an access token.
    """
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
        "user_id": user.Users_ID,
        "username": user.Username,
        "email": user.Email
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
        print(f"Decoded user_id: {user_id}")  # Debugging output
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.Users_ID == user_id).first()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

# =======================
# User Notes Routes
# =======================

# ====== Endpoint Get Notes ======
@router.get("/user/notes", response_model=UserNotesResponse)
async def get_user_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mendapatkan daftar notes pengguna beserta detail ingredients (nama, rating, kategori)
    """
    # Query untuk mengambil notes pengguna beserta detail ingredients
    notes_query = (
        db.query(Notes, Ingredient)
        .join(Ingredient, Notes.id_ingredients == Ingredient.Id_Ingredients)
        .filter(Notes.users_id == current_user.Users_ID)
        .all()
    )
    if not notes_query:
        raise HTTPException(status_code=404, detail="No notes found for user")


    print(f"Query result: {notes_query}")  # Debugging output
    
    # Susun respons
    response = []
    for notes, ingredient in notes_query:
        response.append({
            "id": notes.id_ingredients,
            "name": ingredient.nama,
            "rating": ingredient.rating,
            "category": ingredient.kategoriidn,
            "preference": notes.notes,
        })

    return {"notes": response}

@router.post("/user/notes/add")
async def add_user_note(
    request: AddNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Menambahkan catatan ingredient ke tabel notes.
    """
    # Verifikasi bahwa preference valid
    if request.preference not in ["Suka", "Tidak Suka"]:
        raise HTTPException(status_code=400, detail="Preference must be 'Suka' or 'Tidak Suka'")

    # Cek apakah ingredient dengan Id_Ingredients ada
    ingredient = db.query(Ingredient).filter(Ingredient.Id_Ingredients == request.Id_Ingredients).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Cek apakah catatan sudah ada
    existing_note = db.query(Notes).filter(
        Notes.users_id == current_user.Users_ID,
        Notes.id_ingredients == request.Id_Ingredients
    ).first()
    if existing_note:
        raise HTTPException(status_code=400, detail="Note for this ingredient already exists")

    # Tambahkan catatan baru
    new_note = Notes(
        users_id=current_user.Users_ID,
        id_ingredients=request.Id_Ingredients,
        notes=request.preference,
    )
    db.add(new_note)
    db.commit()

    return {"message": f"Ingredient with Id_Ingredients {request.Id_Ingredients} added to {request.preference} list"}


@router.delete("/user/notes/remove")
async def remove_user_note(
    request: AddNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Menghapus catatan ingredient dari tabel notes.
    """
    # Cari catatan yang sesuai
    note = db.query(Notes).filter(
        Notes.users_id == current_user.Users_ID,
        Notes.id_ingredients == request.Id_Ingredients
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Hapus catatan
    db.delete(note)
    db.commit()

    return {"message": f"Ingredient with Id_Ingredients {request.Id_Ingredients} removed from notes"}
