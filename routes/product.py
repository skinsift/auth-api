from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import mysql.connector
from database import get_db
from schemas import ProductResponse, search_products, ProductDetailResponse
from models import Product
from utils import get_current_user,  create_response
from models import User
from fastapi.responses import JSONResponse
from sqlalchemy import or_

router = APIRouter()

# Base URL untuk Cloud Bucket
CLOUD_BUCKET_BASE_URL = "https://storage.googleapis.com/skinsift/products/"

# === Endpoint untuk mendapatkan seluruh data produk ===
@router.get("/product", response_model=Dict[str, Any])
async def get_all_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Ambil semua data dari tabel products
        products = db.query(Product).all()

        if not products:
            # Kembalikan respons 404 jika tidak ada produk
            return JSONResponse(
                status_code=404,
                content=create_response(404, "No products found")
            )

        # Format response menggunakan list comprehension
        response = [
            ProductResponse(
                Id_Products=product.Id_Products,
                nama_product=product.nama_product,
                merk=product.merk,
                deskripsi=product.deskripsi,
                url_gambar=f"{CLOUD_BUCKET_BASE_URL}{product.nama_gambar}" if product.nama_gambar else None
            ).dict()  # Convert to dict for JSON serialization
            for product in products
        ]

        # Buat respons dasar
        base_response = create_response(200, "Products fetched successfully", response)

        # Sesuaikan nama kunci "list" menjadi "Productlist" jika ada
        if "list" in base_response:
            base_response["Productlist"] = base_response.pop("list")

        # Kembalikan respons
        return JSONResponse(
            status_code=200,
            content=base_response
        )

    except Exception as e:
        # Kembalikan respons error 500 jika terjadi kesalahan
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )


# === Endpoint untuk mencari produk berdasarkan filter ===
@router.post("/product/search", response_model=Dict[str, Any])
async def search_products(
    request: search_products,  # Pastikan ini adalah Pydantic model
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Membuat filter dinamis untuk query
        filters = []

        # Filter untuk nama produk dan merek dengan wildcard
        if request.nama_atau_merk:
            filters.append(
                or_(
                    Product.nama_product.ilike(f"%{request.nama_atau_merk}%"),
                    Product.merk.ilike(f"%{request.nama_atau_merk}%")
                )
            )


        if request.kategori:
            filters.append(or_(*[Product.kategori == kat for kat in request.kategori]))

        if request.jenis_kulit:
            filters.append(or_(*[Product.jenis_kulit == jk for jk in request.jenis_kulit]))

        # Eksekusi query dengan filter
        products = db.query(Product).filter(*filters).all()

        if not products:
            # Kembalikan respons 404 jika tidak ada produk yang cocok
            return JSONResponse(
                status_code=404,
                content=create_response(404, "No products found")
            )

        # Format response menggunakan list comprehension
        response = [
            ProductResponse(
                Id_Products=product.Id_Products,
                nama_product=product.nama_product,
                merk=product.merk,
                deskripsi=product.deskripsi,
                url_gambar=f"{CLOUD_BUCKET_BASE_URL}{product.nama_gambar}" if product.nama_gambar else None
            ).dict()  # Convert to dict for JSON serialization
            for product in products
        ]

        # Buat respons dasar
        base_response = create_response(200, "Products fetched successfully", response)

        # Sesuaikan nama kunci "list" menjadi "Productlist" jika ada
        if "list" in base_response:
            base_response["Productlist"] = base_response.pop("list")

        # Kembalikan respons
        return JSONResponse(
            status_code=200,
            content=base_response
        )

    except Exception as e:
        # Kembalikan respons error 500 jika terjadi kesalahan
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}")
        )

# === Endpoint untuk mendapatkan detail produk ===
@router.get("/product/detail/{id_product}", response_model=Dict[str, Any])
async def get_product_detail(
    id_product: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Ambil data produk berdasarkan ID
        product = db.query(Product).filter(Product.Id_Products == id_product).first()

        # Jika produk tidak ditemukan, lemparkan exception
        if not product:
            return JSONResponse(
                status_code=404,
                content=create_response(404, "Product not found")
            )

        # Format response
        response = [
            ProductDetailResponse(
            Id_Products=product.Id_Products,
            nama_product=product.nama_product,
            merk=product.merk,
            jenis_product=product.jenis,
            kategori=product.kategori,
            jenis_kulit=product.jenis_kulit,
            url_gambar=f"{CLOUD_BUCKET_BASE_URL}{product.nama_gambar}" if product.nama_gambar else None,
            key_ingredients=product.key_ingredients,
            ingredients=product.ingredients,
            deskripsi=product.deskripsi,
            no_BPOM=product.no_BPOM,
            kegunaan=product.kegunaan
        ).dict()
            
        ]
        # Buat respons dasar
        base_response = create_response(200, "Products fetched successfully", response)

        # Sesuaikan nama kunci "list" menjadi "Productlist" jika ada
        if "list" in base_response:
            base_response["Productlist"] = base_response.pop("list")
        # Convert response to dict before returning
        return JSONResponse(
            status_code=200,
            content=base_response 
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"MySQL Error: {str(e)}")
        )

@router.get("/product/filter")
async def get_filtered_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Ambil nilai distinct untuk setiap kolom
        kategoris = db.query(Product.kategori).distinct().all()
        jenis_kulits = db.query(Product.jenis_kulit).distinct().all()

        # Format data hasil query
        data = [{
            "kategori": [k[0] for k in kategoris if k[0] is not None],
            "jenis_kulit": [j[0] for j in jenis_kulits if j[0] is not None],
        }]

        # Kembalikan respons sukses
        base_response = create_response(200, "Filters fetched successfully", data)

        # Sesuaikan nama kunci "list" menjadi "Productlist" jika ada
        if "list" in base_response:
            base_response["Productlist"] = base_response.pop("list")
        return JSONResponse(
            status_code=200,
            content=base_response
        )

    except Exception as e:
        # Tangani error dan kembalikan respons JSON
        return JSONResponse(
            status_code=500,
            content=create_response(500, f"Database Error: {str(e)}"),
        )
