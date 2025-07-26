# Monitor de Selenium - SmartAgent Project

## 🎯 Estado: ✅ FUNCIONANDO CORRECTAMENTE

El monitor de Selenium está completamente funcional y puede monitorear órdenes en tiempo real desde el panel de administración de Besmart Delivery.

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.7+
- Google Chrome
- ChromeDriver (se descarga automáticamente)

### Instalación de Dependencias
```bash
pip install selenium
pip install undetected-chromedriver
```

### Ejecutar el Monitor
```bash
cd smartagent-project
python selenium_monitor_working.py
```

## 📁 Archivos Principales

### 🎯 Archivo Principal (VERSIÓN FINAL)
- **`selenium_monitor_working.py`** - Monitor funcional completo
  - Login automático
  - Detección de órdenes activas
  - Monitoreo continuo
  - Extracción de datos

### 🔧 Herramientas de Debug
- **`selenium_monitor_debug.py`** - Debug detallado
- **`quick_debug.py`** - Debug rápido
- **`diagnostic_monitor.py`** - Diagnóstico completo

### 📚 Archivos de Desarrollo
- `selenium_monitor_final.py` - Versión con selectores flexibles
- `selenium_monitor_corrected.py` - Versión con múltiples estrategias
- `selenium_monitor_dynamic.py` - Versión para contenido dinámico
- `selenium_monitor_login_fix.py` - Versión con verificación de login

## 🔍 Funcionalidades

### ✅ Login Automático
- Múltiples estrategias de login
- Manejo robusto de selectores
- Verificación de login exitoso

### ✅ Detección de Órdenes
- Búsqueda del botón "Active orders"
- Extracción de datos de tabla
- Parsing de información de órdenes

### ✅ Monitoreo Continuo
- Verificación cada 10 segundos
- Detección de nuevas órdenes
- Logs detallados en consola

### ✅ Manejo de Errores
- Recuperación automática
- Debug detallado
- Screenshots para troubleshooting

## 📊 Resultados de Prueba

```
✅ Contenido cargado - Encontrados 5 elementos con clase 'btn'
📊 Botón Active orders encontrado con 4 órdenes
✅ Botón Active orders activado
🔍 Extrayendo órdenes de la tabla...
📊 Encontradas 3 órdenes en la tabla
ℹ️ No hay nuevas órdenes
```

## 🛠️ Configuración

### Credenciales
```python
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "28ZwnPHQRC*H4BmfmEB-YHcC"
```

### URLs
```python
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks"
```

## 🔧 Troubleshooting

### Problema: ChromeDriver no funciona
**Solución**: El monitor usa configuración estándar de Chrome WebDriver

### Problema: No encuentra elementos
**Solución**: Usar `selenium_monitor_debug.py` para diagnóstico

### Problema: Login falla
**Solución**: Verificar credenciales y usar `quick_debug.py`

## 📈 Datos Extraídos

El monitor extrae la siguiente información de cada orden:
- ID de orden
- Estado
- Restaurante
- Cliente
- Zona de entrega
- Total
- Hora de creación
- Tiempo de cocina (CT)
- Tiempo de entrega (DT)
- Rider asignado

## 🎯 Comandos Útiles

### Ejecutar Monitor Principal
```bash
python selenium_monitor_working.py
```

### Debug Detallado
```bash
python selenium_monitor_debug.py
```

### Análisis Rápido
```bash
python quick_debug.py
```

### Diagnóstico Completo
```bash
python diagnostic_monitor.py
```

## 📝 Logs y Output

El monitor genera logs detallados que incluyen:
- Estado de conexión
- Proceso de login
- Detección de elementos
- Extracción de órdenes
- Errores y warnings

## 🔄 Monitoreo Continuo

El monitor funciona en un bucle continuo:
1. Verificar login
2. Navegar a página de tareas
3. Buscar botón "Active orders"
4. Extraer órdenes de tabla
5. Mostrar nuevas órdenes
6. Esperar 10 segundos
7. Repetir

## 🎉 Estado del Proyecto

- **Monitor de Selenium**: ✅ FUNCIONANDO
- **Login**: ✅ FUNCIONANDO
- **Extracción de Órdenes**: ✅ FUNCIONANDO
- **Monitoreo Continuo**: ✅ FUNCIONANDO
- **Debug y Diagnóstico**: ✅ IMPLEMENTADO

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs en consola
2. Usar herramientas de debug
3. Verificar screenshots generados
4. Revisar archivo `SELENIUM_MONITOR_UPDATE.md`

---

**Última Actualización**: 26 de Julio, 2024
**Versión**: 1.0.0
**Estado**: ✅ PRODUCCIÓN READY 