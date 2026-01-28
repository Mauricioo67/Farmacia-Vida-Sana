# Sistema de Farmacia - Python Flask + Supabase

Sistema completo de gestión para farmacias desarrollado con **Python Flask** y **Supabase** (PostgreSQL). Incluye punto de venta, gestión de inventario, reportes y chatbot con IA.

## 🚀 Características Principales

### ✅ Módulos Implementados

- **🔐 Autenticación**: Login seguro con sesiones
- **📊 Dashboard**: Estadísticas en tiempo real (ventas, productos, stock)
- **💊 Gestión de Productos**: CRUD completo con categorías
- **👥 Gestión de Clientes**: Registro y administración
- **🏷️ Categorías**: Organización de productos
- **💰 Punto de Venta (POS)**:
  - Búsqueda rápida de productos
  - Carrito dinámico con JavaScript
  - Control automático de stock
  - Generación de recibos PDF profesionales
  - Historial de ventas
- **📈 Reportes**:
  - Reporte de ventas con filtros de fecha
  - Reporte de inventario con niveles de stock
  - Estadísticas en tiempo real
- **🤖 Chatbot con IA**:
  - Asistente virtual powered by Groq API
  - Búsqueda inteligente de productos
  - Consultas de inventario en tiempo real
  - Respuestas en lenguaje natural

## 🛠 Tecnologías

- **Backend**: Python 3.x, Flask
- **Base de Datos**: Supabase (PostgreSQL)
- **Frontend**: HTML5, Jinja2, Bootstrap 5, JavaScript
- **PDF**: ReportLab
- **IA**: Groq API (LLaMA 3.3 70B)
- **Librerías**: `flask-cors`, `python-dotenv`, `supabase`, `reportlab`, `groq`

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd Farmacia/farmacia_python
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Edita el archivo `.env` y configura:

```env
# Supabase
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_key
SECRET_KEY=tu_secret_key

# Groq API (para chatbot)
GROQ_API_KEY=tu_groq_api_key
```

**Obtener credenciales:**
- Supabase: https://supabase.com/
- Groq API (gratis): https://console.groq.com/

### 5. Configurar base de datos

En el SQL Editor de Supabase, ejecuta:

1. `basededatos.sql` - Crea las tablas
2. `datoss.sql` - Datos de prueba (opcional)

## ▶️ Ejecución

```bash
python app.py
```

Accede a: **http://localhost:5000**

## 👤 Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: `mauricio1`

## 📁 Estructura del Proyecto

```
farmacia_python/
├── app.py                 # Aplicación principal
├── config.py             # Configuración
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno
├── controllers/          # Controladores (rutas)
│   ├── auth.py          # Autenticación
│   ├── main.py          # Dashboard
│   ├── products.py      # Productos
│   ├── clients.py       # Clientes
│   ├── categories.py    # Categorías
│   ├── sales.py         # Ventas y POS
│   ├── reports.py       # Reportes
│   └── chatbot.py       # Chatbot IA
├── models/              # Modelos
│   └── db.py           # Conexión a DB
├── templates/           # Vistas HTML
│   ├── base.html       # Template base
│   ├── auth/           # Login, registro
│   ├── main/           # Dashboard
│   ├── products/       # CRUD productos
│   ├── clients/        # CRUD clientes
│   ├── categories/     # CRUD categorías
│   ├── sales/          # POS e historial
│   └── reports/        # Reportes
└── static/             # Archivos estáticos
    ├── css/
    │   └── chatbot.css
    └── js/
        └── chatbot.js
```

## 🎯 Funcionalidades Destacadas

### Punto de Venta (POS)
- Interfaz intuitiva para ventas rápidas
- Búsqueda de productos en tiempo real
- Actualización automática de stock
- Generación de PDF con diseño profesional

### Reportes
- **Ventas**: Análisis por período con totales
- **Inventario**: Control de stock con alertas

### Chatbot IA
- Asistente virtual disponible en todas las páginas
- Búsqueda de productos por nombre
- Consultas de stock en tiempo real
- Respuestas contextuales sobre la farmacia

## 🔧 Desarrollo

### Agregar nuevos módulos

1. Crear controlador en `controllers/`
2. Crear templates en `templates/`
3. Registrar blueprint en `app.py`

### Base de datos

El proyecto usa Supabase con las siguientes tablas:
- `trabajador` - Usuarios del sistema
- `categoria` - Categorías de productos
- `articulo` - Productos
- `cliente` - Clientes
- `venta` - Ventas
- `detalle_venta` - Detalles de ventas

## 📝 Notas

- El chatbot requiere una API key de Groq (gratuita)
- Los PDFs se generan con ReportLab
- El sistema usa sesiones de Flask para autenticación
- Supabase maneja la persistencia de datos

## 🤝 Contribuciones

Este proyecto es una migración de un sistema legacy PHP a una arquitectura moderna con Python Flask.

## 📄 Licencia

Proyecto educativo/comercial para gestión de farmacias.
