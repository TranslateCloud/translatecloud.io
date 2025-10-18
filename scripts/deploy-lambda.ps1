# ============================================
# DEPLOY BACKEND API TO AWS LAMBDA
# ============================================

cd backend

Write-Host "Empaquetando Lambda..." -ForegroundColor Cyan

# Crear directorio temporal
New-Item -ItemType Directory -Path "lambda-package" -Force | Out-Null

# Copiar código fuente
Copy-Item -Path "src" -Destination "lambda-package/src" -Recurse -Force
Copy-Item -Path "lambda_handler.py" -Destination "lambda-package/" -Force

# Instalar dependencias en el paquete
pip install -r requirements.txt -t lambda-package/ --platform manylinux2014_x86_64 --only-binary=:all:

Write-Host "Creando ZIP..." -ForegroundColor Cyan
cd lambda-package
Compress-Archive -Path * -DestinationPath ../translatecloud-api.zip -Force
cd ..

Write-Host ""
Write-Host "Paquete creado: translatecloud-api.zip" -ForegroundColor Green
Write-Host "Tamaño: $((Get-Item translatecloud-api.zip).Length / 1MB) MB" -ForegroundColor Yellow
Write-Host ""

# Limpiar
Remove-Item -Path "lambda-package" -Recurse -Force

Write-Host "Listo para deployment manual o automatizado" -ForegroundColor Green