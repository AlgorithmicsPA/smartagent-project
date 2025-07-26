#!/usr/bin/env python3
"""
Script para consultar la base de datos PostgreSQL del SmartAgent
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Configuración de la base de datos
DATABASE_URL = "postgresql://neondb_owner:npg_I6sKUNeof9qb@ep-long-wave-adza01b9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

class DatabaseQuery:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Conexión a PostgreSQL establecida")
            return True
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Conexión a PostgreSQL cerrada")
    
    def get_estadisticas_generales(self):
        """Obtener estadísticas generales"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT p.id) as total_paginas,
                    COUNT(b.id) as total_botones,
                    COUNT(i.id) as total_inputs,
                    COUNT(l.id) as total_links,
                    COUNT(f.id) as total_formularios,
                    COUNT(t.id) as total_tablas
                FROM paginas p
                LEFT JOIN botones b ON p.id = b.pagina_id
                LEFT JOIN inputs i ON p.id = i.pagina_id
                LEFT JOIN links l ON p.id = l.pagina_id
                LEFT JOIN formularios f ON p.id = f.pagina_id
                LEFT JOIN tablas_html t ON p.id = t.pagina_id
            """)
            
            stats = self.cursor.fetchone()
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None
    
    def get_paginas_exploradas(self, limit=10):
        """Obtener páginas exploradas"""
        try:
            self.cursor.execute("""
                SELECT url, titulo, timestamp, created_at
                FROM paginas
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error obteniendo páginas: {e}")
            return []
    
    def get_botones_mas_comunes(self, limit=10):
        """Obtener botones más comunes"""
        try:
            self.cursor.execute("""
                SELECT texto, COUNT(*) as cantidad
                FROM botones
                WHERE texto IS NOT NULL AND texto != ''
                GROUP BY texto
                ORDER BY cantidad DESC
                LIMIT %s
            """, (limit,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error obteniendo botones: {e}")
            return []
    
    def get_inputs_mas_comunes(self, limit=10):
        """Obtener inputs más comunes"""
        try:
            self.cursor.execute("""
                SELECT nombre, tipo, COUNT(*) as cantidad
                FROM inputs
                WHERE nombre IS NOT NULL AND nombre != ''
                GROUP BY nombre, tipo
                ORDER BY cantidad DESC
                LIMIT %s
            """, (limit,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error obteniendo inputs: {e}")
            return []
    
    def buscar_por_url(self, url_pattern):
        """Buscar páginas por patrón de URL"""
        try:
            self.cursor.execute("""
                SELECT url, titulo, timestamp
                FROM paginas
                WHERE url ILIKE %s
                ORDER BY created_at DESC
            """, (f'%{url_pattern}%',))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error buscando por URL: {e}")
            return []
    
    def get_detalles_pagina(self, url):
        """Obtener detalles completos de una página"""
        try:
            # Obtener página
            self.cursor.execute("""
                SELECT * FROM paginas WHERE url = %s
            """, (url,))
            
            pagina = self.cursor.fetchone()
            if not pagina:
                return None
            
            # Obtener botones
            self.cursor.execute("""
                SELECT * FROM botones WHERE pagina_id = %s
            """, (pagina['id'],))
            botones = self.cursor.fetchall()
            
            # Obtener inputs
            self.cursor.execute("""
                SELECT * FROM inputs WHERE pagina_id = %s
            """, (pagina['id'],))
            inputs = self.cursor.fetchall()
            
            # Obtener links
            self.cursor.execute("""
                SELECT * FROM links WHERE pagina_id = %s
            """, (pagina['id'],))
            links = self.cursor.fetchall()
            
            # Obtener formularios
            self.cursor.execute("""
                SELECT * FROM formularios WHERE pagina_id = %s
            """, (pagina['id'],))
            formularios = self.cursor.fetchall()
            
            # Obtener tablas
            self.cursor.execute("""
                SELECT * FROM tablas_html WHERE pagina_id = %s
            """, (pagina['id'],))
            tablas = self.cursor.fetchall()
            
            return {
                'pagina': pagina,
                'botones': botones,
                'inputs': inputs,
                'links': links,
                'formularios': formularios,
                'tablas': tablas
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo detalles de página: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "="*60)
    print("    SMARTAGENT - CONSULTA DE BASE DE DATOS")
    print("="*60)
    print("1. Estadísticas generales")
    print("2. Páginas exploradas (últimas 10)")
    print("3. Botones más comunes")
    print("4. Inputs más comunes")
    print("5. Buscar por URL")
    print("6. Detalles de página específica")
    print("7. Exportar datos a JSON")
    print("8. Salir")
    print("="*60)

def main():
    """Función principal"""
    db = DatabaseQuery(DATABASE_URL)
    
    if not db.connect():
        return
    
    try:
        while True:
            mostrar_menu()
            opcion = input("\nSelecciona una opción (1-8): ").strip()
            
            if opcion == "1":
                print("\n📊 ESTADÍSTICAS GENERALES:")
                print("-" * 40)
                stats = db.get_estadisticas_generales()
                if stats:
                    print(f"Páginas exploradas: {stats['total_paginas']}")
                    print(f"Total botones: {stats['total_botones']}")
                    print(f"Total inputs: {stats['total_inputs']}")
                    print(f"Total links: {stats['total_links']}")
                    print(f"Total formularios: {stats['total_formularios']}")
                    print(f"Total tablas: {stats['total_tablas']}")
                
            elif opcion == "2":
                print("\n🌐 PÁGINAS EXPLORADAS (últimas 10):")
                print("-" * 40)
                paginas = db.get_paginas_exploradas(10)
                for i, pagina in enumerate(paginas, 1):
                    print(f"{i}. {pagina['titulo'] or 'Sin título'}")
                    print(f"   URL: {pagina['url']}")
                    print(f"   Explorada: {pagina['created_at']}")
                    print()
                
            elif opcion == "3":
                print("\n🔘 BOTONES MÁS COMUNES:")
                print("-" * 40)
                botones = db.get_botones_mas_comunes(10)
                for i, boton in enumerate(botones, 1):
                    print(f"{i}. '{boton['texto']}': {boton['cantidad']} veces")
                
            elif opcion == "4":
                print("\n📝 INPUTS MÁS COMUNES:")
                print("-" * 40)
                inputs = db.get_inputs_mas_comunes(10)
                for i, input_elem in enumerate(inputs, 1):
                    print(f"{i}. '{input_elem['nombre']}' ({input_elem['tipo']}): {input_elem['cantidad']} veces")
                
            elif opcion == "5":
                print("\n🔍 BUSCAR POR URL:")
                print("-" * 40)
                patron = input("Ingresa un patrón de URL a buscar: ").strip()
                if patron:
                    resultados = db.buscar_por_url(patron)
                    if resultados:
                        for i, resultado in enumerate(resultados, 1):
                            print(f"{i}. {resultado['titulo'] or 'Sin título'}")
                            print(f"   URL: {resultado['url']}")
                            print(f"   Explorada: {resultado['timestamp']}")
                            print()
                    else:
                        print("❌ No se encontraron resultados")
                
            elif opcion == "6":
                print("\n📋 DETALLES DE PÁGINA:")
                print("-" * 40)
                url = input("Ingresa la URL completa de la página: ").strip()
                if url:
                    detalles = db.get_detalles_pagina(url)
                    if detalles:
                        pagina = detalles['pagina']
                        print(f"Título: {pagina['titulo']}")
                        print(f"URL: {pagina['url']}")
                        print(f"Explorada: {pagina['timestamp']}")
                        print(f"Botones: {len(detalles['botones'])}")
                        print(f"Inputs: {len(detalles['inputs'])}")
                        print(f"Links: {len(detalles['links'])}")
                        print(f"Formularios: {len(detalles['formularios'])}")
                        print(f"Tablas: {len(detalles['tablas'])}")
                    else:
                        print("❌ Página no encontrada")
                
            elif opcion == "7":
                print("\n💾 EXPORTAR DATOS:")
                print("-" * 40)
                filename = f"export_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # Obtener todos los datos
                paginas = db.get_paginas_exploradas(1000)  # Obtener todas
                botones = db.get_botones_mas_comunes(1000)
                inputs = db.get_inputs_mas_comunes(1000)
                
                datos_export = {
                    'fecha_export': datetime.now().isoformat(),
                    'paginas': [dict(p) for p in paginas],
                    'botones_comunes': [dict(b) for b in botones],
                    'inputs_comunes': [dict(i) for i in inputs]
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(datos_export, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"✅ Datos exportados a: {filename}")
                
            elif opcion == "8":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1-8.")
            
            input("\nPresiona Enter para continuar...")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main() 