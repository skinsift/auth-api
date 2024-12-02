import mysql.connector
import logging
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from schemas import search_ingredients, IngredientResponse, IngredientDetailResponse
from models import Ingredient
from database import get_db
from sqlalchemy.orm import Session
from utils import get_current_user, create_response
from models import User
from fastapi.responses import JSONResponse
from sqlalchemy import or_, and_

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

# Konfigurasi koneksi database
# db_config = {
#     'host': 'localhost',
#     'user': 'root',  # Ganti dengan username MySQL Anda
#     'password': '',  # Ganti dengan password MySQL Anda
#     'database': 'skinsift_app'  # Ganti dengan nama database Anda
# }

@router.get("/ingredient", response_model=Dict[str, Any])
async def get_all_ingredients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk mendapatkan seluruh data dari tabel ingredients.
    """
    try:
        # Ambil semua data dari tabel ingredients
        ingredients = db.query(Ingredient).all()
        if not ingredients:
            return JSONResponse(
                status_code=404,
                content=create_response(404, "No ingredients found")
            )

        # Format response menggunakan list comprehension
        response = [
            IngredientResponse(
                Id_Ingredients=ingredient.Id_Ingredients,
                nama=ingredient.nama,
                rating=ingredient.rating,
                benefitidn=ingredient.benefitidn,
            ).dict()
            for ingredient in ingredients
        ]

        # Panggil create_response dan ubah kunci 'list' menjadi 'Ingredientlist'
        base_response = create_response(200, "Ingredients fetched successfully", response)
        if "list" in base_response:
            base_response["Ingredientlist"] = base_response.pop("list")

        return JSONResponse(
            status_code=200,
            content=base_response
        )

    except Exception as e:
        # Tangani error lain dan kirimkan respons HTTP 500
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )

@router.post("/ingredient/search", response_model=Dict[str, Any])
async def search_ingredients(
    request: search_ingredients,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("Endpoint '/ingredient/search' was called")
    print("Request data:", request)
    
    try:
        # Membuat filter dinamis untuk query
        filters = []
        if request.nama:
            filters.append(Ingredient.nama.ilike(f"%{request.nama}%"))
        if request.rating:
            rating_filter = or_(*[Ingredient.rating == rat for rat in request.rating])
            filters.append(rating_filter)

        # Filter untuk benefitidn menggunakan and_
        if request.benefitidn:
            benefit_filters = and_(
                *[Ingredient.benefitidn.ilike(f"%{ben}%") for ben in request.benefitidn]
            )
            filters.append(benefit_filters)

        # Eksekusi query dengan filter
        ingredients = db.query(Ingredient).filter(*filters).all()
        if not ingredients:
            print("No ingredients found")
            return JSONResponse(
                status_code=404,
                content=create_response(404, "No ingredients found")
            )

        # Format response
        response = [
            IngredientResponse(
                Id_Ingredients=ingredient.Id_Ingredients,
                nama=ingredient.nama,
                rating=ingredient.rating,
                benefitidn=ingredient.benefitidn,
                kategoriidn=ingredient.kategoriidn,
                keyidn=ingredient.keyidn,
            ).dict()
            for ingredient in ingredients
        ]

        # Panggil create_response dan ubah kunci 'list' menjadi 'Ingredientlist'
        base_response = create_response(200, "Ingredients fetched successfully", response)
        if "list" in base_response:
            base_response["Ingredientlist"] = base_response.pop("list")

        print("Response sent:", base_response)

        return JSONResponse(
            status_code=200,
            content=base_response
        )

    except Exception as e:
        print("Error:", str(e))
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )


@router.get("/ingredient/detail/{id_ingredient}", response_model=Dict[str, Any])
async def get_ingredient_detail(
    id_ingredient: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk mendapatkan detail ingredient berdasarkan ID.
    """
    try:
        # Query data ingredient berdasarkan ID
        ingredient = db.query(Ingredient).filter(Ingredient.Id_Ingredients == id_ingredient).first()
        
        # Jika tidak ditemukan
        if not ingredient:
            return JSONResponse(
                status_code=404,
                content=create_response(404, "Ingredient not found")
            )

        # Format response
        response = {
            "Id_Ingredients": ingredient.Id_Ingredients,
            "nama": ingredient.nama,
            "rating": ingredient.rating,
            "deskripsiidn": ingredient.deskripsiidn,
            "benefitidn": ingredient.benefitidn,
            "kategoriidn": ingredient.kategoriidn,
            "keyidn": ingredient.keyidn,
        }

        return JSONResponse(
            status_code=200,
            content=create_response(200, "Ingredient details fetched successfully", response)
        )

    except Exception as e:
        # Tangani error lain
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )

@router.get("/ingredient/filter")
async def get_filtered_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint untuk mendapatkan nilai distinct dari kolom rating dan benefitidn pada tabel ingredients.
    """
    try:
        # Ambil nilai distinct untuk setiap kolom
        ratings = db.query(Ingredient.rating).distinct().all()
        raw_benefits = db.query(Ingredient.benefitidn).distinct().all()

        # Format data benefits
        benefits = set()
        for benefit in raw_benefits:
            if benefit[0]:  # Pastikan nilai tidak None
                benefits.update(map(str.strip, benefit[0].split(",")))

        # Format respons
        data = {
            "rating": [r[0] for r in ratings if r[0] is not None],
            "benefitidn": list(benefits),
        }

        return JSONResponse(
            status_code=200,
            content=create_response(200, "Filtered data fetched successfully", data)
        )

    except Exception as e:
        # Tangani error dan kembalikan respons JSON
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )
