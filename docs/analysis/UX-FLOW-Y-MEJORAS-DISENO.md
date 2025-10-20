# TRANSLATECLOUD - FLUJO UX Y MEJORAS DE DISEÑO
**Fecha:** 20 de Octubre de 2025
**Versión:** 1.0 - Análisis Completo UX/UI
**Propósito:** Documentar experiencia de usuario, design system y mejoras necesarias

---

## 📊 ÍNDICE
1. [Sistema de Diseño Actual](#sistema-de-diseño-actual)
2. [Flujos UX por Servicio](#flujos-ux-por-servicio)
3. [Problemas UX Identificados](#problemas-ux-identificados)
4. [Mejoras Requeridas](#mejoras-requeridas)
5. [Prioridades de Implementación](#prioridades-de-implementación)

---

## 🎨 SISTEMA DE DISEÑO ACTUAL

### Paleta de Colores

#### Light Mode (Modo Principal)
```css
:root {
  /* Colores principales */
  --color-primary: #111827;           /* Negro grisáceo - texto principal */
  --color-primary-light: #1F2937;     /* Gris muy oscuro */

  /* Colores de marca */
  --color-accent: #0EA5E9;            /* Azul cielo corporativo (principal) */
  --color-accent-hover: #0284C7;      /* Azul cielo oscuro (hover) */
  --color-accent-light: #38BDF8;      /* Azul cielo claro (acentos sutiles) */

  /* Grises neutros */
  --color-white: #FFFFFF;
  --color-gray-50: #F9FAFB;           /* Casi blanco - backgrounds */
  --color-gray-100: #F3F4F6;          /* Gris muy claro - cards */
  --color-gray-200: #E5E7EB;          /* Gris claro - borders */
  --color-gray-300: #D1D5DB;          /* Gris medio-claro */
  --color-gray-400: #9CA3AF;          /* Gris medio */
  --color-gray-500: #6B7280;          /* Gris - texto secundario */
  --color-gray-600: #4B5563;          /* Gris oscuro */
  --color-gray-700: #374151;          /* Gris muy oscuro */
  --color-gray-800: #1F2937;          /* Casi negro */
  --color-gray-900: #111827;          /* Negro grisáceo */

  /* Estados */
  --color-success: #10B981;           /* Verde moderno */
  --color-warning: #F59E0B;           /* Amarillo/naranja */
  --color-error: #EF4444;             /* Rojo */

  /* Texto secundario */
  --color-secondary: #6B7280;         /* Gris neutro medio */
  --color-secondary-light: #9CA3AF;   /* Gris claro neutro */
}
```

**Uso:**
- **Primario (#111827):** Texto principal, headings
- **Accent (#0EA5E9):** Botones CTA, links, estados activos
- **Grises:** Backgrounds, borders, texto secundario
- **Success/Warning/Error:** Alertas y notificaciones

---

#### Dark Mode (Notion/Excel Professional Style)
```css
.dark-mode {
  /* Backgrounds - Progresión de negro */
  --bg-primary: #0d0d0d;              /* Negro casi puro - background principal */
  --bg-secondary: #191919;            /* Gris muy oscuro - navbar/sidebar */
  --bg-tertiary: #202020;             /* Gris oscuro - cards */
  --bg-elevated: #2a2a2a;             /* Gris medio oscuro - hover */

  /* Texto - Progresión de grises claros */
  --text-primary: #e6e6e6;            /* Gris muy claro - texto principal */
  --text-secondary: #9b9b9b;          /* Gris medio - texto secundario */
  --text-tertiary: #6b6b6b;           /* Gris oscuro - placeholder */

  /* Bordes - Sutiles */
  --border-default: #333333;          /* Gris oscuro */
  --border-hover: #404040;            /* Gris medio oscuro */

  /* Accent - Cyan brillante */
  --accent: #00d4ff;                  /* Cyan eléctrico */
  --accent-hover: #00b8e6;            /* Cyan oscuro */
  --accent-bg: rgba(0, 212, 255, 0.08); /* Cyan transparente */
}
```

**Características del Dark Mode:**
- Inspirado en Notion y Excel (profesional, no gaming)
- Contraste alto pero no cansador (90:1 ratio)
- Accent cyan en lugar de azul (destaca más en fondo negro)
- Bordes sutiles (#333) para separar secciones
- Transiciones suaves (0.2s ease)

**Toggle ubicado en:** Bottom-right floating button
**Persistencia:** localStorage (`translatecloud_dark_mode`)

---

### Tipografía

#### Fuente Principal
```css
--font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**IBM Plex Sans** (Google Fonts)
- **Weights disponibles:** 300, 400, 500, 600
- **Características:**
  - Diseñada por IBM para interfaces profesionales
  - Excelente legibilidad en pantalla
  - Geométrica pero cálida
  - Soporta caracteres latinos, cirílicos, griegos

**Razón de elección:** Alternativa moderna a Helvetica/Arial, específicamente diseñada para UIs corporativas.

**Fallback:** System fonts nativos (mejor rendimiento)

#### Escalas Tipográficas
```css
/* Tamaños de texto */
--text-xs: 0.75rem;      /* 12px - Labels pequeños */
--text-sm: 0.875rem;     /* 14px - Texto secundario */
--text-base: 1rem;       /* 16px - Texto principal */
--text-lg: 1.125rem;     /* 18px - Subtítulos */
--text-xl: 1.25rem;      /* 20px - Títulos pequeños */
--text-2xl: 1.5rem;      /* 24px - Títulos medianos */
--text-3xl: 1.875rem;    /* 30px - Títulos grandes */
--text-4xl: 2.25rem;     /* 36px - Hero titles */
--text-5xl: 3rem;        /* 48px - Landing pages */

/* Pesos */
--font-light: 300;       /* Texto largo */
--font-regular: 400;     /* Default */
--font-medium: 500;      /* Botones, labels */
--font-semibold: 600;    /* Headings */

/* Alturas de línea */
--leading-tight: 1.25;   /* Headings */
--leading-normal: 1.5;   /* Texto párrafos */
--leading-relaxed: 1.75; /* Texto largo */
```

**Uso recomendado:**
```css
/* Headings */
h1 { font-size: var(--text-4xl); font-weight: 600; line-height: 1.25; }
h2 { font-size: var(--text-3xl); font-weight: 600; line-height: 1.25; }
h3 { font-size: var(--text-2xl); font-weight: 600; line-height: 1.25; }

/* Body */
p { font-size: var(--text-base); line-height: 1.6; }
small { font-size: var(--text-sm); color: var(--color-gray-500); }

/* Buttons */
button { font-size: var(--text-sm); font-weight: 500; }
```

---

### Espaciado y Layout

#### Espaciado (Escala de 4px)
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

**Reglas de uso:**
- Padding interno cards: `var(--space-6)` (24px)
- Márgenes entre secciones: `var(--space-12)` (48px)
- Separación entre elementos: `var(--space-4)` (16px)
- Padding botones: `var(--space-2) var(--space-4)` (8px 16px)

#### Border Radius
```css
--radius-sm: 0.25rem;   /* 4px - Pills, badges */
--radius-md: 0.375rem;  /* 6px - Botones, inputs */
--radius-lg: 0.5rem;    /* 8px - Cards */
--radius-xl: 0.75rem;   /* 12px - Modals */
--radius-2xl: 1rem;     /* 16px - Hero sections */
--radius-full: 9999px;  /* Círculos perfectos */
```

#### Shadows (Profundidad)
```css
/* Elevación 1 - Cards */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Elevación 2 - Dropdowns */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -1px rgba(0, 0, 0, 0.06);

/* Elevación 3 - Modals */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* Elevación 4 - Overlays */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04);

/* Focus rings */
--shadow-focus: 0 0 0 3px rgba(14, 165, 233, 0.1);
```

#### Breakpoints (Responsive)
```css
/* Mobile first approach */
--breakpoint-sm: 640px;   /* Tablets */
--breakpoint-md: 768px;   /* Tablets landscape */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
--breakpoint-2xl: 1536px; /* Extra large */
```

**Grid system:**
- Container max-width: `1200px`
- Padding lateral: `var(--space-8)` (32px)
- Gap entre elementos: `var(--space-6)` (24px)

---

### Componentes Base

#### Botones

**Primario (CTA):**
```css
.btn-primary {
  background-color: var(--color-accent);     /* #0EA5E9 */
  color: var(--color-white);
  padding: var(--space-2) var(--space-4);    /* 8px 16px */
  border-radius: var(--radius-md);           /* 6px */
  font-weight: 500;
  font-size: var(--text-sm);                 /* 14px */
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--color-accent-hover); /* #0284C7 */
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  background-color: var(--color-gray-300);
  cursor: not-allowed;
  transform: none;
}
```

**Secundario (Outline):**
```css
.btn-secondary {
  background-color: transparent;
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-300);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: var(--color-gray-50);
  border-color: var(--color-gray-400);
}
```

**Destructivo:**
```css
.btn-danger {
  background-color: var(--color-error);  /* #EF4444 */
  color: white;
}

.btn-danger:hover {
  background-color: #DC2626;
}
```

**Tamaños:**
```css
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }    /* Pequeño */
.btn-md { padding: 0.5rem 1rem; font-size: 0.875rem; }         /* Default */
.btn-lg { padding: 0.75rem 1.5rem; font-size: 1rem; }          /* Grande */
```

---

#### Cards
```css
.card {
  background-color: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);           /* 8px */
  padding: var(--space-6);                   /* 24px */
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-gray-300);
  transform: translateY(-2px);
}

.card-header {
  border-bottom: 1px solid var(--color-gray-200);
  padding-bottom: var(--space-4);
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-gray-900);
}

.card-description {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin-top: var(--space-2);
}
```

---

#### Formularios

**Inputs:**
```css
.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);    /* 12px 16px */
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);           /* 6px */
  font-size: var(--text-base);               /* 16px */
  color: var(--color-gray-900);
  background-color: var(--color-white);
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-focus);           /* Azul suave */
  background-color: var(--color-white);
}

.form-input:disabled {
  background-color: var(--color-gray-100);
  cursor: not-allowed;
  color: var(--color-gray-500);
}

.form-input::placeholder {
  color: var(--color-gray-400);
}

/* Estado error */
.form-input.error {
  border-color: var(--color-error);
}

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
```

**Labels:**
```css
.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-gray-700);
  margin-bottom: var(--space-2);
}

.form-label.required::after {
  content: ' *';
  color: var(--color-error);
}
```

**Mensajes de error:**
```css
.form-error {
  font-size: var(--text-sm);
  color: var(--color-error);
  margin-top: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.form-error::before {
  content: '⚠';
}
```

**Select:**
```css
.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,..."); /* Flecha personalizada */
  background-position: right 0.75rem center;
  background-repeat: no-repeat;
  background-size: 16px 12px;
  padding-right: 2.5rem;
}
```

---

#### Alerts/Notificaciones

**Success:**
```css
.alert-success {
  background-color: #D1FAE5;              /* Verde claro */
  border: 1px solid #10B981;
  color: #065F46;                         /* Verde oscuro */
  padding: var(--space-4);
  border-radius: var(--radius-md);
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.alert-success::before {
  content: '✓';
  font-size: 1.25rem;
  color: #10B981;
}
```

**Error:**
```css
.alert-error {
  background-color: #FEE2E2;              /* Rojo claro */
  border: 1px solid #EF4444;
  color: #991B1B;                         /* Rojo oscuro */
}

.alert-error::before {
  content: '✕';
  color: #EF4444;
}
```

**Warning:**
```css
.alert-warning {
  background-color: #FEF3C7;              /* Amarillo claro */
  border: 1px solid #F59E0B;
  color: #92400E;                         /* Amarillo oscuro */
}

.alert-warning::before {
  content: '⚠';
  color: #F59E0B;
}
```

**Info:**
```css
.alert-info {
  background-color: #DBEAFE;              /* Azul claro */
  border: 1px solid #3B82F6;
  color: #1E40AF;                         /* Azul oscuro */
}

.alert-info::before {
  content: 'ℹ';
  color: #3B82F6;
}
```

---

#### Modals
```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);   /* Overlay oscuro */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal {
  background-color: var(--color-white);
  border-radius: var(--radius-xl);        /* 12px */
  padding: var(--space-6);
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.modal-title {
  font-size: var(--text-2xl);
  font-weight: 600;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-gray-500);
}

.modal-close:hover {
  color: var(--color-gray-900);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

#### Loading States

**Spinner:**
```css
.spinner {
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-sm { width: 20px; height: 20px; border-width: 2px; }
.spinner-lg { width: 60px; height: 60px; border-width: 4px; }
```

**Progress Bar:**
```css
.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-accent);
  transition: width 0.3s ease;
  border-radius: var(--radius-full);
}

/* Animación de progreso indeterminado */
.progress-fill.indeterminate {
  width: 30%;
  animation: indeterminate 1.5s ease-in-out infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}
```

**Skeleton Screen:**
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-gray-200) 0%,
    var(--color-gray-300) 50%,
    var(--color-gray-200) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

.skeleton-text {
  height: 1rem;
  margin-bottom: var(--space-2);
}

.skeleton-title {
  height: 1.5rem;
  width: 60%;
  margin-bottom: var(--space-4);
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

---

## 🔄 FLUJOS UX POR SERVICIO

### FLUJO 1: Usuario Nuevo → Primera Traducción

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: DESCUBRIMIENTO                                       │
└─────────────────────────────────────────────────────────────┘

PÁGINA: Landing (index.html)
URL: https://www.translatecloud.io

┌───────────────────────────────────────────────────────────────┐
│                         TranslateCloud                        │
│                                                               │
│           Translate your website. Keep your SEO.              │
│                   Own your content.                           │
│                                                               │
│     [Get Started Free]     [View Pricing]                     │
│                                                               │
│  ✓ 5,000 words free       ✓ No credit card                   │
│  ✓ Professional AI        ✓ SEO-friendly                     │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario click "Get Started Free"


┌─────────────────────────────────────────────────────────────┐
│ FASE 2: REGISTRO                                             │
└─────────────────────────────────────────────────────────────┘

PÁGINA: Signup (signup.html)
URL: /en/signup.html

┌───────────────────────────────────────────────────────────────┐
│  TranslateCloud                                               │
│                                                               │
│  Create your free account                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━                                      │
│                                                               │
│  Full Name                                                    │
│  [________________]                                           │
│                                                               │
│  Email Address                                                │
│  [________________]                                           │
│                                                               │
│  Password                                                     │
│  [________________] 👁                                        │
│  • At least 8 characters                                      │
│  • One uppercase letter                                       │
│  • One number                                                 │
│                                                               │
│  ☐ I agree to Terms of Service and Privacy Policy            │
│                                                               │
│  [Sign Up]                                                    │
│                                                               │
│  Already have an account? [Log in]                           │
└───────────────────────────────────────────────────────────────┘

BACKEND:
POST /api/auth/signup
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}

RESPONSE:
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "email": "john@example.com",
    "plan": "free",
    "word_limit": 5000,
    "words_used_this_month": 0
  }
}

✅ Token guardado en localStorage
✅ Redirección a /en/dashboard.html

⬇️


┌─────────────────────────────────────────────────────────────┐
│ FASE 3: DASHBOARD (Primera Vista)                           │
└─────────────────────────────────────────────────────────────┘

PÁGINA: Dashboard (dashboard.html)
URL: /en/dashboard.html

┌───────────────────────────────────────────────────────────────┐
│  TranslateCloud    Dashboard  Projects  Pricing  [John Doe ▾]│
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Welcome, John! 👋                                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Current Plan: Free                                     │ │
│  │                                                         │ │
│  │  Word Usage                                             │ │
│  │  0 / 5,000 words used this month                       │ │
│  │  ░░░░░░░░░░░░░░░░░░░░ 0%                              │ │
│  │                                                         │ │
│  │  Resets on: November 1, 2025                           │ │
│  │                                                         │ │
│  │  [Upgrade Plan]                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Quick Actions                                          │ │
│  │                                                         │ │
│  │  [🌐 Translate Website]                                 │ │
│  │  Translate entire websites while preserving SEO        │ │
│  │                                                         │ │
│  │  [📄 Translate Document]                                │ │
│  │  Upload PDF, Word, Excel files for translation         │ │
│  │                                                         │ │
│  │  [✏️ Translate Text]                                     │ │
│  │  Quick translation for words and sentences             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Recent Projects                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  No projects yet. Start your first translation!              │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario click "Translate Website"


┌─────────────────────────────────────────────────────────────┐
│ FASE 4: ANÁLISIS DE SITIO WEB                               │
└─────────────────────────────────────────────────────────────┘

PÁGINA: Translate Website (translate.html)
URL: /en/translate.html

┌───────────────────────────────────────────────────────────────┐
│  TranslateCloud    [← Back to Dashboard]                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Translate Website                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  Step 1: Enter Website URL                                    │
│                                                               │
│  Website URL                                                  │
│  [https://example.com________________] 🔗                     │
│                                                               │
│  Languages                                                    │
│  [English ▾]  →  [Spanish ▾]                                 │
│                                                               │
│  ☐ Advanced Options                                          │
│     ☐ Crawl subdomains                                       │
│     ☐ Follow external links                                  │
│     Max pages: [50_____]                                     │
│                                                               │
│  [Analyze Website]                                            │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario ingresa URL y click "Analyze Website"

LOADING STATE:
┌───────────────────────────────────────────────────────────────┐
│  Analyzing website...                                         │
│  ════════════░░░░░░░░░░ 45%                                  │
│                                                               │
│  ⏳ Crawling pages...                                         │
│  ✓ Found 5 pages                                             │
│  ⏳ Counting words...                                         │
└───────────────────────────────────────────────────────────────┘

BACKEND:
POST /api/projects/crawl
{
  "url": "https://example.com",
  "source_language": "en",
  "target_language": "es"
}

⬇️ 3-5 segundos después

RESULTADO:
┌───────────────────────────────────────────────────────────────┐
│  ✅ Website Analysis Complete                                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Summary                                                │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │ │
│  │                                                         │ │
│  │  📊 Pages found:       5                               │ │
│  │  📝 Total words:       2,500                           │ │
│  │  💰 Cost:              €137.50                         │ │
│  │  ⏱️  Estimated time:    2-3 minutes                    │ │
│  │                                                         │ │
│  │  Your available words: 5,000                           │ │
│  │  ✅ You have enough words for this translation         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Pages to be translated:                                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 🏠 https://example.com/                                 │ │
│  │    500 words                                            │ │
│  │    ━━━━━━━━━━░░░░░░░░░░ 20%                            │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ℹ️  https://example.com/about                           │ │
│  │    300 words                                            │ │
│  │    ━━━━━━━━░░░░░░░░░░░░ 12%                            │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ 📧 https://example.com/contact                          │ │
│  │    150 words                                            │ │
│  │    ━━━░░░░░░░░░░░░░░░░░ 6%                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  [Cancel]  [Confirm & Translate]                             │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario revisa y click "Confirm & Translate"


┌─────────────────────────────────────────────────────────────┐
│ FASE 5: TRADUCCIÓN EN PROGRESO                              │
└─────────────────────────────────────────────────────────────┘

LOADING STATE (Mejor UX):
┌───────────────────────────────────────────────────────────────┐
│  Translating your website...                                  │
│  ════════════════════░░░░ 65%                                │
│                                                               │
│  ✅ index.html → Translated (500 words)                      │
│  ✅ about.html → Translated (300 words)                      │
│  ⏳ contact.html → Translating... (150 words)                │
│  ⏹️  services.html → Pending (450 words)                     │
│  ⏹️  blog.html → Pending (1,100 words)                       │
│                                                               │
│  Words translated: 800 / 2,500                                │
│  Estimated time remaining: 1 minute                           │
│                                                               │
│  💡 Tip: We're using DeepL AI for professional translations   │
│                                                               │
└───────────────────────────────────────────────────────────────┘

BACKEND:
POST /api/projects/translate
{
  "project_id": "uuid",
  "pages": [...],
  "source_language": "en",
  "target_language": "es"
}

⬇️ 2-3 minutos después


┌─────────────────────────────────────────────────────────────┐
│ FASE 6: TRADUCCIÓN COMPLETA                                 │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  🎉 Translation Complete!                                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ✅ 5 pages translated successfully                     │ │
│  │  📝 2,500 words processed                               │ │
│  │  ⏱️  Completed in 2m 34s                                 │ │
│  │                                                         │ │
│  │  Remaining words: 2,500 / 5,000 (50%)                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  [Download ZIP File]                                          │
│                                                               │
│  What's included:                                             │
│  • All translated HTML files                                  │
│  • CSS and JavaScript files                                   │
│  • Images and assets                                          │
│  • README with installation instructions                      │
│                                                               │
│  [View Translation] [Start New Translation]                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario click "Download ZIP File"

BACKEND:
POST /api/projects/export/{project_id}

BROWSER:
⬇️ Descarga archivo: translated-site-uuid-123.zip

⬇️


┌─────────────────────────────────────────────────────────────┐
│ FASE 7: APLICAR A SU SITIO WEB (Fuera de la app)            │
└─────────────────────────────────────────────────────────────┘

CONTENIDO DEL ZIP:
translated-site-uuid-123.zip
├── README.md                  ← Instrucciones de instalación
├── index.html                 ← Página principal traducida
├── about.html
├── contact.html
├── services.html
├── blog.html
├── assets/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
└── .htaccess                  ← Reglas de redirección (opcional)

README.md incluye:
1. Método 1: Subdirectorio (/es/)
2. Método 2: Subdominio (es.example.com)
3. Método 3: Dominio separado (example.es)
4. Tags hreflang para SEO
5. Selector de idioma (código HTML)
6. Solución de problemas común

```

---

### FLUJO 2: Usuario Alcanza Límite → Upgrade

```
┌─────────────────────────────────────────────────────────────┐
│ USUARIO EN DASHBOARD                                         │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  Current Plan: Free                                           │
│                                                               │
│  Word Usage                                                   │
│  4,800 / 5,000 words used this month                         │
│  ████████████████████░░ 96%                                  │
│                                                               │
│  ⚠️ Only 200 words remaining!                                │
│                                                               │
│  [Upgrade Plan]                                              │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario intenta traducir sitio con 1,000 palabras

ERROR MODAL (Nuevo):
┌───────────────────────────────────────────────────────────────┐
│  ⚠️ Word Limit Exceeded                              [✕]     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  This translation requires 1,000 words, but you only have    │
│  200 words remaining in your Free plan.                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Upgrade to Professional Plan                           │ │
│  │                                                         │ │
│  │  ✓ 50,000 words per month                              │ │
│  │  ✓ Priority support                                    │ │
│  │  ✓ Faster translation                                  │ │
│  │  ✓ API access                                          │ │
│  │                                                         │ │
│  │  €699/month or €6,990/year (save €1,398!)             │ │
│  │                                                         │ │
│  │  [Upgrade Now]                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Or translate a smaller website (200 words or less)          │
│                                                               │
│  [Cancel]  [View All Plans]                                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario click "Upgrade Now"

PÁGINA: Pricing
URL: /en/pricing.html

┌───────────────────────────────────────────────────────────────┐
│  Choose Your Plan                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                    │
│  │ Free │  │ Pro  │  │ Biz  │  │ Ent  │                    │
│  │      │  │  ⭐  │  │      │  │      │                    │
│  │ €0   │  │€699  │  │€1,799│  │€4,999│                    │
│  │/month│  │/month│  │/month│  │/month│                    │
│  │      │  │      │  │      │  │      │                    │
│  │5,000 │  │50,000│  │150k  │  │500k  │                    │
│  │words │  │words │  │words │  │words │                    │
│  │      │  │      │  │      │  │      │                    │
│  │[Used]│  │[Buy] │  │[Buy] │  │[Call]│                    │
│  └──────┘  └──────┘  └──────┘  └──────┘                    │
│                                                               │
│  ☑ Monthly  ☐ Annual (Save 20%)                             │
│                                                               │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario click "Buy" en Professional

REDIRECT: Stripe Checkout

┌───────────────────────────────────────────────────────────────┐
│  🔒 Secure Checkout - Powered by Stripe                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  Professional Plan                                            │
│  €699.00 per month                                           │
│                                                               │
│  Card Information                                             │
│  [1234 5678 9012 3456_____] 💳                               │
│                                                               │
│  [12/25__] [123_]                                            │
│   MM/YY     CVC                                              │
│                                                               │
│  Name on Card                                                 │
│  [John Doe________________]                                   │
│                                                               │
│  Billing Address                                              │
│  [Spain________________] 🌍                                   │
│                                                               │
│  [Madrid______________]                                       │
│  [28001___]                                                   │
│                                                               │
│  You'll be charged €699.00 today, then €699.00 monthly       │
│  Cancel anytime in your dashboard                             │
│                                                               │
│  [Pay €699.00]                                               │
│                                                               │
│  🔒 Secured by Stripe                                        │
└───────────────────────────────────────────────────────────────┘

⬇️ Usuario completa pago

BACKEND WEBHOOK:
Stripe → POST /api/payments/webhook
Event: checkout.session.completed

DATABASE UPDATE:
UPDATE users SET
  plan = 'professional',
  subscription_status = 'active',
  word_limit = 50000,
  words_used_this_month = 0,  ← Reset!
  stripe_customer_id = 'cus_xxx',
  stripe_subscription_id = 'sub_xxx'
WHERE id = 'user_uuid'

⬇️ Redirect to Success Page

┌───────────────────────────────────────────────────────────────┐
│  🎉 Welcome to Professional Plan!                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                                               │
│  Your subscription has been activated successfully.           │
│                                                               │
│  What's next:                                                 │
│  ✓ Your word limit has been increased to 50,000 words        │
│  ✓ Your monthly usage has been reset to 0                    │
│  ✓ You now have priority support                             │
│  ✓ Faster translation processing                             │
│                                                               │
│  [Go to Dashboard]  [Start Translating]                      │
│                                                               │
│  Receipt sent to: john@example.com                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘

✅ Usuario ahora puede traducir sitios grandes

```

---

## 🔍 PROBLEMAS UX IDENTIFICADOS

### CRÍTICOS (Bloquean Funcionalidad)

#### 1. **Límite de Palabras No Se Aplica**
**Problema:** Backend no valida límite ANTES de traducir
**Impacto:** Usuario Free puede traducir ilimitadamente
**Ubicación:** `backend/src/api/routes/projects.py:210`

**Solución:**
```python
# AGREGAR ANTES DE LINEA 210 (antes de iniciar traducción)
cursor.execute(
    "SELECT word_limit, words_used_this_month FROM users WHERE id = %s",
    (user_id,)
)
user = cursor.fetchone()

total_words = sum(page['word_count'] for page in request.pages)

if user['words_used_this_month'] + total_words > user['word_limit']:
    raise HTTPException(
        status_code=402,
        detail={
            "error": "word_limit_exceeded",
            "words_needed": total_words,
            "words_available": user['word_limit'] - user['words_used_this_month'],
            "upgrade_url": "/en/pricing.html"
        }
    )
```

**Prioridad:** 🔴 CRÍTICA

---

#### 2. **Mensajes de Error Técnicos**
**Problema:** Errores muestran stack traces o JSON crudo
**Ejemplo Actual:**
```
Error: HTTPException: 500 Internal Server Error
Detail: Translation failed: 'NoneType' object has no attribute 'translate'
```

**Solución - Humanizar Errores:**
```javascript
// frontend/public/assets/js/api.js

const ERROR_MESSAGES = {
  'word_limit_exceeded': {
    title: 'Word Limit Exceeded',
    message: 'You don\'t have enough words in your plan for this translation.',
    action: 'Upgrade Plan',
    icon: '⚠️'
  },
  'invalid_url': {
    title: 'Invalid Website URL',
    message: 'Please enter a valid website URL starting with http:// or https://',
    action: 'Try Again',
    icon: '🔗'
  },
  'crawl_failed': {
    title: 'Website Not Accessible',
    message: 'We couldn\'t access this website. It may be down or blocking our crawler.',
    action: 'Contact Support',
    icon: '🚫'
  },
  'translation_failed': {
    title: 'Translation Failed',
    message: 'Something went wrong during translation. Please try again or contact support.',
    action: 'Retry',
    icon: '❌'
  },
  'auth_required': {
    title: 'Please Log In',
    message: 'Your session has expired. Please log in again to continue.',
    action: 'Log In',
    icon: '🔐'
  }
};

function handleAPIError(error) {
  const errorCode = error.detail?.error || 'unknown';
  const errorConfig = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES['translation_failed'];

  showModal({
    title: errorConfig.title,
    message: errorConfig.message,
    icon: errorConfig.icon,
    buttons: [
      {
        text: errorConfig.action,
        onClick: () => handleErrorAction(errorCode)
      },
      {
        text: 'Cancel',
        style: 'secondary'
      }
    ]
  });
}
```

**Prioridad:** 🔴 CRÍTICA

---

#### 3. **No Hay Confirmación Antes de Acciones Destructivas**
**Problema:** Usuario puede eliminar proyecto sin confirmación
**Ubicación:** `frontend/public/en/dashboard.html`

**Solución:**
```javascript
// Agregar modal de confirmación
function deleteProject(projectId) {
  showConfirmModal({
    title: 'Delete Project?',
    message: 'This action cannot be undone. All translation data will be permanently deleted.',
    confirmText: 'Delete',
    confirmStyle: 'danger',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        await fetch(`${API_URL}/api/projects/${projectId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        showToast('Project deleted successfully', 'success');
        loadProjects();
      } catch (error) {
        showToast('Failed to delete project', 'error');
      }
    }
  });
}
```

**Prioridad:** 🟠 ALTA

---

### ALTOS (Afectan UX Significativamente)

#### 4. **Loading States Pobres**
**Problema:** Solo spinner genérico, no muestra progreso real
**Ubicación:** `frontend/public/en/translate.html`

**Estado Actual:**
```html
<div id="loading" class="hidden">
  <div class="spinner"></div>
  <p>Translating...</p>
</div>
```

**Mejora - Skeleton Screen + Progreso Real:**
```html
<div id="translation-progress" class="hidden">
  <!-- Progress bar -->
  <div class="progress-container">
    <div class="progress-bar">
      <div class="progress-fill" id="progress-fill"></div>
    </div>
    <p class="progress-text">
      <span id="progress-percent">0</span>% complete
    </p>
  </div>

  <!-- Lista de páginas con estados -->
  <div class="pages-status">
    <div class="page-status" data-status="completed">
      ✅ index.html → Translated (500 words)
    </div>
    <div class="page-status" data-status="in-progress">
      ⏳ about.html → Translating... (300 words)
    </div>
    <div class="page-status" data-status="pending">
      ⏹️ contact.html → Pending (150 words)
    </div>
  </div>

  <!-- Estadísticas -->
  <div class="translation-stats">
    <p>Words translated: <strong><span id="words-done">500</span> / <span id="words-total">2500</span></strong></p>
    <p>Estimated time remaining: <span id="time-remaining">2 minutes</span></p>
  </div>

  <!-- Tip aleatorio -->
  <div class="translation-tip">
    💡 <span id="random-tip">We're using DeepL AI for professional translations</span>
  </div>
</div>
```

**CSS:**
```css
.page-status {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.page-status[data-status="completed"] {
  background: #D1FAE5;
  color: #065F46;
}

.page-status[data-status="in-progress"] {
  background: #DBEAFE;
  color: #1E40AF;
  animation: pulse 2s ease-in-out infinite;
}

.page-status[data-status="pending"] {
  background: #F3F4F6;
  color: #6B7280;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

**Prioridad:** 🟠 ALTA

---

#### 5. **Dashboard No Muestra Próximo Reset**
**Problema:** Usuario no sabe cuándo se resetean sus palabras
**Ubicación:** `frontend/public/en/dashboard.html`

**Solución:**
```javascript
// Calcular próximo reset (1er día del próximo mes)
function getNextResetDate() {
  const now = new Date();
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return nextMonth.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });
}

// Agregar a HTML del dashboard
<div class="word-usage-card">
  <h3>Word Usage</h3>
  <div class="usage-bar">
    <div class="usage-fill" style="width: 96%"></div>
  </div>
  <p>4,800 / 5,000 words (96%)</p>
  <small class="text-secondary">
    Resets on <strong>${getNextResetDate()}</strong>
  </small>
</div>
```

**Prioridad:** 🟠 ALTA

---

#### 6. **No Hay Alertas de Uso**
**Problema:** Usuario no recibe warning cuando se acerca al límite
**Solución:** Agregar alertas en 80%, 90%, 95%

```javascript
// En dashboard.html
function checkWordUsageAlerts(used, limit) {
  const percentage = (used / limit) * 100;

  if (percentage >= 95 && !localStorage.getItem('alert_95_shown')) {
    showToast({
      message: '⚠️ You\'ve used 95% of your words! Upgrade to continue.',
      type: 'warning',
      duration: 10000,
      action: {
        text: 'Upgrade',
        onClick: () => window.location.href = '/en/pricing.html'
      }
    });
    localStorage.setItem('alert_95_shown', 'true');
  } else if (percentage >= 90 && !localStorage.getItem('alert_90_shown')) {
    showToast({
      message: 'You\'ve used 90% of your monthly words.',
      type: 'warning',
      duration: 5000
    });
    localStorage.setItem('alert_90_shown', 'true');
  } else if (percentage >= 80 && !localStorage.getItem('alert_80_shown')) {
    showToast({
      message: 'You\'ve used 80% of your monthly words.',
      type: 'info',
      duration: 5000
    });
    localStorage.setItem('alert_80_shown', 'true');
  }
}

// Reset alerts al inicio de mes
function resetAlerts() {
  const now = new Date();
  const lastReset = localStorage.getItem('alerts_reset_month');
  const currentMonth = `${now.getFullYear()}-${now.getMonth()}`;

  if (lastReset !== currentMonth) {
    localStorage.removeItem('alert_80_shown');
    localStorage.removeItem('alert_90_shown');
    localStorage.removeItem('alert_95_shown');
    localStorage.setItem('alerts_reset_month', currentMonth);
  }
}
```

**Prioridad:** 🟠 ALTA

---

### MEDIOS (Mejoran UX)

#### 7. **Sin Toast Notifications**
**Problema:** Acciones exitosas no dan feedback visual claro

**Solución - Sistema de Toasts:**
```javascript
// frontend/public/assets/js/toast.js

const Toast = {
  show(message, type = 'info', duration = 3000, options = {}) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      ${this.getIcon(type)}
      <span class="toast-message">${message}</span>
      ${options.action ? `<button class="toast-action">${options.action.text}</button>` : ''}
      <button class="toast-close">×</button>
    `;

    document.body.appendChild(toast);

    // Animación de entrada
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto-close
    const autoClose = setTimeout(() => this.close(toast), duration);

    // Event listeners
    toast.querySelector('.toast-close')?.addEventListener('click', () => {
      clearTimeout(autoClose);
      this.close(toast);
    });

    if (options.action) {
      toast.querySelector('.toast-action')?.addEventListener('click', () => {
        options.action.onClick();
        this.close(toast);
      });
    }
  },

  getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return `<span class="toast-icon">${icons[type]}</span>`;
  },

  close(toast) {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }
};

// CSS
```css
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transform: translateY(100px);
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 9999;
  max-width: 400px;
}

.toast.show {
  transform: translateY(0);
  opacity: 1;
}

.toast-success {
  border-left: 4px solid #10B981;
}

.toast-error {
  border-left: 4px solid #EF4444;
}

.toast-warning {
  border-left: 4px solid #F59E0B;
}

.toast-info {
  border-left: 4px solid #3B82F6;
}

.toast-icon {
  font-size: 1.25rem;
  font-weight: bold;
}

.toast-message {
  flex: 1;
  font-size: 0.875rem;
  color: #374151;
}

.toast-action {
  background: transparent;
  border: none;
  color: #0EA5E9;
  font-weight: 500;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.toast-action:hover {
  text-decoration: underline;
}

.toast-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #9CA3AF;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.toast-close:hover {
  color: #374151;
}
```

**Uso:**
```javascript
// Ejemplos de uso
Toast.show('Project deleted successfully', 'success');
Toast.show('Failed to save changes', 'error');
Toast.show('Translation in progress...', 'info', 5000);
Toast.show('You\'ve used 90% of your words', 'warning', 10000, {
  action: {
    text: 'Upgrade',
    onClick: () => window.location.href = '/en/pricing.html'
  }
});
```

**Prioridad:** 🟡 MEDIA

---

#### 8. **Preview de Páginas No Muestra Contenido**
**Problema:** Solo muestra URL, no da contexto de qué página es
**Ubicación:** Resultados de análisis en `translate.html`

**Mejora:**
```html
<!-- En lugar de solo URL y palabras -->
<div class="page-preview">
  <div class="page-header">
    <span class="page-icon">🏠</span>
    <div>
      <h4 class="page-title">Homepage</h4>
      <p class="page-url">https://example.com/</p>
    </div>
    <span class="page-words">500 words</span>
  </div>

  <!-- Expandible para ver extracto -->
  <button class="expand-btn" onclick="togglePreview(this)">
    Show preview ▼
  </button>

  <div class="page-content hidden">
    <h5>Content Preview:</h5>
    <p class="text-excerpt">
      Welcome to Example Company. We provide the best services...
    </p>
    <ul class="elements-list">
      <li>1 × &lt;title&gt;</li>
      <li>1 × &lt;meta description&gt;</li>
      <li>3 × &lt;h1&gt;</li>
      <li>8 × &lt;h2&gt;</li>
      <li>24 × &lt;p&gt;</li>
    </ul>
  </div>
</div>
```

**Prioridad:** 🟡 MEDIA

---

## 🎯 MEJORAS REQUERIDAS (Priorizado)

### Semana 1: Críticas

| Mejora | Ubicación | Tiempo | Prioridad |
|--------|-----------|--------|-----------|
| Validación límite de palabras ANTES de traducir | `projects.py:210` | 2h | 🔴 CRÍTICA |
| Mensajes de error humanizados | `api.js` | 3h | 🔴 CRÍTICA |
| Modal de confirmación para acciones destructivas | `dashboard.html` | 2h | 🔴 CRÍTICA |
| Toast notification system | Crear `toast.js` | 4h | 🟠 ALTA |
| Loading states con progreso real | `translate.html` | 5h | 🟠 ALTA |

**Total:** 16 horas (2 días)

---

### Semana 2: Altas

| Mejora | Ubicación | Tiempo | Prioridad |
|--------|-----------|--------|-----------|
| Mostrar fecha de próximo reset | `dashboard.html` | 1h | 🟠 ALTA |
| Alertas de uso (80%, 90%, 95%) | `dashboard.html` | 2h | 🟠 ALTA |
| Preview de páginas con contenido | `translate.html` | 3h | 🟡 MEDIA |
| Skeleton screens | Todos los componentes | 4h | 🟡 MEDIA |
| Validación inline en formularios | Todos los forms | 3h | 🟡 MEDIA |

**Total:** 13 horas (1.5 días)

---

### Semana 3: Medias

| Mejora | Ubicación | Tiempo | Prioridad |
|--------|-----------|--------|-----------|
| Gráficos de uso interactivos | `dashboard.html` | 4h | 🟡 MEDIA |
| Historial de traducciones | Crear `history.html` | 5h | 🟡 MEDIA |
| Búsqueda y filtros en proyectos | `dashboard.html` | 3h | 🟡 MEDIA |
| Temas personalizables | `dark-mode.js` | 3h | 🟢 BAJA |
| Animaciones micro-interactions | CSS global | 2h | 🟢 BAJA |

**Total:** 17 horas (2 días)

---

## 📝 CONCLUSIÓN

### Fortalezas del Diseño Actual
✅ Sistema de colores coherente y profesional
✅ Dark mode bien implementado (Notion style)
✅ Tipografía clara y legible (IBM Plex Sans)
✅ Espaciado consistente (escala 4px)
✅ Componentes base bien definidos

### Debilidades Críticas
❌ Límites de palabras no se validan (riesgo financiero)
❌ Mensajes de error técnicos no user-friendly
❌ Loading states pobres (solo spinner)
❌ Sin confirmaciones para acciones destructivas
❌ No hay feedback visual claro (toasts/snackbars)

### Prioridades de Implementación
1. **Semana 1:** Críticas + validación de límites
2. **Semana 2:** Mejoras de UX + alertas
3. **Semana 3:** Pulido + animaciones

**Tiempo total estimado:** 46 horas (6 días laborables)

---

**Documento creado:** 20 de Octubre de 2025
**Próxima revisión:** Después de implementar mejoras de Semana 1
**Nivel de detalle:** MUY ALTO (basado en código real y análisis UX completo)
