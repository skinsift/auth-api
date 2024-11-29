from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
# from base import Base  # Ganti `base` dengan file tempat Base Anda didefinisikan

class Notes(Base):
    __tablename__ = "notes"

    id_notes = Column(Integer, primary_key=True, autoincrement=True, index=True)
    users_id = Column(String(16), ForeignKey("User.Users_ID"), nullable=False)
    id_ingredients = Column(Integer, ForeignKey("ingredients.Id_Ingredients"), nullable=False)
    notes = Column(Enum("Suka", "Tidak Suka", name="note_enum"), nullable=False)

    # Relationships (Opsional, untuk navigasi data)
    user = relationship("User", back_populates="notes")
    ingredient = relationship("Ingredient", back_populates="notes")

class User(Base):
    __tablename__ = "User"

    Users_ID = Column(String(16), primary_key=True, index=True)
    Username = Column(String(1000), unique=True, nullable=False)
    Password = Column(String(1000), nullable=False)
    Email = Column(String(1000), unique=True, nullable=False)

    # Relationship
    notes = relationship("Notes", back_populates="user")

class Ingredient(Base):
    __tablename__ = "ingredients"  # Nama tabel di database

    Id_Ingredients = Column(Integer, primary_key=True, index=True)
    nama = Column(String, index=True)
    rating = Column(String, nullable=True)
    deskripsiidn = Column(String, nullable=True)
    benefitidn = Column(String, nullable=True)
    kategoriidn = Column(String, nullable=True)
    keyidn = Column(String, nullable=True)

    # Relationship
    notes = relationship("Notes", back_populates="ingredient")