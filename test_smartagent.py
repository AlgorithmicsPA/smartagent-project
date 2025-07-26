#!/usr/bin/env python3
"""
Script de prueba para SmartAgent
Verifica que todas las dependencias estén instaladas correctamente
"""

import sys
import importlib
import os
from datetime import datetime

def test_imports():
    """Probar que todas las dependencias estén disponibles"""
    print("🔍 Probando importaciones...")
    
    required_modules = [
        'selenium',
        'bs4',
        'webdriver_manager',
        'requests',
        'lxml'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - NO ENCONTRADO")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Faltan módulos: {', '.join(missing_modules)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las importaciones exitosas")
    return True

def test_selenium_setup():
    """Probar la configuración de Selenium"""
    print("\n🔍 Probando configuración de Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Configurar opciones básicas
        options = Options()
        options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Intentar instalar ChromeDriver automáticamente
        try:
            service = Service(ChromeDriverManager().install())
            print("  ✅ ChromeDriver instalado automáticamente")
        except Exception as e:
            print(f"  ⚠️  Error con ChromeDriver automático: {e}")
            return False
        
        # Crear driver de prueba
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"  ✅ Navegador funcionando (título: {title})")
        return True
        
    except Exception as e:
        print(f"  ❌ Error en Selenium: {e}")
        return False

def test_file_structure():
    """Verificar estructura de archivos"""
    print("\n🔍 Verificando estructura de archivos...")
    
    required_files = [
        'smartagent.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - NO ENCONTRADO")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Faltan archivos: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos los archivos presentes")
    return True

def test_directories():
    """Crear directorios necesarios"""
    print("\n🔍 Verificando directorios...")
    
    required_dirs = ['logs', 'besmart_profile']
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"  ✅ Creado: {dir_name}")
        else:
            print(f"  ✅ Existe: {dir_name}")

def test_configuration():
    """Verificar configuración del SmartAgent"""
    print("\n🔍 Verificando configuración...")
    
    try:
        # Importar configuración del smartagent
        sys.path.append('.')
        from smartagent import START_URL, ADMIN_USERNAME, ADMIN_PASSWORD
        
        print(f"  ✅ URL de inicio: {START_URL}")
        print(f"  ✅ Usuario: {ADMIN_USERNAME}")
        print(f"  ✅ Contraseña: {'*' * len(ADMIN_PASSWORD)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("=" * 50)
    print("    SMARTAGENT - PRUEBAS DE INSTALACIÓN")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Importaciones", test_imports),
        ("Estructura de archivos", test_file_structure),
        ("Directorios", test_directories),
        ("Configuración", test_configuration),
        ("Selenium", test_selenium_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ Error en {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"RESULTADOS: {passed}/{total} pruebas exitosas")
    print("=" * 50)
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        print("✅ SmartAgent está listo para usar")
        print("\nPara ejecutar:")
        print("   python smartagent.py")
    else:
        print("⚠️  Algunas pruebas fallaron")
        print("Revisa los errores arriba y corrige los problemas")
        print("\nComandos útiles:")
        print("   pip install -r requirements.txt")
        print("   python smartagent.py")
    
    print("\nPresiona Enter para continuar...")
    input()

if __name__ == "__main__":
    main() 