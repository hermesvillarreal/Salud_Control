# Prompts para Recreación del Proyecto "Salud Control"

Este documento contiene una serie de prompts diseñados para crear el proyecto "Salud Control" con una arquitectura moderna (FastAPI + React), basada en las mejores prácticas analizadas. Usa estos prompts en orden con un asistente de IA.

## Prompt 1: Inicialización del Proyecto y Definición del Stack

**Objetivo:** Configurar la estructura del proyecto y definir el stack tecnológico para "Salud Control".

**Prompt:**
```text
Quiero iniciar un nuevo proyecto de aplicación web llamado "Salud Control".
**Objetivo del Proyecto:** "Salud Control - Sistema de Monitoreo de Salud".
El sistema debe permitir el registro y monitoreo de indicadores de salud (peso, presión, glucosa), registro de alimentos y ejercicios asistido por IA (Gemini), y gestión de documentos clínicos (recetas, laboratorios).

Por favor, configura la estructura del proyecto con el siguiente stack tecnológico:

**Backend:**
- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **Base de Datos:** PostgreSQL (usando `psycopg2-binary`)
- **ORM:** SQLModel
- **Autenticación:** JWT (usando `python-jose`, `passlib`)
- **IA:** Google Generative AI (`google-generativeai`) para análisis de alimentos y salud.
- **Otros:** `uvicorn` para servir, `python-telegram-bot` para notificaciones.

**Frontend:**
- **Framework:** React 19
- **Herramienta de Build:** Vite
- **Lenguaje:** TypeScript
- **Estilos:** Tailwind CSS (con `postcss`, `autoprefixer`, `clsx`, `tailwind-merge`)
- **Iconos:** Lucide React
- **Manejo de Estado:** Zustand
- **Rutas:** React Router DOM
- **Cliente HTTP:** Axios
- **Gráficos:** Recharts (para visualización de indicadores)

**Infraestructura:**
- Docker y Docker Compose para orquestar Backend, Frontend y Base de Datos.

**Estructura de Directorios:**
- `backend/` (App FastAPI)
- `frontend/` (App React)
- `compose.yaml` (Configuración de Docker Compose)

Por favor crea la estructura de archivos inicial, `backend/requirements.txt`, `frontend/package.json`, y un `compose.yaml` básico para levantar los servicios incluyendo un contenedor de PostgreSQL.
```

---

## Prompt 2: Esquema de Base de Datos y Autenticación

**Objetivo:** Definir los modelos de datos de salud y configurar la autenticación.

**Prompt:**
```text
Ahora definamos los modelos de datos y la autenticación.

1.  **Modelos (`backend/app/models.py`):**
    -   Usa **SQLModel**.
    -   **User:** `id`, `username`, `email`, `full_name`, `password_hash`, `role` (ADMIN, USER), `created_at`.
    -   **WeightRecord:** `id`, `user_id`, `date`, `weight` (float), `notes`.
    -   **BloodPressureRecord:** `id`, `user_id`, `date`, `systolic` (int), `diastolic` (int), `heart_rate` (int, opcional), `notes`.
    -   **GlucoseRecord:** `id`, `user_id`, `date`, `glucose_level` (float), `measurement_type` (e.g., ayuno, postprandial), `notes`.
    -   **FoodRecord:** `id`, `user_id`, `date` (datetime), `meal_type` (desayuno, almuerzo, cena, merienda_manana, merienda_tarde, merienda_noche), `description` (texto), `calories` (int), `protein` (float), `carbs` (float), `fat` (float), `image_url` (opcional).
    -   **ExerciseRecord:** `id`, `user_id`, `date`, `exercise_type`, `duration_minutes`, `calories_burned`, `intensity` (baja, media, alta).
    -   **ClinicalDocument:** `id`, `user_id`, `date`, `title`, `document_type` (receta, laboratorio, imagen), `file_path`, `notes`.

2.  **Conexión a Base de Datos (`backend/app/database.py`):**
    -   Configura `create_engine` y `get_session`.

3.  **Autenticación (`backend/app/auth/`):**
    -   Implementa JWT (`jwt_utils.py` y `dependencies.py`).
    -   Función para hashear contraseñas.

Genera el código para estos archivos.
```

---

## Prompt 3: Lógica Central del Backend e Integración IA

**Objetivo:** Implementar endpoints CRUD y servicios de IA con Gemini.

**Prompt:**
```text
Implementemos la lógica del backend incluyendo la integración con IA.

1.  **Configuración de IA (`backend/app/services/ai_service.py`):**
    -   Configura `google.generativeai` usando `GEMINI_API_KEY`.
    -   Crea función `analyze_food_text(description: str)`: Retorna JSON con macronutrientes estimados.
    -   Crea función `analyze_health_summary(user_history: dict)`: Genera un resumen de salud y recomendaciones basado en el historial del usuario.

2.  **Endpoints (`backend/app/endpoints.py`):**
    -   **Auth:** Login, Register.
    -   **Health Metrics:** CRUD completo para `WeightRecord`, `BloodPressureRecord`, `GlucoseRecord`.
    -   **Food & Exercise:**
        -   POST `/food/analyze`: Recibe texto, usa `ai_service`, retorna macros estimados.
        -   POST `/food/log`: Guarda el registro de comida (puede ser confirmado tras el análisis).
        -   CRUD para `ExerciseRecord`.
    -   **Clinical Docs:**
        -   POST `/documents/upload`: Recibe archivo, guarda en disco/volumen, crea registro `ClinicalDocument`.
        -   GET `/documents`: Lista documentos.
    -   **Dashboard/Analysis:**
        -   GET `/analysis/summary`: Obtiene estadísticas y llama a `analyze_health_summary` para veredictos de IA.

Genera el código para `ai_service.py` y `endpoints.py`.
```

---

## Prompt 4: Bot de Telegram para Registro Rápido

**Objetivo:** Integrar un bot de Telegram para registrar datos y subir fotos fácilmente.

**Prompt:**
```text
Vamos a integrar un Bot de Telegram para facilitar el registro de datos.

1.  **Configuración (`backend/run_bot.py`):**
    -   Usa `python-telegram-bot` en modo polling.
    -   El bot debe poder autenticar al usuario (ej: comando `/start <token>` generado en la web).

2.  **Funcionalidades del Bot:**
    -   `/peso <valor>`: Registra peso actual.
    -   `/presion <sis> <dia>`: Registra presión arterial.
    -   `/glucosa <valor>`: Registra glucosa.
    -   **Registro de Alimentos:** Al enviar un mensaje de texto normal o una foto de comida, el bot debe interactuar con `ai_service` para estimar macros y preguntar "¿Deseas registrar esto?".
    -   **Subida de Documentos:** Al enviar una foto o PDF con el caption "Lab" o "Receta", guardarlo como `ClinicalDocument`.

Genera el código para el bot y sus handlers.
```

---

## Prompt 5: Frontend - Store y API

**Objetivo:** Configurar estado global y cliente API.

**Prompt:**
```text
Configura el nucleo del Frontend.

1.  **API Client (`frontend/src/services/api.ts`):**
    -   Instancia de Axios con interceptores para JWT.
    -   Manejo de refresh token o redirección en error 401.

2.  **Stores (`frontend/src/stores/`):**
    -   `useAuthStore`: Token, User, Login/Logout.
    -   `useHealthStore`: Para cachear o manejar el estado de los indicadores si es necesario (o usar React Query/SWR si prefieres, pero Zustand está bien para empezar).

Implementa la configuración base.
```

---

## Prompt 6: Frontend - Dashboard y Gráficos

**Objetivo:** Crear el Dashboard principal con visualización de datos.

**Prompt:**
```text
Implementa el Dashboard principal (`frontend/src/pages/Dashboard.tsx`).

1.  **Diseño:**
    -   Usa un layout de Grid responsive con Tailwind.
    -   Tarjetas de resumen ("Tarjetas KPI") para: Peso Actual, Última Presión, Promedio Glucosa. debe tener un indicador de tendencia (sube/baja).

2.  **Gráficos (Recharts):**
    -   **Evolución de Peso:** Gráfico de línea.
    -   **Presión Arterial:** Gráfico de área o línea multiseries (Sistólica/Diastólica).
    -   **Glucosa:** Gráfico de línea con zonas de referencia (verde/rojo).
    -   **Macronutrientes Hoy:** Gráfico de pastel o barras para Proteína/Carbo/Grasa.

3.  **Acciones Rápidas:**
    -   Botones flotantes o en el header del dashboard para "Registrar Peso", "Registrar Comida", etc.

Genera el código componentes del Dashboard.
```

---

## Prompt 7: Frontend - Registro de Alimentos con IA

**Objetivo:** Interfaz para describir comidas y ver el análisis de IA.

**Prompt:**
```text
Implementa la página de Registro de Alimentos (`frontend/src/pages/FoodLog.tsx`).

1.  **Formulario Inteligente:**
    -   Text Area para describir la comida.
    -   Botón "Analizar con IA".
    -   Al hacer click, llama al backend `/food/analyze`.

2.  **Vista de Confirmación:**
    -   Muestra los macros estimados (Calorías, P, C, G) devueltos por la IA.
    -   Permite al usuario editar los valores si la IA falló.
    -   Botón "Guardar Registro".

3.  **Historial:**
    -   Lista de comidas del día debajo del formulario.

Genera el código para esta vista.
```

---

## Prompt 8: Frontend - Documentos Clínicos

**Objetivo:** Galería de documentos y subida de archivos.

**Prompt:**
```text
Implementa la sección de Documentos Clínicos (`frontend/src/pages/ClinicalDocs.tsx`).

1.  **Subida de Archivos:**
    -   Drag & Drop zone o Input file para imágenes/PDFs.
    -   Selector de tipo: "Receta", "Laboratorio", "Estudio".
    -   Campo de notas.

2.  **Galería:**
    -   Grid visualizando miniaturas de los documentos.
    -   Al hacer click, abrir modal con la imagen/PDF en grande.

Implementa esta funcionalidad.
```

---

## Prompt 9: Dockerización Final

**Objetivo:** Asegurar que todo correo junto.

**Prompt:**
```text
Genera/Actualiza la configuración final de Docker.

1.  Asegúrate de que `backend/Dockerfile` instale las dependencias de sistema necesarias para `psycopg2` y `python-telegram-bot`.
2.  Asegúrate de que `frontend/Dockerfile` construya la app de producción.
3.  Actualiza `compose.yaml` para incluir un volumen persistente para la carpeta de `uploads` (documentos clínicos) y mapearlo correctamente al contenedor del backend.

Genera los archivos finales.
```
