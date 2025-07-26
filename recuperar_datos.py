#!/usr/bin/env python3
"""
Script de recuperación de datos del SmartAgent
Muestra el progreso y datos recolectados
"""

import json
import os
from datetime import datetime

def mostrar_progreso():
    """Mostrar el progreso actual del SmartAgent"""
    print("=" * 60)
    print("    SMARTAGENT - RECUPERACIÓN DE DATOS")
    print("=" * 60)
    
    # Verificar archivos existentes
    archivos = {
        "estructura.json": "Datos principales",
        "flujo.txt": "Reporte legible",
        "progreso.txt": "Progreso actual",
        "reporte_final.txt": "Reporte final"
    }
    
    print("\n📁 ARCHIVOS DISPONIBLES:")
    print("-" * 40)
    for archivo, descripcion in archivos.items():
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            mod_time = datetime.fromtimestamp(os.path.getmtime(archivo))
            print(f"✅ {archivo} ({descripcion})")
            print(f"   Tamaño: {size:,} bytes")
            print(f"   Modificado: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
        print()
    
    # Buscar backups
    backups = [f for f in os.listdir('.') if f.startswith('backup_') and f.endswith('.json')]
    if backups:
        print("💾 BACKUPS DISPONIBLES:")
        print("-" * 40)
        for backup in sorted(backups, reverse=True):
            size = os.path.getsize(backup)
            mod_time = datetime.fromtimestamp(os.path.getmtime(backup))
            print(f"📦 {backup}")
            print(f"   Tamaño: {size:,} bytes")
            print(f"   Modificado: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def cargar_y_mostrar_datos():
    """Cargar y mostrar los datos recolectados"""
    if not os.path.exists("estructura.json"):
        print("❌ No se encontró estructura.json")
        return
    
    try:
        with open("estructura.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        print("📊 RESUMEN DE DATOS RECOLECTADOS:")
        print("=" * 60)
        print(f"Total de páginas exploradas: {len(datos)}")
        
        if datos:
            # Estadísticas generales
            total_botones = sum(len(pagina.get("botones", [])) for pagina in datos.values())
            total_inputs = sum(len(pagina.get("inputs", [])) for pagina in datos.values())
            total_links = sum(len(pagina.get("links", [])) for pagina in datos.values())
            total_forms = sum(len(pagina.get("forms", [])) for pagina in datos.values())
            total_tables = sum(len(pagina.get("tables", [])) for pagina in datos.values())
            
            print(f"Total botones encontrados: {total_botones}")
            print(f"Total inputs encontrados: {total_inputs}")
            print(f"Total links encontrados: {total_links}")
            print(f"Total formularios encontrados: {total_forms}")
            print(f"Total tablas encontradas: {total_tables}")
            
            print("\n🌐 PÁGINAS EXPLORADAS:")
            print("-" * 40)
            for i, (url, pagina) in enumerate(datos.items(), 1):
                titulo = pagina.get("titulo", "Sin título")
                timestamp = pagina.get("timestamp", "Sin timestamp")
                botones = len(pagina.get("botones", []))
                inputs = len(pagina.get("inputs", []))
                links = len(pagina.get("links", []))
                
                print(f"{i:2d}. {titulo}")
                print(f"    URL: {url}")
                print(f"    Botones: {botones}, Inputs: {inputs}, Links: {links}")
                print(f"    Timestamp: {timestamp}")
                print()
            
            # Mostrar elementos más importantes
            print("🔍 ELEMENTOS DESTACADOS:")
            print("-" * 40)
            
            # Botones más comunes
            todos_botones = []
            for pagina in datos.values():
                todos_botones.extend(pagina.get("botones", []))
            
            if todos_botones:
                botones_texto = [btn.get("texto", "") for btn in todos_botones if btn.get("texto")]
                if botones_texto:
                    print("Botones encontrados:")
                    for texto in set(botones_texto):
                        count = botones_texto.count(texto)
                        print(f"  - '{texto}': {count} veces")
                    print()
            
            # Inputs más comunes
            todos_inputs = []
            for pagina in datos.values():
                todos_inputs.extend(pagina.get("inputs", []))
            
            if todos_inputs:
                inputs_nombre = [inp.get("nombre", "") for inp in todos_inputs if inp.get("nombre")]
                if inputs_nombre:
                    print("Inputs encontrados:")
                    for nombre in set(inputs_nombre):
                        count = inputs_nombre.count(nombre)
                        print(f"  - '{nombre}': {count} veces")
                    print()
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")

def mostrar_progreso_actual():
    """Mostrar el progreso actual si existe el archivo"""
    if os.path.exists("progreso.txt"):
        print("📈 PROGRESO ACTUAL:")
        print("=" * 60)
        with open("progreso.txt", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("❌ No se encontró archivo de progreso")

def opciones_recuperacion():
    """Mostrar opciones de recuperación"""
    print("\n🛠️  OPCIONES DE RECUPERACIÓN:")
    print("=" * 60)
    print("1. Ver progreso actual")
    print("2. Ver datos recolectados")
    print("3. Ver reporte final (si existe)")
    print("4. Continuar exploración")
    print("5. Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            
            if opcion == "1":
                mostrar_progreso_actual()
            elif opcion == "2":
                cargar_y_mostrar_datos()
            elif opcion == "3":
                if os.path.exists("reporte_final.txt"):
                    print("\n📋 REPORTE FINAL:")
                    print("=" * 60)
                    with open("reporte_final.txt", "r", encoding="utf-8") as f:
                        print(f.read())
                else:
                    print("❌ No se encontró reporte final")
            elif opcion == "4":
                print("🚀 Para continuar la exploración, ejecuta:")
                print("   python smartagent.py")
                break
            elif opcion == "5":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Selecciona 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

def main():
    """Función principal"""
    mostrar_progreso()
    opciones_recuperacion()

if __name__ == "__main__":
    main() 