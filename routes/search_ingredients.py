import mysql.connector
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from schemas import search_ingredients, IngredientResponse, IngredientDetailResponse
from models import Ingredient
from database import get_db
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

# Konfigurasi koneksi database
db_config = {
    'host': 'localhost',
    'user': 'root',  # Ganti dengan username MySQL Anda
    'password': '',  # Ganti dengan password MySQL Anda
    'database': 'skinsift_app'  # Ganti dengan nama database Anda
}

@router.get("/search/ingredients", response_model=List[IngredientResponse])
async def get_all_ingredients():
    """Endpoint untuk mendapatkan seluruh data dari tabel ingredients."""
    query = "SELECT * FROM ingredients"

    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()

                response = [
                    IngredientResponse(
                        Id_Ingredients=row[0],
                        nama=row[1],
                        rating=row[2],
                        deskripsiidn=row[3],
                        benefitidn=row[4],
                        kategoriidn=row[5],
                        keyidn=row[6]
                    )
                    for row in result
                ]

                return response

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {str(e)}")

@router.post("/search/ingredients", response_model=List[IngredientResponse])
async def search_ingredients(request: search_ingredients):
    """Endpoint untuk mencari data ingredients berdasarkan filter."""
    nama = request.nama
    rating = request.rating
    benefitidn = request.benefitidn
    kategoriidn = request.kategoriidn

    query = "SELECT * FROM ingredients WHERE 1=1"
    params = []

    if nama:
        query += " AND nama = %s"
        params.append(nama)
    if rating:
        query += " AND rating = %s"
        params.append(rating)
    if benefitidn:
        query += " AND (benefitidn IS NOT NULL AND benefitidn LIKE %s)"
        params.append(f"%{benefitidn}%")
    if kategoriidn:
        query += " AND (kategoriidn IS NOT NULL AND kategoriidn LIKE %s)"
        params.append(f"%{kategoriidn}%")

    logging.debug(f"Final Query: {query}")
    logging.debug(f"Parameters: {params}")

    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                result = cursor.fetchall()

                response = [
                    IngredientResponse(
                        Id_Ingredients=row[0],
                        nama=row[1],
                        rating=row[2],
                        deskripsiidn=row[3],
                        benefitidn=row[4],
                        kategoriidn=row[5],
                        keyidn=row[6]
                    )
                    for row in result
                ]

                return response

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {str(e)}")

# API Route
@router.get("/filter-ingredients")
def get_filtered_ingredients(
    db: Session = Depends(get_db),
):
    # Fetch distinct values for each column
    ratings = db.query(Ingredient.rating).distinct().all()
    raw_benefits = db.query(Ingredient.benefitidn).distinct().all()
    # raw_categories = db.query(Ingredient.kategoriidn).distinct().all()

    # Process multivalued fields for benefits and categories
    benefits = set()
    for benefit in raw_benefits:
        if benefit[0]:  # Check if value is not None
            benefits.update(map(str.strip, benefit[0].split(",")))

    # categories = set()
    # for category in raw_categories:
    #     if category[0]:  # Check if value is not None
    #         categories.update(map(str.strip, category[0].split(",")))

    # Format the results into the desired response structure
    response = [
        {"rating": [r[0] for r in ratings if r[0]]},  # Ensure no None values
        {"benefitidn": list(benefits)},
        # {"kategoriidn": list(categories)},
    ]

    return response

@router.get("/ingredient/detail/{id_ingredient}", response_model=IngredientDetailResponse)
async def get_ingredient_detail(id_ingredient: int):
    """
    Endpoint untuk mendapatkan detail ingredient berdasarkan ID.
    """
    query = "SELECT * FROM ingredients WHERE Id_Ingredients = %s"
    
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (id_ingredient,))
                result = cursor.fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="Ingredient not found")

                # Format response
                response = IngredientDetailResponse(
                    Id_Ingredients=result[0],
                    nama=result[1],
                    rating=result[2],
                    deskripsiidn=result[3],
                    benefitidn=result[4],
                    kategoriidn=result[5],
                    keyidn=result[6]
                )
                return response

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {str(e)}")
