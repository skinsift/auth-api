from fastapi import APIRouter, Depends, HTTPException, Form, Body
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginSchema, LoginResult, LoginResponse, AddNoteRequest, NoteDetail, UserNotesResponse, IngredientDetailResponse, DeleteAccountRequest, UpdateAccountRequest, DeleteNoteRequest
from crud import create_user, get_user_by_email, get_user_by_username
from database import get_db
from utils import verify_password, create_access_token, hash_password, generate_unique_id, get_current_user, create_response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User, Ingredient, Notes
from dotenv import load_dotenv
import os, re
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

    # Validasi tambahan untuk format Username dan Password
    username_regex = r"^[a-zA-Z0-9_]+$"  # Hanya huruf, angka, dan underscore
    password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$"  # Min 6 karakter, ada huruf & angka

    error_messages = []

    # Validasi panjang Username tidak boleh kurang dari 3 karakter
    if len(user.Username) < 3:
        error_messages.append({
            "type": "string_too_short",
            "loc": ["body", "Username"],
            "msg": "Username must be at least 3 characters long.",
            "input": user.Username
        })

    # Validasi format Username
    if not re.match(username_regex, user.Username):
        error_messages.append({
            "type": "string_pattern_mismatch",
            "loc": ["body", "Username"],
            "msg": "Username can only contain letters, numbers, and underscores.",
            "input": user.Username
        })

    # Validasi panjang Password
    if len(user.Password) < 6:
        error_messages.append({
            "type": "string_too_short",
            "loc": ["body", "Password"],
            "msg": "Password should have at least 6 characters",
            "input": user.Password
        })
        
    # Validasi format Password
    elif not re.match(password_regex, user.Password):
        error_messages.append({
            "type": "string_pattern_mismatch",
            "loc": ["body", "Password"],
            "msg": "Password must be at least 6 characters long and include both letters and numbers.",
            "input": user.Password
        })

    # Periksa apakah email atau username sudah terdaftar
    existing_email = get_user_by_email(db, user.Email)
    existing_username = get_user_by_username(db, user.Username)

    if existing_email:
        error_messages.append({
            "type": "value_error.email_taken",
            "loc": ["body", "Email"],
            "msg": "Email or Username is already registered.",
            "input": user.Email
        })
    if existing_username:
        error_messages.append({
            "type": "value_error.username_taken",
            "loc": ["body", "Username"],
            "msg": "Email or Username is already registered.",
            "input": user.Username
        })

    # Jika ada kesalahan, kembalikan dengan status 422
    if error_messages:
        return create_response(
            status_code=422,
            message="Registration failed due to errors",
            data={"errors": [{"msg": e["msg"]} for e in error_messages]},  # Hanya kirimkan pesan kesalahan yang relevan
        )

    # Hash password pengguna
    hashed_password = hash_password(user.Password)

    # Buat pengguna baru
    new_user = create_user(db, {
        "Users_ID": generate_unique_id(),
        "Username": user.Username,
        "Password": hashed_password,
        "Email": user.Email,
    })

    # Respons sukses
    return create_response(
        status_code=201,
        message="User registered successfully",
        data={
            "user_id": new_user.Users_ID,
            "username": new_user.Username,
            "email": new_user.Email,
            "created_at": new_user.created_at,  # Sertakan waktu pembuatan
        },
    )


from fastapi.responses import JSONResponse
from fastapi import HTTPException

@router.post("/login", response_model=LoginResponse)
async def login_user(payload: LoginSchema, db: Session = Depends(get_db)):
    identifier = payload.username_or_email
    user = None

    # Mengidentifikasi apakah menggunakan email atau username
    if "@" in identifier:
        user = get_user_by_email(db, identifier)  # Mencari user berdasarkan email
    else:
        user = get_user_by_username(db, identifier)  # Mencari user berdasarkan username

    # Skema 1: Username tidak ditemukan
    if not user:
        # Gunakan create_response untuk error 404, pastikan loginResult ada sebagai None
        response_data = create_response(
            status_code=404,
            message="Username not found",
            data=None,
            data_key="loginResult"
        )

        # Menggunakan JSONResponse dengan format dict() untuk memastikan struktur valid
        return JSONResponse(
            status_code=response_data["status_code"],
            content=dict(response_data, loginResult=None)  # Pastikan loginResult ada meski None
        )

    # Skema 2: Password salah
    if not verify_password(payload.password, user.Password):  # Verifikasi password
        # Gunakan create_response untuk error 400, pastikan loginResult ada sebagai None
        response_data = create_response(
            status_code=400,
            message="Incorrect password",
            data=None,
            data_key="loginResult"
        )

        # Menggunakan JSONResponse dengan format dict() untuk memastikan struktur valid
        return JSONResponse(
            status_code=response_data["status_code"],
            content=dict(response_data, loginResult=None)  # Pastikan loginResult ada meski None
        )

    # Skema 3: Berhasil login
    access_token = create_access_token(data={"user_id": user.Users_ID})  # Membuat token akses

    # Struktur loginResult yang sesuai
    login_result = {
        "userId": user.Users_ID,
        "name": user.Username,
        "token": access_token
    }

    # Gunakan create_response untuk sukses, pastikan loginResult ada dalam data
    response_data = create_response(
        status_code=200,
        message="Login successful",
        data=login_result,  # Menambahkan data loginResult
        data_key="loginResult"
    )

    # Menggunakan JSONResponse dengan format dict() untuk memastikan struktur valid
    return JSONResponse(
        status_code=response_data["status_code"],
        content=dict(response_data, loginResult=login_result)  # Menambahkan loginResult yang benar
    )


@router.put("/update-account")
def update_account(
    payload: Dict[str, Any] = Body(..., description="Payload for account update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    new_email = payload.get("new_email")

    # Validasi keberadaan current_password
    if not current_password:
        return JSONResponse(
            status_code=400,
            content=create_response(
                status_code=400,
                message="Field 'current_password' is required."
            )
        )

    # Validasi password lama
    if not verify_password(current_password, current_user.Password):
        return JSONResponse(
            status_code=403,
            content=create_response(
                status_code=403,
                message="Invalid current password."
            )
        )

    # Pastikan setidaknya satu dari new_password atau new_email diberikan
    if not new_password and not new_email:
        return JSONResponse(
            status_code=400,
            content=create_response(
                status_code=400,
                message="Please provide at least one field to update: 'new_password' or 'new_email'."
            )
        )

    # Perbarui password jika diberikan
    if new_password:
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$"
        if not re.match(password_regex, new_password):
            return JSONResponse(
                status_code=400,
                content=create_response(
                    status_code=400,
                    message="Password must be at least 6 characters long and include both letters and numbers."
                )
            )
        current_user.Password = hash_password(new_password)

    # Perbarui email jika diberikan
    if new_email:
        if db.query(User).filter(User.Email == new_email).first():
            return JSONResponse(
                status_code=400,
                content=create_response(
                    status_code=400,
                    message="Email already registered."
                )
            )
        current_user.Email = new_email

    # Commit perubahan
    db.commit()
    db.refresh(current_user)

    return JSONResponse(
        status_code=200,
        content=create_response(
            status_code=200,
            message="Account updated successfully.",
            data={
                "user_id": current_user.Users_ID,
                "username": current_user.Username,
                "email": current_user.Email,
            }
        )
    )

@router.delete("/delete-account")
def delete_account(
    request: DeleteAccountRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Cek apakah pengguna ada
    user = db.query(User).filter(User.Users_ID == current_user.Users_ID).first()
    if not user:
        return create_response(
            status_code=404,
            message="User not found",
        )

    # Validasi password
    if not verify_password(request.password, user.Password):
        return create_response(
            status_code=403,
            message="Invalid password",
        )

    # Hapus akun
    db.delete(user)
    db.commit()

    return create_response(
        status_code=200,
        message="Account deleted successfully",
        data={"user_id": user.Users_ID},  # Mengembalikan user ID yang benar
    )


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
async def remove_note_by_id(
    request: DeleteNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Cari catatan berdasarkan id_ingredients dan current_user
    note = db.query(Notes).filter(
        Notes.id_ingredients == request.Id_Ingredients,
        Notes.users_id == current_user.Users_ID
    ).first()

    if not note:
        # Jika catatan tidak ditemukan, kirim respons kesalahan
        response = create_response(
            status_code=404,
            message=f"Ingredient with Id_Ingredients {request.Id_Ingredients} not found",
            data=None
        )
        return JSONResponse(status_code=404, content=response)

    # Hapus catatan
    db.delete(note)
    db.commit()

    # Kirim respons sukses
    response = create_response(
        status_code=200,
        message=f"Ingredient with Id_Ingredients {request.Id_Ingredients} removed from notes",
        data=None
    )
    return JSONResponse(status_code=200, content=response)
