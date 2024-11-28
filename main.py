from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from utils import global_exception_handler, validation_exception_handler
from database import Base, engine
from routes import auth

app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# Buat tabel di database jika belum ada
Base.metadata.create_all(bind=engine)

# Tambahkan route autentikasi
app.include_router(auth.router)

# Tambahkan error handling
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
