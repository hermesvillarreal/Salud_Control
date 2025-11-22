# Salud Control - Sistema de Monitoreo de Salud

Sistema integrado para el seguimiento y análisis de indicadores de salud personal, con una interfaz web moderna (PWA) y capacidades de análisis con IA.

## 📱 Características Implementadas

- **Aplicación Web (PWA)**
  - Dashboard interactivo con gráficas de Plotly
  - Registro de Peso, Presión Arterial y Glucosa
  - **Registro de Alimentos con IA**: Describe tu comida y la IA calculará los macronutrientes automáticamente.
  - **Análisis de Salud con IA**: Obtén un resumen y recomendaciones basadas en tus datos históricos.
  - Diseño responsive y moderno
  - Autenticación de usuarios segura

## 🛠️ Requisitos del Sistema

- Python 3.8 o superior
- Navegador web moderno
- Conexión a Internet (para funciones de IA)
- API Key de Google Gemini (para análisis con IA)

## 📋 Indicadores de Salud Monitoreados

- Peso corporal
- Presión arterial (sistólica/diastólica)
- Niveles de glucosa en sangre
- Registro de alimentos (Proteínas, Carbohidratos, Grasas, Calorías)

## 🚀 Instalación y Configuración

### 1. Preparación del Entorno

```powershell
# Clonar el repositorio
git clone https://github.com/hermesvillarreal/Salud_Control.git
cd Salud_Control

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración del Archivo .env

1. Copiar el archivo de ejemplo:
```powershell
copy .env.example .env
```

2. Editar el archivo `.env` con tus configuraciones:
```plaintext
# API Key de Google Gemini (Requerido para funciones de IA)
GEMINI_API_KEY=tu_api_key_aquí

# Clave secreta para sesiones de Flask
SECRET_KEY=una_clave_secreta_segura
```

## 💻 Uso de la Aplicación

1. Iniciar el servidor web:
```powershell
cd desktop_app
python app.py
```
O ejecutar el script `run_web_app.bat` en la raíz.

2. Acceder al panel de control:
- Abrir el navegador en `http://localhost:5000`
- Registrarse o iniciar sesión
- Empezar a registrar datos

## 🐳 Despliegue con Docker

El proyecto incluye configuración para despliegue rápido usando Docker Compose.

### Requisitos
- Docker y Docker Compose instalados

### Pasos
1. Asegúrate de tener el archivo `.env` configurado.
2. Ejecuta:
```bash
docker-compose up -d --build
```
3. La aplicación estará disponible en `http://localhost:5000`.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.