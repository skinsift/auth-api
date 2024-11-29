import mysql.connector
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from schemas import search_ingredients

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

# Konfigurasi koneksi database
db_config = {
    'host': 'localhost',
    'user': 'root',  # Ganti dengan username MySQL Anda
    'password': '',  # Ganti dengan password MySQL Anda
    'database': 'skinsift_app'  # Ganti dengan nama database Anda
}

# Pydantic model untuk response
class IngredientResponse(BaseModel):
    Id_Ingredients: int
    nama: str
    rating: Optional[str]
    deskripsiidn: Optional[str]
    benefitidn: Optional[str]
    kategoriidn: Optional[str]
    keyidn: Optional[str]

@router.post("/search/ingredients", response_model=List[IngredientResponse])
async def search(request: search_ingredients):
    nama = request.nama
    benefitidn = request.benefitidn
    kategoriidn = request.kategoriidn

    # Query dasar
    query = "SELECT * FROM ingredients WHERE 1=1"
    params = []

    # Jika tidak ada filter, kembalikan semua data
    if not (nama or benefitidn or kategoriidn):
        logging.info("No filters applied. Returning all data.")

    # Jika ada filter, tambahkan ke query
    if nama:
        query += " AND nama = %s"
        params.append(nama)
    if benefitidn:
        query += " AND (benefitidn IS NOT NULL AND benefitidn LIKE %s)"
        params.append(f"%{benefitidn}%")
    if kategoriidn:
        query += " AND (kategoriidn IS NOT NULL AND kategoriidn LIKE %s)"
        params.append(f"%{kategoriidn}%")

    # Log query dan parameter
    logging.debug(f"Final Query: {query}")
    logging.debug(f"Parameters: {params}")

    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                result = cursor.fetchall()

                # Format response
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
