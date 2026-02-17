# Prompt Completo para Generación del Proyecto "Salud Control"

Este documento contiene el prompt detallado para guiar a una IA en la construcción del sistema "Salud Control" con sus funcionalidades actuales.

---

## Rol
Actúa como un Experto Desarrollador Full Stack Senior especializado en aplicaciones de salud, arquitectura de microservicios, y soluciones impulsadas por IA. Tu objetivo es construir "Salud Control", una plataforma integral para el monitoreo y gestión de la salud personal.

## Objetivo del Proyecto
Crear una aplicación web y un bot de Telegram integrados que permitan a los usuarios registrar, visualizar y analizar sus métricas de salud (peso, presión, glucosa), alimentación, ejercicio y documentos clínicos. El sistema debe utilizar IA (Gemini) para interpretar descripciones de texto e imágenes de comidas y ejercicios.

## Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.12+
- **Framework:** FastAPI
- **ORM:** SQLModel (con Pydantic power)
- **Base de Datos:** PostgreSQL 16
- **IA:** Google Generative AI (Gemini 2.5 Flash)
- **Bot:** Python-Telegram-Bot
- **Autenticación:** JWT (JSON Web Tokens) con hashing de contraseñas (bcrypt).

### Frontend
- **Framework:** React 19 (Vite)
- **Lenguaje:** TypeScript
- **Estilos:** Tailwind CSS v4
- **Estado Global:** Zustand
- **Cliente HTTP:** Axios
- **Iconos:** Lucide React
- **Gráficos:** Recharts
- **Router:** React Router Dom v7

### Infraestructura
- **Contenerización:** Docker Compose
- **Servicios:** Backend (API), Frontend (Nginx/Vite preview), Base de datos (Postgres), Telegram Bot (servicio worker separado).

## Base de Datos (Schema)

El sistema debe tener las siguientes tablas principales (definidas con SQLModel):

1.  **User**:
    *   `id`, `username`, `email`, `password_hash`, `role` (ADMIN/USER).
    *   `telegram_chat_id` (int, opcional), `telegram_auth_token` (string, opcional) para vinculación.
    *   Relaciones a todos los registros de salud.

2.  **Métricas de Salud**:
    *   `WeightRecord`: `id`, `user_id`, `weight` (float), `fecha_hora`, `notes`.
    *   `BloodPressureRecord`: `id`, `user_id`, `systolic` (int), `diastolic` (int), `heart_rate`, `fecha_hora`.
    *   `GlucoseRecord`: `id`, `user_id`, `glucose_level` (float), `measurement_type` (ayuno/postprandial), `fecha_hora`.

3.  **Alimentación (FoodRecord)**:
    *   `id`, `user_id`, `description`, `fecha_hora`.
    *   `meal_type`: Enum (desayuno, merienda_manana, almuerzo, merienda_tarde, cena, merienda_postcena). **Nota Crítica:** Usar `sa_type=AutoString` para compatibilidad con Postgres y Enums de Python.
    *   Nutrientes calculados por IA: `calories`, `protein`, `carbs`, `fat`.
    *   `image_url` (opcional).

4.  **Ejercicio (ExerciseRecord)**:
    *   `id`, `user_id`, `exercise_type`, `fecha_hora`.
    *   `duration_minutes` (int), `calories_burned` (int).
    *   `intensity`: Enum (baja, media, alta). Usar `sa_type=AutoString`.

5.  **Documentos (ClinicalDocument)**:
    *   `id`, `user_id`, `title`, `file_path`, `notes`, `fecha_hora`.
    *   `document_type`: Enum (receta, laboratorio, estudio, imagen). Usar `sa_type=AutoString`.

## Funcionalidades Clave

### 1. Autenticación y Usuarios
- Registro e inicio de sesión con JWT.
- Endpoint `/auth/me` para obtener datos del usuario y estado de vinculación con Telegram.
- Sistema de vinculación de Telegram mediante token generado en web (`/auth/telegram-token`) y validado en el bot (`/start <token>`).
- Endpoint para desvincular Telegram.

### 2. Gestión de Salud (CRUD)
- Endpoints genéricos o específicos para registrar y listar Peso, Presión y Glucosa.
- Dashboard en Frontend con tarjetas KPI (último valor, tendencia) y gráficos históricos.

### 3. Registro de Alimentos con IA
- **Frontend:** Formulario para texto y subida de imágenes.
- **Backend:**
    - `POST /food/analyze`: Recibe texto, usa Gemini con prompt de nutricionista para retornar JSON estimado (calorías, macros, tipo de comida).
    - Lógica para subir imágenes, procesarlas con Gemini Vision y retornar estimación.
    - Persistencia en base de datos tras confirmación del usuario.

### 4. Registro de Ejercicios con IA
- Similar a alimentos.
- `POST /exercise/analyze` (texto) y `/exercise/analyze-image`.
- Gemini estima: tipo de ejercicio, duración (si no se especifica, por defecto o estimado), intensidad y calorías quemadas.

### 5. Documentos Clínicos
- Subida de archivos (PDF/Imágenes) con clasificación (Receta, Lab, etc.).
- Almacenamiento local en carpeta `uploads/`.

### 6. Bot de Telegram
- **Comandos:**
    - `/start <token>`: Vincula cuenta.
    - `/peso <val>`, `/presion <sis> <dia>`, `/glucosa <val>`: Registro rápido.
    - `/ejercicio <desc>`: Analiza y registra ejercicio.
    - `/desvincular`.
- **Mensajes de Texto:** Si el usuario envía texto libre, el bot asume que es comida, lo analiza con IA, muestra resumen de macros y pide confirmación ("Sí/No") con teclado inline o reply keyboard.
- **Imágenes:**
    - Si tiene caption "lab" o "receta", lo guarda como documento.
    - Si es comida (default), analiza imagen con IA y pide confirmación para guardar `FoodRecord`.
    - Si es ejercicio (caption "/ejercicio"), analiza imagen con IA.

### 7. Dashboard Web
- Diseño responsivo y moderno con Tailwind CSS.
- Gráficos interactivos (Recharts) para:
    - Evolución de peso.
    - Presión arterial (dos líneas: sistólica/diastólica).
    - Glucosa.
    - Distribución de macros del día actual (Pie Chart o Bar Chart).
- Resumen de salud generado por IA (`/analysis/summary`) que lee los últimos 5 registros de cada métrica y da un veredicto en lenguaje natural.

## Detalles de Implementación Importantes

- **Prompts de IA:** Deben ser robustos, instruyendo a Gemini a retornar **SOLAMENTE JSON** válido para facilitar el parsing. Incluir manejo de errores si la IA no puede interpretar la entrada.
- **Manejo de Enums:** En SQLAlchemy/SQLModel, asegurar que los Enums se guarden como strings simples en la base de datos para evitar problemas de tipos, especialmente si se comparten definiciones entre modelos.
- **Seguridad:** Variables de entorno para credenciales (DB, JWT Secret, Gemini API Key, Telegram Token).

## Estructura de Carpetas Sugerida

.
├── backend/
│   ├── app/
│   │   ├── auth/ (jwt, hash, dependencies)
│   │   ├── services/ (ai_service.py)
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── endpoints.py
│   ├── run_bot.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/ (authStore, healthStore)
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
└── compose.yaml
