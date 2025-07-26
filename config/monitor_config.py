#!/usr/bin/env python3
"""
Configuración del Monitor de Pedidos en Tiempo Real
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
project_root = Path(__file__).parent.parent
load_dotenv(project_root / "config" / ".env")

# Configuración del monitor de active_orders
MONITOR_CONFIG = {
    # Intervalos de tiempo
    "check_interval": 30,  # Segundos entre verificaciones
    "order_timeout": 300,  # Segundos para considerar un active_order como "nuevo"
    "max_retries": 3,      # Máximo de reintentos en caso de error
    
    # Página objetivo
    "target_page": "/tasks",
    "target_section": "active_orders",
    
    # Notificaciones
    "notification_sound": True,  # Sonido de notificación
    "desktop_notifications": True,  # Notificaciones de escritorio
    "email_notifications": False,  # Notificaciones por email
    
    # Logging
    "log_level": "INFO",
    "log_file": "logs/order_monitor.log",
    
    # Detección de active_orders
    "detection_patterns": [
        r'Task[:\s]*([A-Z0-9-]+)',
        r'Tarea[:\s]*([A-Z0-9-]+)',
        r'Order[:\s]*([A-Z0-9-]+)',
        r'Pedido[:\s]*([A-Z0-9-]+)',
        r'#([A-Z0-9-]+)',
        r'([A-Z]{2,3}-\d{4,})',
        r'ID[:\s]*([A-Z0-9-]+)',
        r'Active[:\s]*([A-Z0-9-]+)',
        r'ORD-(\d+)',
        r'TASK-(\d+)'
    ],
    
    # Selectores CSS/XPath para elementos de active_orders
    "active_orders_selectors": {
        "containers": [
            "div[class*='active_orders']",
            "div[id*='active_orders']",
            "section[class*='active_orders']",
            "table[class*='active_orders']",
            "ul[class*='active_orders']",
            "div[class*='task']",
            "div[class*='active']",
            "tr[class*='active']",
            "li[class*='active']",
            ".active-orders",
            ".active_orders",
            ".task-item",
            ".active-item"
        ],
        "task_id": [
            "span[class*='task-id']",
            "span[class*='order-id']",
            "span[class*='active-id']",
            "td[class*='task-id']",
            "td[class*='order-id']",
            "td[class*='active-id']",
            ".task-id",
            ".order-id",
            ".active-id"
        ],
        "order_number": [
            "span[class*='order-number']",
            "span[class*='task-number']",
            "span[class*='active-number']",
            "td[class*='order-number']",
            "td[class*='task-number']",
            "td[class*='active-number']",
            ".order-number",
            ".task-number",
            ".active-number"
        ],
        "customer": [
            "span[class*='customer']",
            "span[class*='cliente']",
            "span[class*='user']",
            "td[class*='customer']",
            "td[class*='cliente']",
            "td[class*='user']"
        ],
        "address": [
            "span[class*='address']",
            "span[class*='direccion']",
            "span[class*='location']",
            "td[class*='address']",
            "td[class*='direccion']",
            "td[class*='location']"
        ],
        "status": [
            "span[class*='status']",
            "span[class*='estado']",
            "span[class*='state']",
            "td[class*='status']",
            "td[class*='estado']",
            "td[class*='state']"
        ],
        "amount": [
            "span[class*='amount']",
            "span[class*='total']",
            "span[class*='monto']",
            "span[class*='price']",
            "td[class*='amount']",
            "td[class*='total']",
            "td[class*='monto']",
            "td[class*='price']"
        ],
        "description": [
            "span[class*='description']",
            "span[class*='descripcion']",
            "span[class*='task-desc']",
            "td[class*='description']",
            "td[class*='descripcion']",
            "td[class*='task-desc']"
        ]
    },
    
    # Configuración de la base de datos
    "database": {
        "auto_save": True,
        "create_notifications": True,
        "create_events": True,
        "batch_size": 10
    },
    
    # Configuración del navegador
    "browser": {
        "headless": False,
        "window_size": "1920,1080",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "disable_images": True,
        "disable_css": False,
        "disable_javascript": False
    },
    
    # Configuración de alertas
    "alerts": {
        "high_priority_keywords": ["urgente", "urgent", "rápido", "fast", "active", "task"],
        "low_stock_threshold": 5,
        "delivery_time_warning": 30  # minutos
    }
}

# Configuración de desarrollo
DEV_CONFIG = {
    "debug_mode": True,
    "save_screenshots": True,
    "save_html": True,
    "verbose_logging": True
}

# Configuración de producción
PROD_CONFIG = {
    "debug_mode": False,
    "save_screenshots": False,
    "save_html": False,
    "verbose_logging": False
}

def get_config(environment="dev"):
    """Obtener configuración según el entorno"""
    config = MONITOR_CONFIG.copy()
    
    if environment == "prod":
        config.update(PROD_CONFIG)
    else:
        config.update(DEV_CONFIG)
    
    return config

def validate_config(config):
    """Validar configuración del monitor de active_orders"""
    errors = []
    
    # Validar intervalos
    if config["check_interval"] < 10:
        errors.append("check_interval debe ser al menos 10 segundos")
    
    if config["order_timeout"] < 60:
        errors.append("order_timeout debe ser al menos 60 segundos")
    
    # Validar página objetivo
    if not config.get("target_page"):
        errors.append("Debe especificar una página objetivo")
    
    # Validar patrones de detección
    if not config["detection_patterns"]:
        errors.append("Debe haber al menos un patrón de detección")
    
    # Validar selectores
    if not config["active_orders_selectors"]["containers"]:
        errors.append("Debe haber al menos un selector de contenedores de active_orders")
    
    return errors

def print_config_summary():
    """Imprimir resumen de la configuración"""
    config = get_config()
    
    print("🔧 Configuración del Monitor de Active_Orders")
    print("=" * 50)
    print(f"🌐 Página objetivo: {config['target_page']}")
    print(f"🎯 Sección objetivo: {config['target_section']}")
    print(f"⏱️  Intervalo de verificación: {config['check_interval']} segundos")
    print(f"⏰ Timeout de active_orders: {config['order_timeout']} segundos")
    print(f"🔔 Sonido de notificación: {'Activado' if config['notification_sound'] else 'Desactivado'}")
    print(f"📧 Notificaciones por email: {'Activadas' if config['email_notifications'] else 'Desactivadas'}")
    print(f"🐛 Modo debug: {'Activado' if config['debug_mode'] else 'Desactivado'}")
    print(f"📸 Guardar screenshots: {'Activado' if config['save_screenshots'] else 'Desactivado'}")
    print(f"📝 Patrones de detección: {len(config['detection_patterns'])}")
    print(f"🎯 Selectores de active_orders: {len(config['active_orders_selectors']['containers'])}")
    print("=" * 50)

if __name__ == "__main__":
    print_config_summary()
    
    # Validar configuración
    config = get_config()
    errors = validate_config(config)
    
    if errors:
        print("\n❌ Errores de configuración:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuración válida") 