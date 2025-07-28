# 🎯 Monitor de Pedidos en Tiempo Real - Guía Completa

## 📋 Descripción

El **Monitor de Pedidos en Tiempo Real** es un sistema especializado que escucha continuamente nuevos pedidos entrantes en el panel de administración de BeSmart Delivery, sin extraer toda la información de la aplicación. Se enfoca únicamente en detectar y procesar nuevos pedidos de manera eficiente.

## 🚀 Características Principales

### ✅ **Detección Inteligente**
- **Múltiples estrategias** de detección de elementos
- **Patrones de reconocimiento** para números de pedido
- **Selectores CSS/XPath** optimizados
- **Detección de cambios** en tiempo real

### ✅ **Notificaciones en Tiempo Real**
- **Sonidos de alerta** para nuevos pedidos
- **Notificaciones visuales** en consola
- **Guardado automático** en base de datos
- **Eventos de trazabilidad** completos

### ✅ **Configuración Flexible**
- **Intervalos personalizables** de verificación
- **Timeouts configurables** para pedidos
- **Modo debug** para desarrollo
- **Configuración por entorno** (dev/prod)

## 🏗️ Arquitectura del Sistema

### **Componentes Principales**

```
order_monitor.py
├── 🔐 Login automático
├── 🎯 Navegación a página de pedidos
├── 🔍 Extracción de nuevos pedidos
├── 💾 Guardado en base de datos
├── 🔔 Notificaciones en tiempo real
└── 📊 Estadísticas de monitoreo
```

### **Flujo de Funcionamiento**

1. **Inicialización** → Configuración de driver y base de datos
2. **Login** → Autenticación en el panel de administración
3. **Navegación** → Búsqueda de página de pedidos
4. **Monitoreo** → Verificación continua de nuevos pedidos
5. **Detección** → Análisis de elementos de la página
6. **Procesamiento** → Extracción y validación de datos
7. **Notificación** → Alertas y guardado en BD
8. **Repetición** → Ciclo continuo de monitoreo

## 🔧 Configuración

### **Archivo de Configuración**
```python
# config/monitor_config.py
MONITOR_CONFIG = {
    "check_interval": 30,        # Segundos entre verificaciones
    "order_timeout": 300,        # Segundos para pedidos "nuevos"
    "notification_sound": True,  # Sonido de notificación
    "debug_mode": True,          # Modo debug
    # ... más configuraciones
}
```

### **Variables de Entorno**
```env
# config/.env
ADMIN_USERNAME=federico
ADMIN_PASSWORD=***CONTRASEÑA_OCULTA***
LOGIN_URL=https://admin.besmartdelivery.mx/
DATABASE_URL=postgresql://...
```

## 🚀 Cómo Usar

### **Método 1: Menú Principal**
```bash
cd smartagent-project
python main.py
# Seleccionar opción 2: "Monitor de pedidos en tiempo real"
```

### **Método 2: Script Directo**
```bash
cd smartagent-project
python src/core/order_monitor.py
```

### **Método 3: Script de Inicio Rápido**
```bash
cd smartagent-project
scripts/start_monitor.bat
```

### **Método 4: Configuración**
```bash
cd smartagent-project
python config/monitor_config.py
```

## 📊 Funcionalidades de Detección

### **Patrones de Números de Pedido**
- `Pedido: ORD-1234`
- `Order: PED-5678`
- `#ORD-9012`
- `PED-3456`
- `ORD-7890`

### **Elementos Detectados**
- **Número de pedido** → Identificación única
- **Cliente** → Nombre del cliente
- **Dirección** → Dirección de entrega
- **Estado** → Estado actual del pedido
- **Monto** → Monto total del pedido
- **Timestamp** → Fecha y hora de detección

### **Selectores Utilizados**
```css
/* Contenedores de pedidos */
div[class*='order'], div[class*='pedido'], tr[class*='order']

/* Números de pedido */
span[class*='order-number'], .order-number

/* Información del cliente */
span[class*='customer'], td[class*='cliente']

/* Dirección de entrega */
span[class*='address'], td[class*='direccion']

/* Estado del pedido */
span[class*='status'], td[class*='estado']

/* Monto total */
span[class*='amount'], td[class*='monto']
```

## 💾 Integración con Base de Datos

### **Tablas Utilizadas**
- **`orders`** → Almacenamiento de pedidos
- **`customers`** → Información de clientes
- **`order_events`** → Eventos de detección
- **`notifications`** → Notificaciones del sistema

### **Datos Guardados**
```sql
-- Pedido detectado
INSERT INTO orders (order_number, status, customer_id, delivery_address)
VALUES ('ORD-1234', 'pending', 1, 'Dirección de entrega');

-- Evento de detección
INSERT INTO order_events (order_id, event_type, raw_data)
VALUES (1, 'order_detected', '{"order_number": "ORD-1234", ...}');

-- Notificación del sistema
INSERT INTO notifications (order_id, notification_type, message)
VALUES (1, 'system', 'Nuevo pedido detectado: ORD-1234');
```

## 🔔 Sistema de Notificaciones

### **Notificaciones Visuales**
```
============================================================
🚨 ¡NUEVO PEDIDO DETECTADO! 🚨
============================================================
📦 Número de Pedido: ORD-1234
👤 Cliente: Juan Pérez
📍 Dirección: Calle Principal 123
💰 Monto: $150.00
⏰ Detectado: 20:30:45
============================================================
```

### **Notificaciones de Sonido**
- **Beep del sistema** en Windows
- **Sonido de alerta** configurable
- **Fallback** para diferentes sistemas

### **Estadísticas en Tiempo Real**
```
📊 Estadísticas del Monitor:
   Verificaciones totales: 50
   Nuevos pedidos detectados: 3
   Última verificación: 20:35:00
   Pedidos conocidos: 15
```

## ⚙️ Configuración Avanzada

### **Modo de Desarrollo**
```python
DEV_CONFIG = {
    "debug_mode": True,
    "save_screenshots": True,
    "save_html": True,
    "verbose_logging": True
}
```

### **Modo de Producción**
```python
PROD_CONFIG = {
    "debug_mode": False,
    "save_screenshots": False,
    "save_html": False,
    "verbose_logging": False
}
```

### **Personalización de Intervalos**
```python
# Verificación cada 15 segundos
"check_interval": 15

# Pedidos nuevos en últimos 10 minutos
"order_timeout": 600

# Máximo 5 reintentos
"max_retries": 5
```

## 🐛 Solución de Problemas

### **Problemas Comunes**

#### **1. No se detectan pedidos**
- Verificar que la página de pedidos esté accesible
- Revisar selectores CSS/XPath
- Comprobar patrones de detección
- Activar modo debug para análisis

#### **2. Errores de login**
- Verificar credenciales en `.env`
- Comprobar conectividad a la URL
- Revisar elementos de login en la página

#### **3. Errores de base de datos**
- Verificar conexión a PostgreSQL
- Comprobar permisos de usuario
- Revisar estructura de tablas

#### **4. Alto uso de CPU**
- Aumentar intervalo de verificación
- Desactivar modo debug
- Optimizar selectores CSS

### **Logs de Debug**
```bash
# Ver logs en tiempo real
tail -f logs/order_monitor.log

# Buscar errores específicos
grep "ERROR" logs/order_monitor.log

# Verificar estadísticas
grep "Estadísticas" logs/order_monitor.log
```

## 📈 Monitoreo y Estadísticas

### **Métricas Clave**
- **Verificaciones totales** → Número de ciclos completados
- **Pedidos detectados** → Nuevos pedidos encontrados
- **Tiempo de respuesta** → Velocidad de detección
- **Tasa de éxito** → Porcentaje de detecciones exitosas

### **Archivos de Log**
- **`logs/order_monitor.log`** → Log principal del monitor
- **`logs/main.log`** → Log del sistema principal
- **Screenshots** → Capturas de pantalla (modo debug)

## 🔒 Seguridad y Privacidad

### **Credenciales Seguras**
- Variables de entorno en archivo `.env`
- No hardcodeo de contraseñas
- Configuración centralizada

### **Datos Sensibles**
- Información de clientes protegida
- Logs sin datos sensibles
- Conexión segura a base de datos

## 🚀 Próximas Mejoras

### **Funcionalidades Planificadas**
1. **Notificaciones por email** → Alertas automáticas
2. **Dashboard web** → Interfaz gráfica
3. **API REST** → Integración externa
4. **Machine Learning** → Detección inteligente
5. **Múltiples sitios** → Monitoreo simultáneo

### **Optimizaciones**
1. **Detección más rápida** → Algoritmos optimizados
2. **Menor uso de recursos** → Eficiencia mejorada
3. **Mayor precisión** → Menos falsos positivos
4. **Escalabilidad** → Soporte para más pedidos

## 📞 Soporte

### **Comandos de Ayuda**
```bash
# Ver configuración
python config/monitor_config.py

# Verificar estado del sistema
scripts/status.bat

# Ejecutar pruebas
python tests/test_login_enhanced.py
```

### **Archivos Importantes**
- **`src/core/order_monitor.py`** → Monitor principal
- **`config/monitor_config.py`** → Configuración
- **`config/.env`** → Variables de entorno
- **`logs/order_monitor.log`** → Logs del sistema

---

**¡El Monitor de Pedidos en Tiempo Real está listo para detectar nuevos pedidos de manera eficiente y confiable!** 🎯 