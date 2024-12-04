# Gunakan image Python slim
FROM python:3.10-slim

# Set environment variable untuk Python
ENV PYTHONUNBUFFERED True

# Set working directory
WORKDIR /app

# Salin file proyek ke dalam container
COPY . /app

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt
# Tentukan perintah untuk menjalankan aplikasi
CMD ["fastapi", "dev", "main.py"]
