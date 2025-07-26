#!/usr/bin/env python3
"""
SmartAgent Project - Main Entry Point
Sistema completo de exploración web y gestión de pedidos
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configurar logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/main.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    """Función principal del proyecto"""
    print("🚀 SmartAgent Project - Sistema Completo")
    print("=" * 50)
    print("1. Ejecutar sistema principal (smartagent_enhanced)")
    print("2. Monitor de pedidos en tiempo real")
    print("3. Configurar base de datos")
    print("4. Mostrar estructura de base de datos")
    print("5. Ejecutar pruebas")
    print("6. Consultar base de datos")
    print("7. Configurar monitor de pedidos")
    print("8. Salir")
    print("=" * 50)

    while True:
        try:
            choice = input("\nSelecciona una opción (1-8): ").strip()

            if choice == "1":
                print("\n🤖 Ejecutando sistema principal...")
                from core.smartagent_enhanced import main as run_enhanced
                run_enhanced()
                break

            elif choice == "2":
                print("\n🎯 Iniciando monitor de pedidos en tiempo real...")
                from core.order_monitor import main as run_monitor
                run_monitor()
                break

            elif choice == "3":
                print("\n🗄️ Configurando base de datos...")
                from database.database_enhancement import main as setup_db
                setup_db()
                break

            elif choice == "4":
                print("\n📊 Mostrando estructura de base de datos...")
                from database.show_database_structure import main as show_structure
                show_structure()
                break

            elif choice == "5":
                print("\n🧪 Ejecutando pruebas...")
                import subprocess
                subprocess.run([sys.executable, "tests/test_smartagent.py"])
                subprocess.run([sys.executable, "tests/test_orders.py"])
                break

            elif choice == "6":
                print("\n🔍 Consultando base de datos...")
                from database.consultar_db import main as consult_db
                consult_db()
                break

            elif choice == "7":
                print("\n🔧 Configurando monitor de pedidos...")
                import subprocess
                subprocess.run([sys.executable, "config/monitor_config.py"])
                break

            elif choice == "8":
                print("\n👋 ¡Hasta luego!")
                break

            else:
                print("❌ Opción no válida. Por favor selecciona 1-8.")

        except KeyboardInterrupt:
            print("\n\n⏹️ Operación cancelada por el usuario")
            break
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 