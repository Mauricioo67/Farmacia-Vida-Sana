# 💊 Farmacia Vida Sana - Gestión Profesional & POS

Sistema integral de gestión farmacéutica y Punto de Venta (POS) desarrollado bajo estándares modernos con **Python Flask** y **Supabase**. El sistema combina una interfaz de usuario premium con inteligencia artificial para optimizar las operaciones de venta y control de inventario.

---

## 🌟 Características Destacadas

### 🛒 Punto de Venta (POS) Avanzado
- **Multi-Pago**: Soporte para cobros en **Efectivo** (con cálculo automático de cambio) y **Pagos QR / Transferencias**.
- **Moneda Local**: Totalmente adaptado a **Bolivianos (Bs.)** en recibos, dashboard y reportes.
- **Validación Robusta**: Control de stock en tiempo real y prevención de ventas sin existencias.
- **Recibos Profesionales**: Generación de facturas PDF automatizadas con ReportLab.

### 🤖 Asistente Inteligente (Chatbot RAG)
- **Contexto en Tiempo Real**: Capacidad de consultar el inventario, precios y existencias mediante lenguaje natural.
- **Motor Groq LLaMA 3.3**: Respuestas rápidas y precisas impulsadas por inteligencia artificial de vanguardia.
- **Sugerencias de Productos**: Ayuda al vendedor a encontrar artículos por nombre, código o categoría.

### 📊 Dashboard & Analítica Modernos
- **Visualización de Datos**: Gráficas dinámicas de tendencia de ventas diarias con **Chart.js**.
- **Métricas Clave**: Seguimiento instantáneo de Ventas Hoy, Productos Bajos en Stock y Clientes.
- **Interfaz UI/UX Premium**: Diseño responsivo con efectos de **Glassmorphism**, animaciones fluidas y soporte nativo para **Modo Oscuro/Claro**.

---

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.10+ & Flask.
- **Base de Datos**: Supabase (PostgreSQL) con consultas optimizadas.
- **Inteligencia Artificial**: Groq Cloud API & LangChain (RAG).
- **Frontend**: HTML5, Jinja2, Bootstrap 5, Vanilla JS (ES6+).
- **DevOps & CI/CD**: 
  - **GitHub Actions**: Pipeline automatizado para pruebas (`pytest`).
  - **Render**: Despliegue en la nube con soporte para Gunicorn.

---

## 🛡️ Seguridad y Robustez

- **Autenticación**: Manejo seguro de sesiones y perfiles de usuario.
- **Protección de Datos**: Configuración de `.gitignore` para secretos y cumplimiento de RLS en base de datos.
- **Integridad**: Capa de abstracción de datos personalizada para manejar operaciones atómicas en Supabase.

---

## 🚀 Guía de Instalación Rápida

1. **Clonar**: `git clone https://github.com/Mauricioo67/Farmacia-Vida-Sana.git`
2. **Entorno**: `python -m venv venv` -> `source venv/Scripts/activate`
3. **Dependencias**: `pip install -r requirements.txt`
4. **Variables**: Configurar `.env` con las llaves de Supabase y Groq.
5. **Ejecutar**: `python app.py`

---

## ☁️ Despliegue (Production Ready)

El sistema incluye archivos de configuración para despliegue inmediato:
- **`Procfile`**: Configurado para Render/Heroku.
- **`.github/workflows/ci.yml`**: Pruebas automáticas en cada push.
- **`GUIA_DESPLIEGUE.txt`**: Manual paso a paso en español para el administrador.

---

> **Nota de Desarrollo**: Este proyecto representa la evolución de un sistema legacy hacia una arquitectura moderna, escalable y centrada en el usuario.

**Desarrollado para la eficiencia farmacéutica.** 🏥✨
