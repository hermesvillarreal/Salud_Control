# Guía de Despliegue: Salud Control (100% Gratis)
**Proyecto:** Salud Control (Neon + Render + Cloudflare Pages)

Esta guía detalla los pasos y ajustes técnicos específicos para desplegar la aplicación Salud Control de forma gratuita y profesional.

---

## 1. Base de Datos: Neon.tech (PostgreSQL)
Neon ofrece una DB serverless que escala a cero cuando no se usa.

### Pasos:
1. Crear un proyecto en [Neon.tech](https://neon.tech).
2. Seleccionar **Postgres 16** (para coincidir con tu `compose.yaml`).
3. Elegir la región más cercana (ej: `AWS US-East-1 N. Virginia`).
4. **IMPORTANTE:** Copiar la "Connection String" con el modo **Pooled Connection** activo.
   - Debe lucir así: `postgresql://user:pass@ep-cool-name...neon.tech/neondb?sslmode=require`
   - *Ajuste técnico:* El parámetro `?sslmode=require` es obligatorio para que Render pueda conectarse.

---

## 2. Backend: Render.com (FastAPI)
Render hospeda el servicio de Python y la lógica de IA.

### Configuración del Servicio:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000` (Nota: el entry point es `app.main`)

### Variables de Entorno (Environment Variables):
- `DATABASE_URL`: La URL de conexión de Neon.
- `GEMINI_API_KEY`: Tu API Key de Google AI Studio.
- `SECRET_KEY`: Una cadena aleatoria larga para firmar los tokens JWT.
- `TZ`: `America/New_York` (o tu zona horaria local).

### Ajustes de Compatibilidad:
- **Bcrypt:** Si al registrarte recibes un error `TypeError: Unicode-objects must be encoded`, cambia en `requirements.txt` a `bcrypt==3.2.0` y `passlib[bcrypt]==1.7.4`.

---

## 3. Frontend: Cloudflare Pages (React + Vite)
Cloudflare sirve el sitio estático de forma global.

### Configuración de Despliegue:
- **Framework Preset:** `Vite`.
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Build output directory:** `dist`

### Variables de Entorno (Crucial):
- `VITE_API_URL`: La URL pública que te dio Render (ej: `https://salud-control-backend.onrender.com`). **Sin barra diagonal al final.**

---

## 4. Ajustes Globales de Arquitectura

### CORS (Cross-Origin Resource Sharing)
Verifica en `backend/app/main.py` que los CORS permitan el dominio de Cloudflare o usa `"*"` para pruebas iniciales:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir que Cloudflare hable con Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Manejo de Fecha Local
Se utiliza `datetime.now()` en los modelos para capturar la hora local según la variable `TZ` del servidor.

### Telegram Bot
El bot de Telegram está configurado para desarrollo local en el `compose.yaml`. En el despliegue de producción gratuito de Render, el bot no se ejecuta por defecto (ya que usamos un comando de inicio específico para la API). Si deseas el bot en producción, este requeriría un servicio de tipo "Background Worker" o configurar un Webhook.

---

## 5. Desarrollo Local (Docker)
Para trabajar de forma segura:

### Pasos:
1. Asegúrate de tener el archivo `.env` en la raíz con:
   ```env
   POSTGRES_USER=salud_user
   POSTGRES_PASSWORD=salud_password
   POSTGRES_DB=salud_control
   GEMINI_API_KEY=tu_clave_aqui
   ```
2. Levantar servicios:
   ```bash
   docker-compose up -d --build
   ```
3. Acceso:
   - Frontend: [http://localhost:84](http://localhost:84)
   - Backend API: [http://localhost:8004](http://localhost:8004)

---

## 6. Migración de Datos (Local -> Neon)
### Exportar desde Local:
```bash
docker exec -t salud-control-db pg_dump -U salud_user salud_control > backup_salud.sql
```
### Importar a Neon:
```bash
psql "tu_connection_string_de_neon" < backup_salud.sql
```

---

## 7. Notas de la Versión Gratuita
- **Render Spin-down:** El Backend tardará unos ~50 segundos en despertar si no se ha usado en 15 minutos.
- **Neon Sleep:** La base de datos también entra en reposo si no hay conexiones activas.
- **Límite de Horas:** Render ofrece 750 horas al mes. Con una sola aplicación activa no hay problema; con dos, se debe vigilar que entren en reposo cuando no se usen.
