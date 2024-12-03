import uvicorn  # Tambahkan impor untuk Uvicorn
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.engine import Connection
from sqlalchemy import text
from utils import global_exception_handler, validation_exception_handler
from database import Base, engine
from routes import auth, search_ingredients, product
# from connect import get_db_connection

# Inisialisasi aplikasi FastAPI
app = FastAPI()

# Endpoint untuk menguji koneksi database
# @app.get("/test-db")
# async def test_db(connection: Connection = Depends(get_db_connection)):
#     try:
#         # Cek apakah koneksi berhasil dan jalankan query
#         result = connection.execute(text("SELECT 1")).fetchone()
        
#         # Jika hasil query ada, kembalikan hasilnya
#         if result:
#             return {"status": "success", "message": "Koneksi berhasil", "result": result[0]}
#         else:
#             return {"status": "error", "message": "Tidak ada data ditemukan"}
#     except Exception as e:
#         # Tangani error dan beri tahu lebih jelas
#         return {"status": "error", "message": f"Koneksi gagal: {str(e)}"}


# Membuat tabel jika belum ada
Base.metadata.create_all(bind=engine)

# Menyertakan router dari modul lain
app.include_router(auth.router)
app.include_router(search_ingredients.router)
app.include_router(product.router)

# Menambahkan penanganan error kustom
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Menjalankan server saat file dieksekusi langsung
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
