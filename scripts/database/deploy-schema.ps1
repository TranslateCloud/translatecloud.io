# ============================================
# DEPLOY DATABASE SCHEMA TO RDS
# ============================================
# Uso: .\scripts\database\deploy-schema.ps1
# ============================================

param(
    [string]$Environment = "prod"
)

# Agregar PostgreSQL al PATH
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# Verificar que psql esta disponible
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: psql no encontrado" -ForegroundColor Red
    Write-Host "Instala PostgreSQL client o verifica el PATH" -ForegroundColor Yellow
    exit 1
}

# Configuracion
$DB_HOST = "translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com"
$DB_PORT = "5432"
$DB_USER = "postgres"
$DB_NAME = "postgres"
$DB_PASSWORD = "TranslateCloud2025!"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DEPLOYING SCHEMA TO RDS ($Environment)" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configurar password
$env:PGPASSWORD = $DB_PASSWORD

# Ejecutar schema
Write-Host "Ejecutando schema..." -ForegroundColor Cyan
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f scripts/database/schema.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Schema desplegado correctamente" -ForegroundColor Green
    
    # Verificar tablas
    Write-Host ""
    Write-Host "Verificando tablas creadas..." -ForegroundColor Cyan
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"
} else {
    Write-Host ""
    Write-Host "ERROR al desplegar schema" -ForegroundColor Red
}

# Limpiar password
Remove-Item Env:\PGPASSWORD

Write-Host ""
Write-Host "Deployment completado" -ForegroundColor Green
