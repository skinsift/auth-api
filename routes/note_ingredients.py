from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Ingredient

# Router Initialization
router = APIRouter()

