from pydantic import BaseModel, EmailStr, constr
from enum import Enum
from typing import Optional, List

class UserCreate(BaseModel):
    Username: constr(min_length=3, max_length=100)
    Password: constr(min_length=6)
    Email: EmailStr
    # Jenis_Kulit: str
    # Good_Ingre: str = None
    # Bad_Ingre: str = None

class LoginSchema(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

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
    preference: str

class UserNotesResponse(BaseModel):
    notes: List[NoteDetail]

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


# class SkinTypeEnum(str, Enum):
#     Berminyak = "Berminyak"
#     Kering = "Kering"
#     Sensitif = "Sensitif"
#     Normal = "Normal"

# class UpdateSkinType(BaseModel):
#     Users_ID: str
#     jenis_kulit: SkinTypeEnum 

#     class Config:
#         from_attributes = True
#         allow_population_by_field_name = True