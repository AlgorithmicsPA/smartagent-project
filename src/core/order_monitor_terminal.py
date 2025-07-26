#!/usr/bin/env python3
"""
Monitor de Pedidos en Tiempo Real - Terminal Version
Versión modular que funciona completamente en terminal sin Selenium/WebDriver
"""

import sys
import os
from pathlib import Path

# Cambiar al directorio del proyecto
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

# Agregar el directorio src al path
sys.path.insert(0, str(project_root / "src"))

# Importar el monitor terminal modular
from core.monitors.terminal_monitor import main

if __name__ == "__main__":
    main() 