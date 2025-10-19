# DeepL API Setup Guide

## 🔑 Obtener DeepL API Key (GRATIS - 500,000 caracteres/mes)

### Paso 1: Crear Cuenta
1. Ir a: https://www.deepl.com/pro-api
2. Click en "Sign up for free"
3. Llenar formulario:
   - Email: v.posadasbiazutti@gmail.com
   - Password: (tu password segura)
   - Seleccionar "DeepL API Free"

### Paso 2: Verificar Email
1. Revisar email de verificación
2. Click en link de activación
3. Confirmar cuenta

### Paso 3: Obtener API Key
1. Login en https://www.deepl.com/account/summary
2. Ir a "Account" → "API Keys"
3. Copiar tu API key (formato: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx`)

### Paso 4: Configurar en TranslateCloud

#### Opción A: Variable de Entorno (Recomendado para desarrollo)
```bash
# Windows PowerShell
$env:DEEPL_API_KEY="tu-api-key-aqui"

# Windows CMD
set DEEPL_API_KEY=tu-api-key-aqui

# Linux/Mac
export DEEPL_API_KEY="tu-api-key-aqui"
```

#### Opción B: Archivo .env
Crear archivo `.env` en la raíz del proyecto:
```env
DEEPL_API_KEY=tu-api-key-aqui
JWT_SECRET_KEY=cambiar-en-produccion-por-algo-muy-seguro
```

#### Opción C: AWS Secrets Manager (Para producción)
```bash
# Añadir DeepL API key al secreto existente
aws secretsmanager update-secret \
  --secret-id prod/translatecloud/db \
  --secret-string '{
    "host": "translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com",
    "port": 5432,
    "database": "postgres",
    "username": "translatecloud_api",
    "password": "ApiUser2025Secure!",
    "deepl_api_key": "tu-api-key-aqui"
  }' \
  --region eu-west-1
```

Luego actualizar `backend/src/config/database.py` para leer la key:
```python
# En get_secret():
creds = json.loads(response['SecretString'])
deepl_key = creds.get('deepl_api_key')
```

## ✅ Verificar Configuración

### Test Local
```bash
# Ejecutar script de test
python test_translation_system.py
```

Deberías ver:
```
✓ DeepL available: True
✓ Primary provider: deepl
```

### Test en Lambda (después de deploy)
```bash
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/translation/status
```

Respuesta esperada:
```json
{
  "deepl_available": true,
  "marian_available": false,
  "primary_provider": "deepl",
  "status": "operational"
}
```

## 📊 Monitorear Uso

### Ver uso actual
```bash
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/translation/usage
```

Respuesta:
```json
{
  "provider": "deepl",
  "characters_used": 12450,
  "characters_limit": 500000,
  "percentage_used": 2.49,
  "available": true
}
```

## 💡 Límites del Plan Gratuito

- **500,000 caracteres/mes**
- ~250 páginas web (promedio 2000 palabras/página)
- Renueva automáticamente cada mes
- Sin tarjeta de crédito requerida

## 🚀 Upgrade a Plan Pago (Opcional)

Si necesitas más caracteres:
- **DeepL API Pro**: $5.49/mes por 500k chars adicionales
- **DeepL API Business**: Planes personalizados

## ⚠️ Seguridad

**NUNCA** commitear la API key a git:
```bash
# .gitignore ya incluye:
.env
*.env
```

**Rotar la key** cada 90 días por seguridad.

## 🔧 Troubleshooting

### Error: "Invalid authentication"
- Verificar que copiaste la key completa (incluye `:fx` al final)
- Revisar que no haya espacios extra

### Error: "Quota exceeded"
- Has usado los 500k caracteres del mes
- Esperar al próximo mes o upgrade a plan pago

### DeepL no disponible
- Verificar variable de entorno: `echo $DEEPL_API_KEY`
- Verificar logs de Lambda en CloudWatch

## 📚 Documentación Oficial

- API Docs: https://www.deepl.com/docs-api
- Idiomas soportados: https://www.deepl.com/docs-api/translate-text
- Status page: https://status.deepl.com/
