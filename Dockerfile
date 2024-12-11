# Gunakan Python image resmi
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Salin file ke container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (standar Cloud Run)
EXPOSE 8080

# Jalankan aplikasi
CMD ["python", "app.py"]
