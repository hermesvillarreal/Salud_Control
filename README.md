# Salud Control - Sistema de Monitoreo de Salud

Sistema integrado para el seguimiento y análisis de indicadores de salud personal, con una interfaz de escritorio para visualización y una aplicación de registro local.

## 📱 Características Implementadas

- **Aplicación de Registro (PyQt5)**
  - Registro fácil de indicadores de salud
  - Almacenamiento local con SQLite
  - Interfaz gráfica intuitiva
  - Exportación de datos en formato JSON
  - Sincronización con aplicación web

- **Aplicación Web de Visualización**
  - Visualización de datos con gráficas interactivas
  - Panel de control con estadísticas en tiempo real
  - Análisis estadístico básico de indicadores
  - Integración opcional con IA para recomendaciones
  - Interfaz web responsive

## 🛠️ Requisitos del Sistema

- Python 3.8 o superior
- Navegador web moderno
- Espacio en disco: ~50MB
- Conexión a Internet (para sincronización)
- API Key de OpenAI (opcional, solo para análisis con IA)

## 📋 Indicadores de Salud Monitoreados

- Peso corporal
- Presión arterial (sistólica/diastólica)
- Niveles de glucosa en sangre
- Notas y observaciones personales
- Fecha y hora de cada registro

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
# La API key de OpenAI es opcional
OPENAI_API_KEY=tu_api_key_aquí

# Configuración de bases de datos
DESKTOP_DB_PATH=desktop_health.db
MOBILE_DB_PATH=salud_control.db
```

## 💻 Uso de la Aplicación

### 1. Aplicación de Registro (GUI)

1. Iniciar la aplicación de registro:
```powershell
cd mobile_app
python main.py
```

2. Funcionalidades disponibles:
- Registro de datos de salud diarios
- Visualización de fecha y hora de registro
- Guardado automático en base de datos local
- Exportación de datos en formato JSON
- Sincronización con aplicación web

### 2. Aplicación Web de Visualización

1. Iniciar el servidor web:
```powershell
cd desktop_app
python app.py
```

2. Acceder al panel de control:
- Abrir el navegador en `http://localhost:5000`
- Las gráficas y estadísticas se actualizarán automáticamente
- Los análisis están disponibles en el panel principal

## 📊 Visualización y Análisis

### Gráficas Interactivas

- **Evolución del Peso**
  - Gráfica temporal de cambios en el peso
  - Visualización de tendencias a lo largo del tiempo

- **Presión Arterial**
  - Gráfica combinada sistólica/diastólica
  - Seguimiento temporal de ambas medidas

- **Niveles de Glucosa**
  - Monitoreo de glucosa en sangre
  - Visualización de tendencias y patrones

### Análisis de Datos

- **Análisis Básico**
  - Estadísticas descriptivas de cada indicador
  - Cálculo de promedios y tendencias
  - Identificación de patrones básicos

- **Análisis con IA (Opcional)**
  - Requiere API key de OpenAI
  - Recomendaciones personalizadas
  - Análisis detallado de tendencias

## 🔄 Sincronización de Datos

La sincronización entre la aplicación de registro y la web es simple:

1. En la aplicación de registro:
   - Ingresa tus datos de salud
   - Haz clic en "Guardar" para almacenamiento local
   - Usa "Sincronizar con Desktop" para enviar datos

2. En la aplicación web:
   - Los datos se actualizan automáticamente
   - Las gráficas se refrescan en tiempo real
   - El análisis se actualiza con nuevos datos

## � Exportación de Datos

1. Desde la aplicación de registro:
   - Usa el botón "Exportar"
   - Se genera un archivo JSON con todos los registros
   - El archivo incluye fecha y hora de cada registro

2. El archivo exportado contiene:
   - Historial completo de mediciones
   - Notas y observaciones
   - Timestamps de cada registro

## 🔒 Seguridad y Privacidad

- Almacenamiento local en SQLite
- Sin dependencia de servicios en la nube
- Sincronización local via HTTP
- Control total sobre tus datos

## 🔍 Solución de Problemas

### Problemas Comunes

1. **Error de Sincronización**
   - Verifica que ambas aplicaciones estén ejecutándose
   - Comprueba que el servidor web esté activo en puerto 5000
   - Asegúrate de que no hay firewall bloqueando la conexión

2. **Problemas con las Gráficas**
   - Verifica que hay datos ingresados
   - Actualiza la página del navegador
   - Limpia el caché del navegador si persisten los problemas

3. **Análisis con IA no Disponible**
   - Verifica si has configurado la API key de OpenAI
   - El análisis básico funciona sin la API key
   - Comprueba la conexión a Internet si usas IA

## 📫 Soporte y Contacto

Para soporte técnico o consultas:
- GitHub Issues: [crear un issue](https://github.com/hermesvillarreal/Salud_Control/issues)
- Email: [tu_email@dominio.com]

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

## 🙋‍♂️ Contribuir

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Tareas de Mejora de Usabilidad

A continuación se detalla una lista de tareas identificadas para mejorar la experiencia de usuario (UX) y la interfaz de usuario (UI) del proyecto.

### General
- [ ] Mejorar el manejo de errores y mensajes al usuario (feedback visual más claro).
- [ ] Unificar el estilo visual entre ambas aplicaciones para una experiencia coherente.

### Mobile App (PyQt5)
- [ ] **Validación de Entrada**: Mejorar la configuración de los `SpinBox` para facilitar la entrada de datos (pasos más grandes, botones +/- más accesibles).
- [ ] **Navegación**: Revisar el orden de tabulación (tab order) para facilitar el uso con teclado.
- [ ] **Feedback**: Reemplazar algunos `QMessageBox` modales por notificaciones no intrusivas (e.g., barra de estado) para acciones frecuentes como guardar.
- [ ] **Visualización**: Mejorar el diseño de la tabla de metas para que sea más legible en diferentes tamaños de ventana.
- [ ] **Sincronización**: Agregar un indicador visual de estado de sincronización (conectado/desconectado, última sincronización).

### Desktop App (Web)
- [ ] **Feedback de Carga**: Implementar indicadores de carga (spinners) para las gráficas y datos mientras se obtienen del servidor.
- [ ] **Manejo de Errores**: Mostrar mensajes de error amigables en la interfaz si falla la carga de datos, en lugar de solo en la consola.
- [ ] **Estética**: Mejorar el diseño CSS para una apariencia más moderna y pulida (e.g., sombras suaves, mejores tipografías).
- [ ] **Interactividad**: Agregar tooltips o explicaciones breves sobre qué significa cada gráfica o estadística.