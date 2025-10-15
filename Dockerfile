# escape=`
FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["powershell", "-NoLogo", "-ExecutionPolicy", "Bypass", "-Command"]

# ===============================
# 1️⃣ Chocolatey yükle
# ===============================
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# ===============================
# 2️⃣ Python 3.13 + VC++ Runtime
# ===============================
RUN choco install -y vcredist140; `
    choco install -y python --version=3.11.5 --install-arguments="'/PrependPath /Quiet'"

# ===============================
# 3️⃣ Yardımcı araçlar
# ===============================
RUN choco install -y git; `
    choco install -y 7zip; `
    choco install -y curl

# ===============================
# 4️⃣ Uygulama dosyalarını kopyala
# ===============================
WORKDIR C:\\app
COPY . C:\\app

# ===============================
# 5️⃣ Python bağımlılıklarını yükle
# ===============================
RUN if (Test-Path C:\app\requirements.txt) { `
        python -m pip install --no-cache-dir -r requirements.txt `
    } else { `
        Write-Host 'requirements.txt bulunamadı, atlanıyor.' `
    }

# ===============================
# 6️⃣ Ortam değişkenleri
# ===============================
ENV PYTHONUNBUFFERED=1

# ===============================
# 7️⃣ FastAPI portu
# ===============================
EXPOSE 8000

ENV PYTHONUTF8=1

# ===============================
# 8️⃣ Çalıştırma komutu
# ===============================
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===============================
# 9️⃣ SQL Server ODBC Driver 18
# ===============================
#RUN powershell -NoLogo -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/?linkid=2156821' -OutFile 'msodbcsql17.msi'; Start-Process msiexec.exe -ArgumentList '/i msodbcsql17.msi /quiet /norestart IACCEPTMSODBCSQLLICENSETERMS=YES' -Wait; Remove-Item msodbcsql17.msi -Force"