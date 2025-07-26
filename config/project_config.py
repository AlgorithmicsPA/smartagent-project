#!/usr/bin/env python3
"""
Configuración del proyecto SmartAgent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
CONFIG_PATH = PROJECT_ROOT / "config"
LOGS_PATH = PROJECT_ROOT / "logs"
DATA_PATH = PROJECT_ROOT / "data"
DOCS_PATH = PROJECT_ROOT / "docs"
TESTS_PATH = PROJECT_ROOT / "tests"
SCRIPTS_PATH = PROJECT_ROOT / "scripts"

# Configuración de la aplicación
APP_NAME = "SmartAgent Project"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Sistema completo de exploración web y gestión de pedidos"

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_PATH / "main.log"

# Configuración de base de datos
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL"),
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600
}

# Configuración de web scraping
SCRAPING_CONFIG = {
    "max_pages": 50,
    "delay_min": 1,
    "delay_max": 3,
    "timeout": 30,
    "retry_attempts": 3
}

# Configuración de credenciales
CREDENTIALS_CONFIG = {
    "username": os.getenv("ADMIN_USERNAME"),
    "password": os.getenv("ADMIN_PASSWORD"),
    "start_url": os.getenv("START_URL"),
    "login_url": os.getenv("LOGIN_URL")
}

# Configuración de Chrome
CHROME_CONFIG = {
    "headless": False,
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "no_sandbox": True,
    "disable_dev_shm": True
}

# Configuración de archivos
FILE_CONFIG = {
    "json_backup": DATA_PATH / "estructura.json",
    "txt_report": DATA_PATH / "flujo.txt",
    "progress_file": DATA_PATH / "progreso.txt"
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    "email_enabled": True,
    "sms_enabled": False,
    "whatsapp_enabled": True,
    "push_enabled": False
}

# Configuración de analytics
ANALYTICS_CONFIG = {
    "enabled": True,
    "daily_reports": True,
    "performance_tracking": True,
    "error_tracking": True
}

def get_project_info():
    """Obtener información del proyecto"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "paths": {
            "root": str(PROJECT_ROOT),
            "src": str(SRC_PATH),
            "config": str(CONFIG_PATH),
            "logs": str(LOGS_PATH),
            "data": str(DATA_PATH),
            "docs": str(DOCS_PATH),
            "tests": str(TESTS_PATH),
            "scripts": str(SCRIPTS_PATH)
        }
    }

def validate_config():
    """Validar configuración del proyecto"""
    errors = []
    
    # Verificar rutas
    required_paths = [PROJECT_ROOT, SRC_PATH, CONFIG_PATH, LOGS_PATH, DATA_PATH]
    for path in required_paths:
        if not path.exists():
            errors.append(f"Ruta no encontrada: {path}")
    
    # Verificar variables de entorno
    required_env_vars = ["DATABASE_URL", "ADMIN_USERNAME", "ADMIN_PASSWORD"]
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"Variable de entorno no encontrada: {var}")
    
    return errors

if __name__ == "__main__":
    print("🔧 Configuración del Proyecto SmartAgent")
    print("=" * 50)
    
    info = get_project_info()
    print(f"📋 Nombre: {info['name']}")
    print(f"📦 Versión: {info['version']}")
    print(f"📝 Descripción: {info['description']}")
    print()
    
    print("📁 Rutas del proyecto:")
    for name, path in info['paths'].items():
        print(f"   {name}: {path}")
    print()
    
    errors = validate_config()
    if errors:
        print("❌ Errores de configuración:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuración válida") 