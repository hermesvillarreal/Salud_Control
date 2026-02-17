# Salud Control - Sistema Integral de Monitoreo de Salud

**Salud Control** es una plataforma moderna diseñada para la autogestión y el monitoreo detallado de la salud personal. Combina una aplicación web intuitiva con un bot de Telegram, potenciados por Inteligencia Artificial (Google Gemini) para simplificar el registro de alimentos, ejercicios y métricas vitales.

---

## 1. Sección Funcional

### Objetivo del Proyecto
Proporcionar una herramienta centralizada que permita a los usuarios registrar, visualizar y analizar su estado de salud de manera fácil y rápida. El sistema busca eliminar la fricción del registro manual utilizando IA para interpretar fotos de comidas y descripciones de texto, ofreciendo insights inmediatos sobre nutrición y actividad física.

### Capacidades Principales

#### 📊 Monitoreo de Métricas de Salud
*   **Registro de Vitales:** Seguimiento de Peso, Presión Arterial (Sistólica/Diastólica) y Glucosa.
*   **Visualización:** Tablero (Dashboard) con tarjetas de resumen clínico y gráficos interactivos para ver tendencias históricas.
*   **Indicadores de Salud:** Feedback inmediato mediante colores y rangos médicos estándar.

#### 🍎 Registro de Alimentación con IA
*   **Análisis por Foto:** Sube una foto de tu plato y la IA estimará las calorías, proteínas, carbohidratos, grasas y tipo de comida.
*   **Entrada de Texto Natural:** Describe lo que comiste (ej: "licuado de banana con avena") y el sistema calculará los macros automáticamente.
*   **Historial:** Visualización diaria de comidas y totales nutricionales.

#### 🏋️ Registro de Ejercicios
*   **Interpretación Inteligente:** Analiza descripciones o fotos de tu actividad física para estimar calorías quemadas e intensidad.
*   **Clasificación:** Categorización automática del tipo de ejercicio y duración.

#### 🤖 Bot de Telegram Integrado
*   **Registro Rápido:** Envía comandos simples (`/peso 75`, `/glucosa 110`) sin abrir la app.
*   **Interacción Natural:** Manda una foto de tu comida o ejercicio al chat para registrarlo automáticamente.
*   **Vinculación Segura:** Sistema de tokens para conectar tu cuenta de Telegram con tu perfil web.

#### 🧮 Calculadoras de Salud
*   Herramientas integradas para calcular TDEE (Gasto Energético Total), BMI (Índice de Masa Corporal), Macros sugeridos y Riesgo Cardiovascular (ASCVD).

#### 📁 Gestión Documental
*   Almacenamiento digital de estudios clínicos, recetas y laboratorios en formato PDF o imagen.

---

## 2. Sección Técnica

Este proyecto utiliza una arquitectura moderna basada en microservicios contenerizados, priorizando el tipado estático, la seguridad y la escalabilidad.

### Arquitectura de Backend
*   **Framework:** FastAPI (Python 3.12+) - Alta performance y validación automática de datos.
*   **Base de Datos:** PostgreSQL 16 - Robusta y relacional.
*   **ORM:** SQLModel - Interacción moderna con SQL combinando Pydantic y SQLAlchemy.
*   **IA:** Google Generative AI (Gemini 2.5 Flash) - Motor de análisis multimodal.
*   **Bot:** Python-Telegram-Bot - Servicio worker dedicado para gestión de eventos de Telegram.
*   **Seguridad:** Autenticación JWT y hashing de contraseñas con Bcrypt.

### Arquitectura de Frontend
*   **Framework:** React 19 (Vite) - Rápido y modular.
*   **Lenguaje:** TypeScript - Tipado estricto para reducir errores en tiempo de ejecución.
*   **Estilos:** Tailwind CSS v4 - Diseño responsivo y sistema de diseño consistente.
*   **Estado:** Zustand - Gestión de estado global ligera y eficiente.
*   **Gráficos:** Recharts - Visualización de datos médicos.
*   **Cliente HTTP:** Axios - Con interceptores para manejo de tokens JWT.

### Infraestructura
*   **Docker Compose:** Orquestación de servicios (Frontend, Backend, DB, Bot).
*   **Nginx:** Servidor web para el frontend en producción.

---

## 3. FAQ y Solución de Problemas Comunes

### 🕒 Problemas de Zona Horaria
**P: ¿Por qué mis registros muestran una hora diferente a la que ingresé?**
**R:** El sistema utiliza fechas en formato ISO local para el registro (`YYYY-MM-DDTHH:mm`).
*   **Solución:** Asegúrate de que tu navegador/dispositivo tenga la zona horaria correcta. Hemos implementado utilidades (`dateUtils.ts`) que normalizan las fechas locales antes de enviarlas al servidor para evitar desajustes UTC involuntarios.

### 💾 Errores al Guardar Datos
**P: Recibo un error al intentar guardar un ejercicio o comida.**
**R:** Esto suele deberse a discrepancias en los valores permitidos (Enums) en la base de datos.
*   **Solución:**
    *   Para ejercicios: La base de datos espera intensidades en minúsculas (`baja`, `media`, `alta`). Si tienes una versión antigua de la DB, puede requerir una migración (ej: `ALTER TYPE intensitytype ...`).
    *   Para comidas: Los tipos de comida deben coincidir con las opciones predefinidas (ej: `almuerzo`, `cena`).

### 🐳 Docker y Despliegue
**P: El contenedor frontend falla al construir.**
**R:** Verifica que no haya conflictos de versiones en `npm`.
*   **Solución:** Revisa las importaciones de iconos (`lucide-react`); algunas versiones cambian el nombre de los iconos (ej: `Image` vs `ImageIcon`). Ejecuta `docker compose up -d --build frontend` para reconstruir con los últimos cambios.

### 🤖 El Bot no responde
**P: El bot de Telegram no contesta mis mensajes.**
**R:** El bot corre como un servicio separado (`telegram-bot`).
*   **Solución:** Verifica que el contenedor esté corriendo (`docker logs salud-control-bot`). Asegúrate de haber iniciado el chat con el comando `/start <token>` generado desde el dashboard web para vincular tu usuario.

---

### Cómo Iniciar

1.  **Clonar el repositorio.**
2.  **Configurar variables de entorno:** Crear `.env` basado en el ejemplo (API Keys de Gemini, Token de Telegram, Secretos de DB).
3.  **Ejecutar con Docker:**
    ```bash
    docker compose up -d --build
    ```
4.  **Acceder:**
    *   Web: `http://localhost:84`
    *   API Docs: `http://localhost:8004/docs`
