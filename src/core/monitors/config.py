"""
Configuración para monitores de órdenes
Configuraciones centralizadas para todas las versiones de monitores
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "config" / ".env")

# Variables de entorno
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
TASKS_URL = os.getenv("TASKS_URL", "https://admin.besmartdelivery.mx/tasks") # URL base sin parámetros
TASKS_URL_WITH_PARAMS = os.getenv("TASKS_URL_WITH_PARAMS", "https://admin.besmartdelivery.mx/tasks?status=REQUIRES_CONFIRMATION&status=PROCESSED&status=INPREPARATION&status=READYFORCOLLECTION&status=ONTHEWAY&status=ATLOCATION")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "federico")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "28ZwnPHQRC*H4BmfmEB-YHcC")
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración del monitor terminal
TERMINAL_MONITOR_CONFIG = {
    "check_interval": 10,           # Segundos entre verificaciones
    "order_timeout": 300,           # Segundos para considerar un pedido como "nuevo"
    "max_retries": 3,               # Máximo de reintentos en caso de error
    "notification_sound": True,     # Sonido de notificación
    "log_level": "INFO",
    "max_known_orders": 500,        # Máximo de órdenes conocidas en memoria
    "request_timeout": 30,          # Timeout para peticiones HTTP
    "enable_auto_refresh": True,    # Auto-refresh de sesión
    "refresh_interval": 600,        # Segundos entre auto-refresh (10 min)
    "enable_debug_mode": False,     # Modo debug para desarrollo
    "save_screenshots": False,      # No screenshots en terminal
    "enable_webhook": False,        # Habilitar webhooks para notificaciones
    "webhook_url": "",             # URL del webhook
    "enable_database_logging": True, # Logging detallado en base de datos
    "enable_performance_monitoring": True, # Monitoreo de rendimiento
    "max_concurrent_orders": 50,    # Máximo de órdenes concurrentes
    "order_priority_levels": ["urgent", "high", "normal", "low"], # Niveles de prioridad
    "enable_order_analytics": True, # Análisis de órdenes
    "enable_restaurant_tracking": True, # Seguimiento de restaurantes
    "enable_customer_tracking": True,   # Seguimiento de clientes
    "enable_delivery_optimization": True, # Optimización de entregas
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configuración del monitor mejorado
ENHANCED_MONITOR_CONFIG = {
    "check_interval": 15,           # Segundos entre verificaciones
    "order_timeout": 300,           # Segundos para considerar un pedido como "nuevo"
    "max_retries": 5,               # Máximo de reintentos en caso de error
    "notification_sound": True,     # Sonido de notificación
    "log_level": "INFO",
    "max_known_orders": 1000,       # Máximo de órdenes conocidas en memoria
    "page_load_timeout": 30,        # Timeout para cargar página
    "element_wait_timeout": 10,     # Timeout para esperar elementos
    "enable_auto_refresh": True,    # Auto-refresh de página
    "refresh_interval": 300,        # Segundos entre auto-refresh
    "enable_debug_mode": False,     # Modo debug para desarrollo
    "save_screenshots": True,       # Guardar screenshots de nuevas órdenes
    "enable_webhook": False,        # Habilitar webhooks para notificaciones
    "webhook_url": "",             # URL del webhook
    "enable_database_logging": True, # Logging detallado en base de datos
    "enable_performance_monitoring": True, # Monitoreo de rendimiento
    "max_concurrent_orders": 50,    # Máximo de órdenes concurrentes
    "order_priority_levels": ["urgent", "high", "normal", "low"], # Niveles de prioridad
    "enable_order_analytics": True, # Análisis de órdenes
    "enable_restaurant_tracking": True, # Seguimiento de restaurantes
    "enable_customer_tracking": True,   # Seguimiento de clientes
    "enable_delivery_optimization": True, # Optimización de entregas
}

# Configuración del monitor original
ORIGINAL_MONITOR_CONFIG = {
    "check_interval": 30,           # Segundos entre verificaciones
    "order_timeout": 300,           # Segundos para considerar un pedido como "nuevo"
    "max_retries": 3,               # Máximo de reintentos en caso de error
    "notification_sound": True,     # Sonido de notificación
    "log_level": "INFO"
} 