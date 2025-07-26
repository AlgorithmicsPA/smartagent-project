#!/usr/bin/env python3
"""
Script de prueba para el monitor de órdenes
"""

import sys
import os
from pathlib import Path

# Cambiar al directorio del proyecto
project_root = Path(__file__).parent
os.chdir(project_root)

# Agregar el directorio src al path
sys.path.insert(0, str(project_root / "src"))

try:
    print("🔍 Probando importación del monitor...")
    from core.monitors.terminal_monitor import TerminalOrderMonitor
    print("✅ Monitor importado correctamente")
    
    print("🚀 Iniciando monitor...")
    monitor = TerminalOrderMonitor()
    
    print("📡 Probando conexión...")
    if monitor.http_client.setup_session():
        print("✅ Sesión HTTP configurada")
        
        if monitor.http_client.login():
            print("✅ Login exitoso")
            
            print("📄 Obteniendo página de órdenes...")
            html_content = monitor.http_client.get_orders_page()
            if html_content:
                print("✅ Página obtenida correctamente")
                print(f"📏 Tamaño del contenido: {len(html_content)} caracteres")
                
                print("🔍 Extrayendo órdenes...")
                new_orders = monitor.order_extractor.extract_new_orders(html_content, set())
                print(f"📊 Órdenes encontradas: {len(new_orders)}")
                
                if new_orders:
                    print("🎯 Órdenes detectadas:")
                    for i, order in enumerate(new_orders, 1):
                        print(f"   {i}. ID: {order.get('order_id', 'N/A')}")
                        print(f"      Cliente: {order.get('customer_name', 'N/A')}")
                        print(f"      Restaurante: {order.get('restaurant', 'N/A')}")
                        print(f"      Total: ${order.get('total_amount', 'N/A')}")
                        print(f"      Estado: {order.get('status', 'N/A')}")
                        print()
                else:
                    print("ℹ️ No se encontraron órdenes nuevas")
            else:
                print("❌ No se pudo obtener la página")
        else:
            print("❌ Error en el login")
    else:
        print("❌ Error configurando sesión HTTP")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 