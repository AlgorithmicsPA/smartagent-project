# SmartAgent para BeSmart Delivery Admin Panel

## Descripción
Script de Python para automatizar la exploración y mapeo del panel de administración de BeSmart Delivery.

## Características Actualizadas

### ✅ Nuevas Funcionalidades
- **Login automático** con credenciales configuradas
- **Exploración inteligente** del admin panel
- **Extracción detallada** de elementos de la interfaz
- **Logging completo** con archivos de registro
- **Manejo robusto de errores**
- **Guardado automático** de datos cada 30 segundos

### 🔧 Mejoras Técnicas
- **ChromeDriver automático** con webdriver-manager
- **Detección anti-bot** mejorada
- **Estructura de datos mejorada** con timestamps
- **Extracción de formularios y tablas**
- **Manejo de sesiones** persistente

## Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Verificar Chrome
Asegúrate de tener Google Chrome instalado en tu sistema.

## Configuración

### Credenciales (ya configuradas)
- **Usuario**: manus
- **Contraseña**: ***CONTRASEÑA_OCULTA***
- **URL**: https://admin.besmartdelivery.mx/

### Archivos de configuración
- `smartagent.py` - Script principal
- `requirements.txt` - Dependencias
- `estructura.json` - Datos extraídos (se genera automáticamente)
- `flujo.txt` - Reporte legible (se genera automáticamente)
- `logs/smartagent.log` - Archivo de logs

## Uso

### Ejecutar el script
```bash
python smartagent.py
```

### Funcionamiento
1. **Inicio automático** del navegador Chrome
2. **Login automático** en el admin panel
3. **Exploración sistemática** de todas las páginas
4. **Extracción de datos**:
   - Botones y sus propiedades
   - Campos de entrada (inputs)
   - Enlaces internos
   - Formularios
   - Tablas de datos
5. **Guardado automático** cada 30 segundos

## Archivos de Salida

### estructura.json
```json
{
  "https://admin.besmartdelivery.mx/": {
    "url": "https://admin.besmartdelivery.mx/",
    "titulo": "BeSmart Delivery Admin",
    "timestamp": "2024-01-01T12:00:00",
    "botones": [
      {
        "texto": "Guardar",
        "tipo": "submit",
        "id": "save-btn"
      }
    ],
    "inputs": [
      {
        "tipo": "text",
        "nombre": "username",
        "id": "user-input",
        "placeholder": "Ingrese usuario"
      }
    ],
    "links": [
      {
        "url": "https://admin.besmartdelivery.mx/dashboard",
        "texto": "Dashboard"
      }
    ],
    "forms": [
      {
        "action": "/login",
        "method": "post",
        "id": "login-form"
      }
    ],
    "tables": [
      {
        "id": "data-table",
        "class": ["table", "table-striped"],
        "rows": 10
      }
    ]
  }
}
```

### flujo.txt
```
=== REPORTE SMARTAGENT - 2024-01-01 12:00:00 ===

==================================================
URL: https://admin.besmartdelivery.mx/
Título: BeSmart Delivery Admin
Timestamp: 2024-01-01T12:00:00

Botones (5):
  - Login (tipo: submit, id: login-btn)
  - Guardar (tipo: button, id: save-btn)

Inputs (3):
  - text - username (id: user-input)
  - password - password (id: pass-input)

Links (8):
  - Dashboard: https://admin.besmartdelivery.mx/dashboard
  - Usuarios: https://admin.besmartdelivery.mx/users

Formularios (2):
  - post -> /login
  - get -> /search

Tablas (1):
  - data-table: 10 filas
```

## Logs

### logs/smartagent.log
```
2024-01-01 12:00:00 - INFO - 🤖 Iniciando SmartAgent para BeSmart Delivery Admin Panel
2024-01-01 12:00:01 - INFO - ✅ ChromeDriver automático instalado
2024-01-01 12:00:02 - INFO - ✅ Navegador configurado correctamente
2024-01-01 12:00:03 - INFO - 🔐 Iniciando proceso de login...
2024-01-01 12:00:08 - INFO - ✅ Login exitoso
2024-01-01 12:00:09 - INFO - 🚀 Iniciando exploración del admin panel...
2024-01-01 12:00:10 - INFO - 🔍 Explorando: https://admin.besmartdelivery.mx/
2024-01-01 12:00:15 - INFO - ✅ Datos extraídos de https://admin.besmartdelivery.mx/
2024-01-01 12:00:30 - INFO - 💾 Guardado automático realizado - 1 páginas exploradas
```

## Características de Seguridad

### 🔒 Protecciones Implementadas
- **Detección anti-bot** deshabilitada
- **User-Agent** personalizado
- **Pausas inteligentes** entre requests
- **Manejo de errores** robusto
- **Logs detallados** para debugging

### ⚠️ Consideraciones
- Las credenciales están hardcodeadas (para desarrollo)
- En producción, usar variables de entorno
- Respetar los términos de uso del sitio
- No sobrecargar el servidor

## Troubleshooting

### Error: ChromeDriver no encontrado
```bash
pip install webdriver-manager
```

### Error: Login fallido
- Verificar credenciales en el código
- Verificar que el sitio esté accesible
- Revisar logs para más detalles

### Error: Elementos no encontrados
- El sitio puede haber cambiado su estructura
- Revisar logs para identificar elementos específicos
- Actualizar selectores si es necesario

## Desarrollo

### Estructura del Código
- `SmartAgent` - Clase principal
- `setup_driver()` - Configuración del navegador
- `login()` - Autenticación automática
- `extract_page_data()` - Extracción de datos
- `explore_page()` - Exploración de páginas
- `guardar_periodicamente()` - Guardado automático

### Personalización
- Modificar `ADMIN_USERNAME` y `ADMIN_PASSWORD`
- Ajustar `START_URL` si es necesario
- Modificar selectores en `login()` si cambia la interfaz
- Ajustar tiempos de espera según la velocidad del sitio

## Soporte

Para reportar problemas o solicitar mejoras:
1. Revisar los logs en `logs/smartagent.log`
2. Verificar la conectividad al sitio
3. Comprobar que las dependencias estén actualizadas
4. Revisar que Chrome esté actualizado 