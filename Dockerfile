# escape=`
FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["powershell", "-NoLogo", "-ExecutionPolicy", "Bypass", "-Command"]

# ===============================
# import Chocolatey 
# ===============================   
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# ===============================
# Python 3.13 + VC++ Runtime
# ===============================
RUN choco install -y vcredist140; `
    choco install -y python --version=3.11.5 --install-arguments="'/PrependPath /Quiet'"
# ===============================
# Install tools: git, 7zip, curl
# ===============================
RUN choco install -y git; `
    choco install -y 7zip; `
    choco install -y curl

# ===============================
# Copy application files
# ===============================
WORKDIR C:\\app
COPY . C:\\app

# ===============================
# Upload Python dependencies
# ===============================
RUN if (Test-Path C:\app\requirements.txt) { `
        python -m pip install --no-cache-dir -r requirements.txt `
    } else { `
        Write-Host 'requirements.txt bulunamadı, atlanıyor.' `
    }

# ===============================
#  Environment Variables
# ===============================
ENV PYTHONUNBUFFERED=1

# ===============================
#  FastAPI Port
# ===============================
EXPOSE 8000

ENV PYTHONUTF8=1

# ===============================
# Run the application
# ===============================
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===============================
#  SQL Server ODBC Driver 18
# ===============================
#RUN powershell -NoLogo -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/?linkid=2156821' -OutFile 'msodbcsql17.msi'; Start-Process msiexec.exe -ArgumentList '/i msodbcsql17.msi /quiet /norestart IACCEPTMSODBCSQLLICENSETERMS=YES' -Wait; Remove-Item msodbcsql17.msi -Force