from sqlalchemy import Column, String, Enum
from database import Base

class User(Base):
    __tablename__ = "User"

    Users_ID = Column(String(16), primary_key=True, index=True)
    Username = Column(String(1000), unique=True, nullable=False)
    Password = Column(String(1000), nullable=False)
    Email = Column(String(1000), unique=True, nullable=False)
    Good_Ingre = Column(String(1000), nullable=True)
    Bad_Ingre = Column(String(1000), nullable=True)

from sqlalchemy import Column, Integer, String
from database import Base  # Pastikan ini adalah Base yang Anda definisikan

class Ingredient(Base):
    __tablename__ = "ingredients"  # Nama tabel di database

    Id_Ingredients = Column(Integer, primary_key=True, index=True)
    nama = Column(String, index=True)
    rating = Column(String, nullable=True)
    deskripsiidn = Column(String, nullable=True)
    benefitidn = Column(String, nullable=True)
    kategoriidn = Column(String, nullable=True)
    keyidn = Column(String, nullable=True)
