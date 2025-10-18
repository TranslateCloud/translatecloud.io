# TranslateCloud - Backend

Sistema de traducción profesional de sitios web con IA.

## 🚀 Quick Start

### Prerequisitos
- Python 3.10+
- Conda/Miniconda
- AWS CLI configurado
- GPU (opcional, recomendado para producción)

### Instalación

\\\ash
# Crear entorno
conda create -n translatecloud python=3.10
conda activate translatecloud

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar tests
pytest
\\\

## 📁 Estructura

\\\
backend/
├── src/
│   ├── core/              # Lógica core de traducción
│   │   ├── marian_translator.py
│   │   ├── web_extractor.py
│   │   └── html_reconstructor.py
│   ├── functions/         # Lambda functions
│   ├── utils/             # Utilidades
│   ├── config/            # Configuración
│   └── tests/             # Tests unitarios
├── requirements.txt
└── README.md
\\\

## 🧪 Testing

\\\ash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src

# Tests específicos
pytest src/tests/test_translator.py
\\\

## 📝 Documentación

Ver carpeta /docs para documentación completa.
