from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginSchema, LoginResult, LoginResponse, AddNoteRequest, NoteDetail, UserNotesResponse, IngredientDetailResponse
from crud import create_user, get_user_by_email, get_user_by_username
from database import get_db
from utils import verify_password, create_access_token, create_response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User, Ingredient, Notes
from dotenv import load_dotenv
import os
from utils import get_current_user, create_response
from typing import List, Optional, Dict, Any
from fastapi.responses import JSONResponse

# Load .env file
load_dotenv()

router = APIRouter()

# =======================
# Authentication Routes
# =======================

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Debugging untuk melihat data user yang diterima
    print(user.dict())

    # Periksa apakah email atau username sudah terdaftar
    existing_email = get_user_by_email(db, user.Email)
    existing_username = get_user_by_username(db, user.Username)

    error_messages: List[str] = []
    if existing_email:
        error_messages.append("Email already registered")
    if existing_username:
        error_messages.append("Username already registered")

    # Jika ada kesalahan, kembalikan dengan status 400
    if error_messages:
        return create_response(
            status_code=400,
            message="Registration failed due to errors",
            data={"errors": error_messages},
        )

    # Buat pengguna baru
    new_user = create_user(db, user)

    # Respons sukses
    return create_response(
        status_code=201,
        message="User registered successfully",
    )

@router.post("/login", response_model=LoginResponse)
async def login_user(payload: LoginSchema, db: Session = Depends(get_db)):
    identifier = payload.username_or_email
    user = None

    # Identifikasi apakah menggunakan email atau username
    if "@" in identifier:
        user = get_user_by_email(db, identifier)
    else:
        user = get_user_by_username(db, identifier)

    # Verifikasi kredensial
    if not user or not verify_password(payload.password, user.Password):
        # Gunakan create_response untuk error 400
        return create_response(
            status_code=400,
            message="Invalid credentials",
            data=None
        )

    # Buat token akses
    access_token = create_access_token(data={"user_id": user.Users_ID})

    # Struktur login result yang sesuai
    login_result = {
        "userId": user.Users_ID,  # Menggunakan userId sesuai format yang diminta
        "name": user.Username,    # Menggunakan Username atau nama pengguna yang sesuai
        "token": access_token     # Menambahkan token akses
    }

    # Kembalikan respons dengan create_response untuk 200
    response = create_response(
        status_code=200,
        message="success",
        data=login_result
    )

    # Ganti kunci "data" menjadi "loginResult"
    if "data" in response:
        response["loginResult"] = response.pop("data")

    return response


# =======================
# User Notes Routes
# =======================
@router.get("/user/notes", response_model=UserNotesResponse)
async def get_user_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Query untuk mendapatkan notes dan ingredients yang terkait
    notes_query = (
        db.query(Notes, Ingredient)
        .join(Ingredient, Notes.id_ingredients == Ingredient.Id_Ingredients)
        .filter(Notes.users_id == current_user.Users_ID)
        .all()
    )

    # Jika tidak ada data ditemukan, kirimkan respons tanpa 'data' (tidak mengirim array kosong)
    if not notes_query:
        response = create_response(
            status_code=404,
            message="No notes found for user",
            data=None  # Tidak ada data yang perlu dikembalikan
        )
        return JSONResponse(status_code=404, content=response)

    # Menyusun data respons sesuai dengan format yang diharapkan oleh Pydantic schema
    response_data = [
        NoteDetail(
            id=notes.id_ingredients,
            name=str(ingredient.nama),
            rating=str(ingredient.rating),  # Pastikan konversi tipe yang tepat
            category=str(ingredient.kategoriidn),
            preference=notes.notes if notes.notes else None,
        ).dict()
        for notes, ingredient in notes_query
    ]

    # Mengembalikan respons sukses dengan data
    response = create_response(
        status_code=200,
        message="User notes fetched successfully",
        data=response_data  # Return the list of NoteDetail objects
    )
    return JSONResponse(status_code=200, content=response)


@router.post("/user/notes")
async def add_user_note(
    request: AddNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Validasi preference
    if request.preference not in ["Suka", "Tidak Suka"]:
        # Menggunakan create_response untuk mengatur respons kesalahan
        response = create_response(
            status_code=400,
            message="Preference must be 'Suka' or 'Tidak Suka'",
            data=None
        )
        return JSONResponse(status_code=400, content=response)

    # Cek apakah ingredient dengan Id_Ingredients ada
    ingredient = db.query(Ingredient).filter(Ingredient.Id_Ingredients == request.Id_Ingredients).first()
    if not ingredient:
        # Menggunakan create_response untuk mengatur respons kesalahan
        response = create_response(
            status_code=404,
            message="Ingredient not found",
            data=None
        )
        return JSONResponse(status_code=404, content=response)

    # Cek apakah catatan sudah ada
    existing_note = db.query(Notes).filter(
        Notes.users_id == current_user.Users_ID,
        Notes.id_ingredients == request.Id_Ingredients
    ).first()
    if existing_note:
        # Menggunakan create_response untuk mengatur respons kesalahan
        response = create_response(
            status_code=400,
            message="Note for this ingredient already exists",
            data=None
        )
        return JSONResponse(status_code=400, content=response)

    # Tambahkan catatan baru
    new_note = Notes(
        users_id=current_user.Users_ID,
        id_ingredients=request.Id_Ingredients,
        notes=request.preference,
    )
    db.add(new_note)
    db.commit()

    # Menggunakan create_response untuk membuat respons sukses
    response = create_response(
        status_code=201,
        message=f"Ingredient with Id_Ingredients {request.Id_Ingredients} added to {request.preference} list",
        data=None
    )
    return JSONResponse(status_code=201, content=response)


@router.delete("/user/notes")
async def remove_user_note(
    request: AddNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Menghapus catatan ingredient dari tabel notes.
    """
    # Cari catatan yang sesuai
    note = db.query(Notes).filter(
        Notes.users_id == current_user.Users_ID,
        Notes.id_ingredients == request.Id_Ingredients
    ).first()
    if not note:
        # Menggunakan create_response untuk mengatur respons kesalahan
        response = create_response(
            status_code=404,
            message="Note not found",
            data=None
        )
        return JSONResponse(status_code=404, content=response)

    # Hapus catatan
    db.delete(note)
    db.commit()

    # Menggunakan create_response untuk membuat respons sukses
    response = create_response(
        status_code=200,
        message=f"Ingredient with Id_Ingredients {request.Id_Ingredients} removed from notes",
        data=None
    )
    return JSONResponse(status_code=200, content=response)