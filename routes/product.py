from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from schemas import search_products, ProductResponse, ProductDetailResponse
from database import get_db
from models import Products

router = APIRouter(prefix="/products", tags=["Products"])

# === Schemas ===
class ProductResponse(BaseModel):
    id: int
    nama_product: str
    merk: str
    deskripsi: Optional[str]
    nama_gambar: Optional[str]

    class Config:
        orm_mode = True

# === Endpoint ===
@router.get("/product", response_model=List[ProductResponse])
async def get_products(
    kategori: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    jenis_kulit: Optional[str] = Query(None, description="Filter berdasarkan jenis kulit"),
    search: Optional[str] = Query(None, description="Cari berdasarkan nama atau merk produk"),
    db: Session = Depends(get_db),
):
    """
    Mendapatkan daftar produk skincare berdasarkan filter kategori, jenis kulit, atau pencarian nama/merk.
    """
    query = db.query(Products)

    # Filter berdasarkan kategori
    if kategori:
        query = query.filter(Products.kategori.ilike(f"%{kategori}%"))

    # Filter berdasarkan jenis kulit
    if jenis_kulit:
        query = query.filter(Products.jenis_kulit.ilike(f"%{jenis_kulit}%"))

    # Pencarian nama atau merk produk
    if search:
        query = query.filter(
            (Products.nama_product.ilike(f"%{search}%")) |
            (Products.merk.ilike(f"%{search}%"))
        )

    products = query.all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products
