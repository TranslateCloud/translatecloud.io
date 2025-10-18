# TRANSLATECLOUD - GDPR & COMPLIANCE GUIDE
Last Updated: 2025-10-18 10:11:25

## OVERVIEW
TranslateCloud cumple con GDPR y LOPDGDD española.

## INFRASTRUCTURE COMPLIANCE

### Data Residency
- Region: EU-West-1 (Irlanda)
- RDS PostgreSQL: eu-west-1
- S3 Buckets: eu-west-1
- CloudFront: Origen EU

### Encryption
- En tránsito: HTTPS/TLS 1.2+
- En reposo: RDS AES-256, S3 AES-256

### Authentication
- Cognito: User Pool ID eu-west-1_FH51nx4II
- JWT con RS256
- Session: 30 min

## LEGAL REQUIREMENTS (España)

1. Política de Privacidad
2. Aviso Legal (LSSI)
3. Política de Cookies
4. Términos y Condiciones

## USER RIGHTS (ARCO-POL)

### Endpoints Requeridos
- GET /api/users/me/data (Acceso)
- PUT /api/users/me (Rectificación)
- DELETE /api/users/me (Olvido)
- GET /api/users/me/export (Portabilidad)
- PUT /api/users/me/marketing (Oposición)

## DATA RETENTION

- Usuarios activos: Sin límite
- Inactivos: Aviso 12 meses, delete 18 meses
- Proyectos: 90 días post-completado
- Logs: 30 días
- Backups: 30 días
- Facturas: 7 años (legal España)

## SECURITY MEASURES

- [x] HTTPS
- [x] DB cifrada
- [x] Secrets Manager
- [x] Cognito passwords
- [ ] WAF
- [ ] Rate limiting
- [ ] MFA admin

## BREACH NOTIFICATION

Proceso GDPR Art. 33-34:
1. Detección
2. Evaluación impacto
3. Notificación AEPD (72h)
4. Notificación usuarios (si alto riesgo)

Contacto AEPD: https://www.aepd.es

## DPO (Data Protection Officer)

NO obligatorio si:
- Menos 250 empleados
- No datos sensibles masivos

Recomendado: Responsable interno

## AWS DPA

- [ ] Firmar AWS GDPR DPA
- Disponible: AWS Artifact

## COOKIES

Esenciales (no consentimiento):
- JWT session
- CSRF token

Opcionales (requieren consentimiento):
- Language preference
- Analytics

## CHILDREN DATA

- Edad mínima: 14 años (España)
- Checkbox signup: Confirmo 14+ años

## THIRD PARTIES

Sub-processors:
1. AWS (Infrastructure) - EU
2. Stripe (Payments) - SCC
3. MarianMT (Translation) - Local

## PENALTIES

GDPR Fines:
- Tier 1: 10M EUR o 2% facturación
- Tier 2: 20M EUR o 4% facturación

## NEXT STEPS

### Pre-launch
1. Crear Política Privacidad
2. Crear Aviso Legal
3. Cookie banner
4. Endpoints ARCO
5. Firmar AWS DPA

### Post-launch
1. Registro ROPA
2. Procedimiento brechas
3. Auditoría seguridad

## RESOURCES

- AEPD: https://www.aepd.es
- GDPR: https://gdpr-info.eu