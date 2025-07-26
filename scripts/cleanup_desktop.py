#!/usr/bin/env python3
"""
Cleanup Desktop - Script para limpiar archivos del escritorio
Mueve archivos relacionados con SmartAgent al proyecto organizado
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime

class DesktopCleanup:
    def __init__(self):
        self.desktop_path = Path.home() / "OneDrive" / "Desktop"
        self.project_path = self.desktop_path / "smartagent-project"
        self.backup_path = self.desktop_path / "smartagent-backup"
        
        # Archivos y carpetas a mover al proyecto
        self.smartagent_files = [
            "smartagent.py",
            "smartagent_enhanced.py",
            "smartagent_orders.py",
            "test_*.py",
            "login_page.*",
            "*.log",
            "*.json",
            "*.txt",
            "*.bat",
            "*.md",
            "requirements.txt",
            "logs/",
            "besmart*/",
            "Algo/"
        ]
        
        # Archivos a eliminar (archivos temporales)
        self.temp_files = [
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.old",
            "Thumbs.db",
            "desktop.ini"
        ]
    
    def scan_desktop(self):
        """Escanear el escritorio en busca de archivos relacionados"""
        print("🔍 Escaneando escritorio...")
        
        found_files = []
        found_dirs = []
        
        for pattern in self.smartagent_files:
            matches = glob.glob(str(self.desktop_path / pattern))
            for match in matches:
                path = Path(match)
                if path.is_file():
                    found_files.append(path)
                elif path.is_dir():
                    found_dirs.append(path)
        
        return found_files, found_dirs
    
    def create_backup(self):
        """Crear backup antes de limpiar"""
        if not self.backup_path.exists():
            self.backup_path.mkdir(parents=True)
            print(f"📁 Backup creado en: {self.backup_path}")
        else:
            print(f"📁 Backup existente en: {self.backup_path}")
    
    def move_files_to_project(self, files, dirs):
        """Mover archivos al proyecto organizado"""
        print("\n📦 Moviendo archivos al proyecto...")
        
        moved_count = 0
        
        # Mover archivos
        for file_path in files:
            try:
                if file_path.name not in ["smartagent-project", "smartagent-backup"]:
                    dest_path = self.project_path / file_path.name
                    
                    # Si el archivo ya existe, crear copia con timestamp
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name_parts = file_path.stem, timestamp, file_path.suffix
                        new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        dest_path = self.project_path / new_name
                    
                    shutil.move(str(file_path), str(dest_path))
                    print(f"   ✅ Movido: {file_path.name}")
                    moved_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error moviendo {file_path.name}: {e}")
        
        # Mover directorios
        for dir_path in dirs:
            try:
                if dir_path.name not in ["smartagent-project", "smartagent-backup"]:
                    dest_path = self.project_path / dir_path.name
                    
                    # Si el directorio ya existe, crear copia con timestamp
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_name = f"{dir_path.name}_{timestamp}"
                        dest_path = self.project_path / new_name
                    
                    shutil.move(str(dir_path), str(dest_path))
                    print(f"   ✅ Movido: {dir_path.name}/")
                    moved_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error moviendo {dir_path.name}/: {e}")
        
        return moved_count
    
    def cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        print("\n🧹 Limpiando archivos temporales...")
        
        removed_count = 0
        
        for pattern in self.temp_files:
            matches = glob.glob(str(self.desktop_path / pattern))
            for match in matches:
                try:
                    path = Path(match)
                    if path.is_file():
                        path.unlink()
                        print(f"   🗑️ Eliminado: {path.name}")
                        removed_count += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando {path.name}: {e}")
        
        return removed_count
    
    def generate_report(self, files, dirs, moved_count, removed_count):
        """Generar reporte de limpieza"""
        print("\n📊 REPORTE DE LIMPIEZA")
        print("=" * 50)
        print(f"   Archivos encontrados: {len(files)}")
        print(f"   Directorios encontrados: {len(dirs)}")
        print(f"   Archivos movidos: {moved_count}")
        print(f"   Archivos temporales eliminados: {removed_count}")
        print(f"   Backup disponible en: {self.backup_path}")
        
        if files or dirs:
            print("\n📁 ARCHIVOS ENCONTRADOS:")
            for file_path in files:
                print(f"   📄 {file_path.name}")
            for dir_path in dirs:
                print(f"   📁 {dir_path.name}/")
    
    def run_cleanup(self):
        """Ejecutar proceso de limpieza completo"""
        print("🧹 LIMPIEZA DEL ESCRITORIO - SmartAgent Project")
        print("=" * 60)
        
        try:
            # Crear backup
            self.create_backup()
            
            # Escanear escritorio
            files, dirs = self.scan_desktop()
            
            if not files and not dirs:
                print("✅ No se encontraron archivos para limpiar")
                return
            
            # Mostrar archivos encontrados
            print(f"\n📋 Archivos encontrados: {len(files)}")
            print(f"📋 Directorios encontrados: {len(dirs)}")
            
            # Confirmar limpieza
            response = input("\n¿Deseas proceder con la limpieza? (y/N): ").lower()
            if response != 'y':
                print("❌ Limpieza cancelada")
                return
            
            # Mover archivos al proyecto
            moved_count = self.move_files_to_project(files, dirs)
            
            # Limpiar archivos temporales
            removed_count = self.cleanup_temp_files()
            
            # Generar reporte
            self.generate_report(files, dirs, moved_count, removed_count)
            
            print("\n✅ Limpieza completada exitosamente")
            
        except Exception as e:
            print(f"\n❌ Error durante la limpieza: {e}")

def main():
    """Función principal"""
    cleanup = DesktopCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main() 