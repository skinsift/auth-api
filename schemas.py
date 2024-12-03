from pydantic import BaseModel, EmailStr, constr, Field
from enum import Enum
from typing import Optional, List

class UserCreate(BaseModel):
    Username: str
    Password: str
    Email: str

class LoginSchema(BaseModel):
    username_or_email: str
    password: str

class LoginResult(BaseModel):
    userId: str
    name: str
    token: str

class LoginResponse(BaseModel):
    error: bool
    message: str
    loginResult: LoginResult

class DeleteAccountRequest(BaseModel):
    password: str

class UpdateAccountRequest(BaseModel):
    current_password: str = Field(..., description="Current password of the user")
    new_password: Optional[str] = Field(None, description="New password to set")
    new_email: Optional[str] = Field(None, description="New email to set")

class IngredientResponse(BaseModel):
    Id_Ingredients: int
    nama: str
    rating: Optional[str]
    benefitidn: Optional[str] = None

class search_ingredients(BaseModel):
    nama: Optional[str] = None
    rating: Optional[List[str]] = None
    benefitidn: Optional[List[str]] = None

class IngredientDetailResponse(BaseModel):
    Id_Ingredients: int
    nama: str
    rating: Optional[str]
    deskripsiidn: Optional[str]
    benefitidn: Optional[str]
    kategoriidn: Optional[str]
    keyidn: Optional[str]

class AddNoteRequest(BaseModel):
    Id_Ingredients: int
    preference: str  # "good" atau "bad"

class NoteDetail(BaseModel):
    id: int
    name: str
    rating: str
    category: str
    preference: Optional[str]

class UserNotesResponse(BaseModel):
    status_code: int
    message: str
    error: bool
    data: Optional[List[NoteDetail]] = None 

class ProductResponse(BaseModel):
    Id_Products: int
    nama_product: str
    merk: Optional[str]
    deskripsi: Optional[str]
    url_gambar: Optional[str]

class search_products(BaseModel):
    nama_atau_merk: Optional[str] = None
    kategori: Optional[List[str]] = None
    jenis_kulit: Optional[List[str]] = None

class ProductDetailResponse(BaseModel):
    Id_Products: int
    nama_product: str
    merk: Optional[str]
    jenis_product: Optional[str]
    kategori: Optional[str]
    jenis_kulit: Optional[str]
    url_gambar: Optional[str]
    key_ingredients: Optional[str]
    ingredients: Optional[str]
    deskripsi: Optional[str]
    no_BPOM: Optional[str]
    kegunaan: Optional[str]
