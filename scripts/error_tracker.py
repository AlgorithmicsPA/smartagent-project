#!/usr/bin/env python3
"""
Error Tracker - Sistema automatizado de seguimiento de errores
Ejecuta el sistema SmartAgent y captura errores para documentación
"""

import subprocess
import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path

class ErrorTracker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.error_file = self.project_root / "ERROR_TRACKING.md"
        self.error_count = 0
        self.errors_found = []
        
    def run_system_test(self):
        """Ejecutar el sistema y capturar errores"""
        print("🔍 Iniciando seguimiento de errores...")
        print("=" * 50)
        
        try:
            # Cambiar al directorio del proyecto
            os.chdir(self.project_root)
            
            # Ejecutar el sistema principal
            result = subprocess.run(
                ["python", "main.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            # Capturar salida
            stdout = result.stdout
            stderr = result.stderr
            
            print("📊 Resultado de la ejecución:")
            print(f"   Código de salida: {result.returncode}")
            print(f"   Tiempo de ejecución: {result.returncode}")
            
            # Analizar errores
            self.analyze_output(stdout, stderr)
            
        except subprocess.TimeoutExpired:
            self.add_error("TIMEOUT", "El sistema tardó más de 5 minutos en ejecutarse", "CRÍTICA")
        except Exception as e:
            self.add_error("EXECUTION_ERROR", f"Error ejecutando el sistema: {str(e)}", "ALTA")
    
    def analyze_output(self, stdout, stderr):
        """Analizar la salida en busca de errores"""
        print("\n🔍 Analizando salida en busca de errores...")
        
        # Patrones de error comunes
        error_patterns = [
            (r"ERROR - ❌ (.+)", "ERROR"),
            (r"Exception: (.+)", "EXCEPTION"),
            (r"Traceback \(most recent call last\):", "TRACEBACK"),
            (r"ModuleNotFoundError: (.+)", "MODULE_ERROR"),
            (r"ImportError: (.+)", "IMPORT_ERROR"),
            (r"FileNotFoundError: (.+)", "FILE_ERROR"),
            (r"PermissionError: (.+)", "PERMISSION_ERROR"),
            (r"TimeoutError: (.+)", "TIMEOUT_ERROR"),
            (r"ConnectionError: (.+)", "CONNECTION_ERROR"),
            (r"❌ (.+)", "GENERAL_ERROR")
        ]
        
        # Buscar errores en stdout
        for pattern, error_type in error_patterns:
            matches = re.findall(pattern, stdout, re.MULTILINE)
            for match in matches:
                self.add_error(error_type, match.strip(), self.classify_severity(error_type))
        
        # Buscar errores en stderr
        if stderr:
            for pattern, error_type in error_patterns:
                matches = re.findall(pattern, stderr, re.MULTILINE)
                for match in matches:
                    self.add_error(error_type, match.strip(), self.classify_severity(error_type))
        
        # Buscar errores específicos del ChromeDriver
        chromedriver_errors = re.findall(r"ChromeDriver.*?Error.*?:(.+)", stdout + stderr, re.MULTILINE)
        for error in chromedriver_errors:
            self.add_error("CHROMEDRIVER_ERROR", error.strip(), "ALTA")
    
    def classify_severity(self, error_type):
        """Clasificar la severidad del error"""
        severity_map = {
            "TIMEOUT": "CRÍTICA",
            "EXECUTION_ERROR": "ALTA",
            "CHROMEDRIVER_ERROR": "ALTA",
            "CONNECTION_ERROR": "ALTA",
            "MODULE_ERROR": "MEDIA",
            "IMPORT_ERROR": "MEDIA",
            "FILE_ERROR": "MEDIA",
            "PERMISSION_ERROR": "ALTA",
            "TIMEOUT_ERROR": "CRÍTICA",
            "EXCEPTION": "MEDIA",
            "TRACEBACK": "MEDIA",
            "ERROR": "MEDIA",
            "GENERAL_ERROR": "BAJA"
        }
        return severity_map.get(error_type, "MEDIA")
    
    def add_error(self, error_type, message, severity):
        """Agregar un error al seguimiento"""
        self.error_count += 1
        error = {
            "id": self.error_count,
            "type": error_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ACTIVO"
        }
        self.errors_found.append(error)
        print(f"🚨 Error #{self.error_count} detectado: {error_type} - {message[:50]}...")
    
    def update_error_file(self):
        """Actualizar el archivo de seguimiento de errores"""
        if not self.errors_found:
            print("✅ No se detectaron errores nuevos")
            return
        
        print(f"\n📝 Actualizando archivo de seguimiento con {len(self.errors_found)} errores...")
        
        # Leer el archivo actual
        if self.error_file.exists():
            with open(self.error_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # Generar contenido de errores
        errors_content = self.generate_errors_content()
        
        # Actualizar el archivo
        updated_content = self.update_content_with_errors(content, errors_content)
        
        with open(self.error_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Archivo de seguimiento actualizado")
    
    def generate_errors_content(self):
        """Generar contenido de errores en formato markdown"""
        content = "\n## 🚨 ERRORES ACTIVOS\n\n"
        
        if not self.errors_found:
            content += "### No hay errores activos actualmente\n"
        else:
            for error in self.errors_found:
                content += f"""### Error #{error['id']} - {error['type']}
- **Fecha detectado:** {error['timestamp']}
- **Archivo afectado:** `smartagent-project/`
- **Severidad:** {error['severity']}
- **Estado:** {error['status']}

#### 🔍 Descripción del Error
```
{error['message']}
```

#### 📊 Información Técnica
- **Tipo de error:** {error['type']}
- **Mensaje de error:** `{error['message']}`

#### 🎯 Impacto
- **Funcionalidad afectada:** Sistema principal
- **Usuario afectado:** Desarrollador
- **Frecuencia:** Detectado en esta ejecución

#### 🔧 Solución Implementada
```
[Pendiente de implementar]
```

#### ✅ Verificación
- **Fecha resuelto:** Pendiente
- **Método de verificación:** Pendiente
- **Resultado:** Pendiente

#### 📚 Notas Adicionales
Error detectado automáticamente por el sistema de seguimiento.

---
"""
        
        return content
    
    def update_content_with_errors(self, content, errors_content):
        """Actualizar el contenido del archivo con los nuevos errores"""
        try:
            # Buscar la sección de errores activos
            if "## 🚨 ERRORES ACTIVOS" in content:
                # Reemplazar la sección existente
                start_marker = "## 🚨 ERRORES ACTIVOS"
                end_marker = "\n---\n"
                
                start_pos = content.find(start_marker)
                end_pos = content.find(end_marker, start_pos)
                
                if start_pos != -1 and end_pos != -1:
                    before_errors = content[:start_pos]
                    after_errors = content[end_pos:]
                    updated_content = before_errors + errors_content + after_errors
                else:
                    updated_content = content + "\n" + errors_content
            else:
                # Insertar después del resumen
                if "## 📋 Resumen de Estado" in content:
                    summary_end = content.find("\n---\n")
                    if summary_end != -1:
                        before_summary = content[:summary_end + 6]
                        after_summary = content[summary_end + 6:]
                        updated_content = before_summary + errors_content + "\n---\n" + after_summary
                    else:
                        updated_content = content + "\n" + errors_content
                else:
                    # Agregar al final
                    updated_content = content + "\n" + errors_content
            
            # Actualizar contadores
            updated_content = self.update_counters(updated_content)
            
            return updated_content
            
        except Exception as e:
            print(f"⚠️ Error actualizando contenido: {e}")
            return content + "\n" + errors_content
    
    def update_counters(self, content):
        """Actualizar contadores en el archivo"""
        # Actualizar total de errores
        total_errors = len(self.errors_found)
        content = re.sub(
            r"(\*\*Total de errores:\*\* )\d+",
            r"\1" + str(total_errors),
            content
        )
        
        # Actualizar errores activos
        active_errors = len([e for e in self.errors_found if e['status'] == 'ACTIVO'])
        content = re.sub(
            r"(\*\*Errores activos:\*\* )\d+",
            r"\1" + str(active_errors),
            content
        )
        
        # Actualizar fecha de última actualización
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(
            r"(\*\*Fecha:\*\* ).*",
            r"\1" + current_time,
            content
        )
        
        return content
    
    def generate_report(self):
        """Generar reporte de la sesión"""
        print("\n📊 REPORTE DE SEGUIMIENTO DE ERRORES")
        print("=" * 50)
        print(f"   Errores detectados: {len(self.errors_found)}")
        print(f"   Errores críticos: {len([e for e in self.errors_found if e['severity'] == 'CRÍTICA'])}")
        print(f"   Errores altos: {len([e for e in self.errors_found if e['severity'] == 'ALTA'])}")
        print(f"   Errores medios: {len([e for e in self.errors_found if e['severity'] == 'MEDIA'])}")
        print(f"   Errores bajos: {len([e for e in self.errors_found if e['severity'] == 'BAJA'])}")
        
        if self.errors_found:
            print("\n🚨 ERRORES DETECTADOS:")
            for error in self.errors_found:
                print(f"   #{error['id']} - {error['type']}: {error['message'][:60]}...")
        
        print(f"\n📁 Archivo de seguimiento: {self.error_file}")
        print("✅ Seguimiento completado")

def main():
    """Función principal"""
    tracker = ErrorTracker()
    
    try:
        # Ejecutar prueba del sistema
        tracker.run_system_test()
        
        # Actualizar archivo de seguimiento
        tracker.update_error_file()
        
        # Generar reporte
        tracker.generate_report()
        
    except KeyboardInterrupt:
        print("\n⚠️ Seguimiento interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el seguimiento: {e}")

if __name__ == "__main__":
    main() 