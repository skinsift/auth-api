from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    Username: constr(min_length=3, max_length=100)
    Password: constr(min_length=6)
    Email: EmailStr
    Jenis_Kulit: str
    Good_Ingre: str = None
    Bad_Ingre: str = None

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str