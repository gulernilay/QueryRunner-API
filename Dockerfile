# Microsoft SQL Server ODBC Driver 18 kurulumu
FROM python:3.11-slim 

# Sistem paketlerini yükle
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https gcc unixodbc unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Ortam değişkenlerini ayarla
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Çalışma dizinini oluştur
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Varsayılan olarak uvicorn ile başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]