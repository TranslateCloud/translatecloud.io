# Guía Completa de Solución - CORS + Timeout Errors

**Fecha:** 21 de Octubre 2025
**Estado:** ✅ CORS RESUELTO | ⚠️ 504 Timeout necesita cambio en frontend
**Autor:** Claude Code Deep Analysis

---

## 📋 RESUMEN EJECUTIVO

### Problemas Identificados y Resueltos

| # | Problema | Estado | Solución |
|---|----------|--------|----------|
| 1 | CORS error desde navegador | ✅ RESUELTO | Eliminar OPTIONS de API Gateway |
| 2 | 504 Gateway Timeout en traducciones | ⚠️ IDENTIFICADO | Usar API async (/api/jobs/translate) |
| 3 | Inconsistencia headers CORS | ✅ RESUELTO | FastAPI maneja 100% del CORS |

---

## 🔴 PROBLEMA 1: CORS Error (RESUELTO)

### Síntomas

```
Access to fetch at 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login'
from origin 'https://translatecloud.io' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause (Análisis Completo)

#### Configuración ANTES del fix:

**API Gateway OPTIONS (preflight):**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,PATCH,OPTIONS
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization...
```

**FastAPI Lambda (requests reales):**
```http
HTTP/1.1 200 OK
access-control-allow-origin: https://translatecloud.io
access-control-allow-credentials: true
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

#### Por qué esto falla:

Según la especificación CORS (W3C):

> **REGLA:** Si la response incluye `Access-Control-Allow-Credentials: true`, entonces `Access-Control-Allow-Origin` NO PUEDE ser wildcard (`*`). DEBE ser un origin específico.

**El navegador ejecutaba:**

1. **Preflight (OPTIONS):** API Gateway respondía `Access-Control-Allow-Origin: *`
2. **Navegador pensaba:** "OK, cualquier origin está permitido"
3. **Request real (POST /api/auth/login):** FastAPI respondía:
   - `access-control-allow-origin: https://translatecloud.io`
   - `access-control-allow-credentials: true`
4. **Navegador detectaba:** "¡INCONSISTENCIA! Preflight dijo `*`, pero ahora dice origin específico CON credentials"
5. **Navegador BLOQUEABA:** Error CORS

#### Por qué funcionaba con curl:

`curl` NO ejecuta preflight requests. Solo hace la request directa y muestra la response. Por eso los tests con curl mostraban headers CORS correctos, pero el navegador fallaba.

### Solución Aplicada

**Eliminar método OPTIONS de API Gateway** para que FastAPI maneje TODO:

```bash
# Eliminar OPTIONS de resource /{proxy+}
aws apigateway delete-method \
  --rest-api-id e5yug00gdc \
  --resource-id y2ser9 \
  --http-method OPTIONS

# Eliminar OPTIONS de resource /
aws apigateway delete-method \
  --rest-api-id e5yug00gdc \
  --resource-id gwirqn12h1 \
  --http-method OPTIONS

# Deploy changes
aws apigateway create-deployment \
  --rest-api-id e5yug00gdc \
  --stage-name prod \
  --description "Remove OPTIONS - let FastAPI handle CORS"
```

### Resultado DESPUÉS del fix:

Ahora FastAPI (via CORSMiddleware) maneja TODAS las requests:

**OPTIONS (preflight):**
```http
HTTP/1.1 200 OK
access-control-allow-origin: https://translatecloud.io
access-control-allow-credentials: true
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-max-age: 600
vary: Origin
```

**POST/GET (requests reales):**
```http
HTTP/1.1 200 OK
access-control-allow-origin: https://translatecloud.io
access-control-allow-credentials: true
vary: Origin
```

✅ **CONSISTENTE:** Mismo origin específico + credentials en TODAS las responses

### Verificación

```bash
# Test OPTIONS preflight
curl -X OPTIONS "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login" \
  -H "Origin: https://translatecloud.io" \
  -H "Access-Control-Request-Method: POST" \
  -i

# Deberías ver:
# access-control-allow-origin: https://translatecloud.io
# access-control-allow-credentials: true
```

```bash
# Test POST real
curl -X POST "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login" \
  -H "Origin: https://translatecloud.io" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -i

# Deberías ver:
# access-control-allow-origin: https://translatecloud.io
# access-control-allow-credentials: true
```

---

## 🔴 PROBLEMA 2: 504 Gateway Timeout (IDENTIFICADO - REQUIERE ACCIÓN)

### Síntomas

```
e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/projects/crawl:1
Failed to load resource: the server responded with a status of 504 ()

e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/projects/translate:1
Failed to load resource: the server responded with a status of 504 ()

[API] Retrying request (attempt 2/3) after 1000ms
```

### Root Cause

#### API Gateway Timeout Limit: 30 segundos

API Gateway tiene un **límite máximo de 30 segundos** para cualquier request. Después de 30 segundos, devuelve `504 Gateway Timeout`, INCLUSO si Lambda todavía está procesando (Lambda puede ejecutar hasta 300 segundos).

```
Navegador → API Gateway (30s max) → Lambda (300s max)
                  ↑
                  Si Lambda no responde en 30s → 504 Gateway Timeout
```

#### Endpoints Síncronos vs Asíncronos

Tu backend tiene **DOS APIs** para traducción:

**❌ API Síncrona (DEPRECATED - causa 504):**
- `POST /api/projects/crawl` - Crawlea el sitio y espera respuesta (puede tomar 30+ segundos)
- `POST /api/projects/translate` - Traduce y espera respuesta (puede tomar minutos)

**✅ API Asíncrona (RECOMENDADA):**
- `POST /api/jobs/translate` - Crea job y devuelve job_id inmediatamente (< 1 segundo)
- `GET /api/jobs/{job_id}` - Polling cada 2 segundos para ver progreso
- Download cuando status = "completed"

### Arquitectura Correcta (Async)

```
[1] Frontend envía: POST /api/jobs/translate
    ↓ (< 1 segundo)
[2] API responde: {"job_id": "abc-123", "status": "pending"}
    ↓
[3] Frontend hace polling cada 2s: GET /api/jobs/abc-123
    ↓
[4] Responses progresivas:
    - {"status": "pending", "progress": 0}
    - {"status": "processing", "progress": 30}
    - {"status": "processing", "progress": 65}
    - {"status": "completed", "progress": 100, "download_url": "..."}
    ↓
[5] Frontend descarga ZIP desde S3 (presigned URL)
```

### Solución: Cambiar Frontend

Según la documentación (`SESSION-SUMMARY-2025-10-20.md`), el archivo `translate.html` YA FUE ACTUALIZADO el 20 de octubre para usar la API async.

**PERO** el usuario sigue viendo errores 504 en `/api/projects/crawl` y `/api/projects/translate`.

Esto significa:
1. El frontend NO está usando `translate.html` actualizado
2. O hay otra página/script llamando a los endpoints síncronos

**ACCIÓN REQUERIDA:**

Verificar que el frontend desplegado en https://translatecloud.io use el código actualizado:

```javascript
// ❌ INCORRECTO (causa 504)
const response = await fetch('/prod/api/projects/translate', {
  method: 'POST',
  body: JSON.stringify({
    url: websiteUrl,
    source_language: sourceLang,
    target_language: targetLang
  })
});

// ✅ CORRECTO (async job)
// 1. Submit job
const submitResponse = await fetch('/prod/api/jobs/translate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: websiteUrl,
    source_lang: sourceLang,
    target_lang: targetLang
  })
});
const { job_id } = await submitResponse.json();

// 2. Poll every 2 seconds
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/prod/api/jobs/${job_id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const job = await statusResponse.json();

  if (job.status === 'completed') {
    clearInterval(pollInterval);
    // Download from job.download_url
  }

  if (job.status === 'failed') {
    clearInterval(pollInterval);
    // Show error
  }

  // Update progress: job.progress (0-100)
}, 2000);
```

### Verificar Deployment del Frontend

```bash
# ¿Qué versión está desplegada en producción?
# Buscar el archivo translate.html en el bucket S3
aws s3 cp s3://translatecloud-frontend-prod/en/translate.html - | grep -E "(api/jobs|api/projects)" | head -5

# Si dice /api/projects → PROBLEMA: versión vieja desplegada
# Si dice /api/jobs → OK: versión correcta desplegada
```

### Si el problema persiste:

Revisar **todos los archivos JavaScript** en el frontend que hagan fetch a la API:

```bash
# Buscar todas las referencias a /api/projects
grep -r "api/projects" frontend/public/**/*.js
grep -r "api/projects" frontend/public/**/*.html

# Reemplazar con /api/jobs
```

---

## 🛠️ TROUBLESHOOTING GUIDE

### Herramienta 1: Test CORS desde DevTools

Abre DevTools (F12) en Chrome/Firefox y ejecuta:

```javascript
// Test CORS desde consola del navegador
fetch('https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    email: 'test@test.com',
    password: 'test123'
  })
})
.then(r => r.json())
.then(data => console.log('✅ CORS OK:', data))
.catch(err => console.error('❌ CORS ERROR:', err));
```

**Si falla:**
- Abrir Network tab
- Buscar el request fallido
- Click en el request
- Tab "Headers"
- Verificar:
  - Request Headers → Origin: https://translatecloud.io
  - Response Headers → access-control-allow-origin debe ser https://translatecloud.io

### Herramienta 2: Test CORS con curl

```bash
# Test OPTIONS (preflight)
curl -X OPTIONS \
  "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login" \
  -H "Origin: https://translatecloud.io" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -v 2>&1 | grep -i "access-control"

# Debe mostrar:
# access-control-allow-origin: https://translatecloud.io
# access-control-allow-credentials: true

# Test POST (request real)
curl -X POST \
  "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login" \
  -H "Origin: https://translatecloud.io" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser12345@test.com","password":"Test123"}' \
  -v 2>&1 | grep -i "access-control"

# Debe mostrar:
# access-control-allow-origin: https://translatecloud.io
# access-control-allow-credentials: true
```

### Herramienta 3: Ver CloudWatch Logs

```powershell
# Ver últimos 30 minutos de logs de Lambda
powershell -Command "aws logs tail '/aws/lambda/translatecloud-api' --since 30m --format short"

# Ver solo ERRORs
powershell -Command "aws logs tail '/aws/lambda/translatecloud-api' --since 30m --filter-pattern ERROR --format short"

# Ver logs en tiempo real (útil para debugging)
powershell -Command "aws logs tail '/aws/lambda/translatecloud-api' --follow"
```

### Herramienta 4: Verificar Estado del Sistema

```bash
# ✅ Health check
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/health

# Debe responder: {"status":"healthy"}

# ✅ Translation service status
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/translation/status

# Debe responder:
# {"deepl_available":true,"marian_available":false,"primary_provider":"deepl","status":"operational"}

# ✅ DeepL usage
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/translation/usage

# Debe mostrar cuántos caracteres quedan
```

---

## 📚 DOCUMENTACIÓN TÉCNICA

### Configuración CORS en FastAPI (backend/src/main.py)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://translatecloud.io",          # ✅ Producción
        "https://www.translatecloud.io",       # ✅ Producción con www
        "https://translate.translatecloud.io", # ✅ Subdominio translate
        "http://localhost:3000",               # ✅ Dev local
        "http://localhost:5173",               # ✅ Vite dev server
        "http://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com",  # ✅ S3 endpoint
        "https://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com"  # ✅ S3 HTTPS
    ],
    allow_credentials=True,  # ⚠️ Esto requiere origin específico (NO wildcard *)
    allow_methods=["*"],     # Permite todos los métodos HTTP
    allow_headers=["*"],     # Permite todos los headers
)
```

### API Gateway Configuration

**Tipo:** REST API (v1) - ID: `e5yug00gdc`

**Recursos:**
- `/` (resource ID: gwirqn12h1) → Método ANY (proxy a Lambda)
- `/{proxy+}` (resource ID: y2ser9) → Método ANY (proxy a Lambda)

**❌ NO tiene método OPTIONS** (eliminado el 21 Oct 2025)

**Razón:** FastAPI maneja OPTIONS via CORSMiddleware

**Deployment:** Stage `prod`
**Endpoint:** `https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod`

### Lambda Function Configuration

- **Nombre:** `translatecloud-api`
- **Runtime:** Python 3.11
- **Handler:** `lambda_handler.handler`
- **Timeout:** 300 segundos (5 minutos)
- **Memory:** 1024 MB
- **Code Size:** ~26 MB
- **Region:** eu-west-1

**Environment Variables:**
- `DB_HOST`: RDS PostgreSQL endpoint
- `DB_PORT`: 5432
- `DB_NAME`: postgres
- `DB_USER`: translatecloud_api
- `DB_PASSWORD`: [secret]
- `DEEPL_API_KEY`: [secret]
- `JWT_SECRET_KEY`: [secret]

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de lanzar a producción, verificar:

### CORS
- [x] OPTIONS devuelve `access-control-allow-origin: https://translatecloud.io`
- [x] OPTIONS devuelve `access-control-allow-credentials: true`
- [x] POST/GET devuelven mismos headers que OPTIONS
- [x] No hay wildcard `*` con credentials
- [x] FastAPI maneja 100% del CORS (API Gateway no interfiere)

### Auth
- [x] POST /api/auth/signup funciona
- [x] POST /api/auth/login funciona
- [x] JWT token se devuelve correctamente
- [x] bcrypt 4.0.1 funciona en Lambda

### Database
- [x] Lambda conecta a RDS PostgreSQL
- [x] SSL/TLS habilitado (sslmode=require)
- [x] Queries ejecutan correctamente
- [x] Transactions (commit/rollback) funcionan

### Translation
- [x] DeepL API funciona
- [x] GET /api/translation/status → operational
- [x] Caracteres disponibles suficientes (46% remaining)

### API Async (CRÍTICO - VERIFICAR)
- [ ] **TODO:** Frontend usa POST /api/jobs/translate (NO /api/projects/translate)
- [ ] **TODO:** Frontend hace polling a GET /api/jobs/{job_id}
- [ ] **TODO:** No hay 504 timeouts en producción
- [ ] **TODO:** Progress tracking funciona (0-100%)
- [ ] **TODO:** Download desde S3 funciona

---

## 🚀 PRÓXIMOS PASOS

### Inmediato (HOY - 21 Oct)
1. ✅ CORS fix deployed y verificado
2. ⏳ **URGENTE:** Verificar qué versión de frontend está en producción
3. ⏳ **URGENTE:** Asegurar que frontend use `/api/jobs/translate` (async)
4. ⏳ Probar traducción completa end-to-end desde https://translatecloud.io
5. ⏳ Eliminar endpoints síncronos `/api/projects/crawl` y `/api/projects/translate` del código (deprecate)

### Corto Plazo (22-23 Oct)
1. Test de carga: 10 traducciones concurrentes
2. Verificar que DynamoDB y SQS estén configurados para jobs async
3. Implementar manejo de errores cuando DeepL quota se agote
4. Agregar CloudWatch alarms para 504 errors
5. Documentar flow completo de async translation para el equipo

### Antes del Launch (24-27 Oct)
1. Smoke test completo desde producción
2. Verificar rate limiting
3. Test de recuperación ante fallos
4. Plan de rollback documentado
5. Monitoring dashboard configurado

---

## 📞 CONTACTOS Y RECURSOS

**API Endpoint:** https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
**Frontend:** https://translatecloud.io
**Region:** eu-west-1

**CloudWatch Logs:**
```powershell
powershell -Command "aws logs tail '/aws/lambda/translatecloud-api' --follow"
```

**API Gateway Console:**
```
https://eu-west-1.console.aws.amazon.com/apigateway/home?region=eu-west-1#/apis/e5yug00gdc
```

**Lambda Console:**
```
https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions/translatecloud-api
```

---

**Última Actualización:** 21 de Octubre 2025, 14:30 UTC
**Autor:** Claude Code - Deep System Analysis
**Status:** CORS ✅ RESUELTO | Timeout ⚠️ IDENTIFICADO - Requiere verificación frontend
