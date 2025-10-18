# TRANSLATECLOUD - TODO LIST
Last Updated: 2025-10-18 10:10:37

## DAY 4 - DEPLOYMENT & AUTH (IN PROGRESS)

### High Priority
- [x] Crear Cognito User Pool
- [x] Configurar JWT authentication middleware
- [ ] Desplegar API a AWS Lambda
- [ ] Configurar API Gateway
- [ ] Probar autenticación end-to-end
- [ ] Conectar frontend con backend

### Medium Priority
- [ ] Rate limiting
- [ ] Error handling mejorado
- [ ] Logging CloudWatch
- [ ] Monitoreo básico

## DAY 5 - PAYMENTS & PRODUCTION

- [ ] Crear cuenta Stripe
- [ ] Integrar Stripe SDK
- [ ] Payment intent endpoints
- [ ] Webhook handling
- [ ] Subscription management
- [ ] Usage tracking

## WEEK 2 - FEATURES

- [ ] Document upload/translation
- [ ] Batch processing
- [ ] Translation memory
- [ ] Analytics dashboard
- [ ] Admin panel

## GDPR & COMPLIANCE (PRIORITARIO)

### Legal Requirements
- [ ] Política de Privacidad (ES/EN)
- [ ] Términos y Condiciones (ES/EN)
- [ ] Cookie Policy
- [ ] Aviso Legal (España)
- [ ] Consentimiento explícito (checkbox, no pre-marcado)
- [ ] Double opt-in para emails

### Data Protection
- [ ] Implementar "Derecho al Olvido" (DELETE user endpoint)
- [ ] Implementar "Derecho de Acceso" (GET all user data)
- [ ] Implementar "Portabilidad de Datos" (export user data JSON)
- [ ] Implementar "Rectificación" (UPDATE user data)
- [ ] Data retention policies (auto-delete después X días inactivo)
- [ ] Minimización de datos (solo recoger lo necesario)

### Security & Privacy
- [x] Cifrado en tránsito (HTTPS)
- [x] Cifrado en reposo (RDS, S3)
- [ ] Logs de auditoría (quién accedió qué y cuándo)
- [ ] IP logging con consentimiento
- [ ] Anonimización de datos en analytics
- [x] Password hashing (Cognito)
- [ ] MFA opcional para usuarios
- [ ] Session timeout (30 min inactividad)

### Compliance Documentation
- [ ] Registro de Actividades de Tratamiento (ROPA)
- [ ] Evaluación de Impacto (DPIA) si aplica
- [ ] Nombrar DPO si aplica
- [ ] Contrato AWS DPA
- [ ] Medidas técnicas y organizativas

### User Rights Endpoints
- [ ] DELETE /api/users/me (derecho al olvido)
- [ ] GET /api/users/me/data (acceso a datos)
- [ ] GET /api/users/me/export (portabilidad JSON)
- [ ] PUT /api/users/me/consent (consentimientos)
- [ ] GET /api/users/me/audit-log (historial)

### Frontend Compliance
- [ ] Banner de cookies
- [ ] Formulario consentimiento signup
- [ ] Links políticas en footer
- [ ] Página Mis Datos
- [ ] Configuración privacidad
- [ ] Opt-out emails

### Infrastructure
- [x] Servidor EU (eu-west-1)
- [x] Base de datos EU
- [x] Secrets Manager EU

## INFRASTRUCTURE

- [ ] Git remote GitHub
- [ ] CI/CD pipeline
- [ ] Testing automatizado

## TECHNICAL DEBT

- [ ] Fix LF/CRLF
- [ ] Testing completo
- [ ] Performance
- [ ] Security hardening