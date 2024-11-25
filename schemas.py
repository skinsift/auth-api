from pydantic import BaseModel, EmailStr, constr
from enum import Enum

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

class SkinTypeEnum(str, Enum):
    Berminyak = "Berminyak"
    Kering = "Kering"
    Sensitif = "Sensitif"
    Normal = "Normal"

class UpdateSkinType(BaseModel):
    Users_ID: str
    jenis_kulit: SkinTypeEnum 

    class Config:
        from_attributes = True
        allow_population_by_field_name = True

# class NoteIngredients(BaseModel):
#     Jenis_Kulit: Optional[SkinType]
#     Good_Ingre: Optional[str]
#     Bad_Ingre: Optional[str]