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
