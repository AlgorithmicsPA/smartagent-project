#!/usr/bin/env python3
"""
Script para mostrar la estructura completa de la base de datos mejorada
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_I6sKUNeof9qb@ep-long-wave-adza01b9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseStructureViewer:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logging.info("✅ Conexión a PostgreSQL establecida")
            return True
        except Exception as e:
            logging.error(f"❌ Error conectando a la base de datos: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.info("🔌 Conexión a PostgreSQL cerrada")
    
    def get_all_tables(self):
        """Obtener todas las tablas de la base de datos"""
        try:
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in self.cursor.fetchall()]
            return tables
        except Exception as e:
            logging.error(f"❌ Error obteniendo tablas: {e}")
            return []
    
    def get_table_structure(self, table_name):
        """Obtener estructura de una tabla específica"""
        try:
            self.cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            columns = self.cursor.fetchall()
            return columns
        except Exception as e:
            logging.error(f"❌ Error obteniendo estructura de {table_name}: {e}")
            return []
    
    def get_foreign_keys(self, table_name):
        """Obtener claves foráneas de una tabla"""
        try:
            self.cursor.execute("""
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = %s
            """, (table_name,))
            foreign_keys = self.cursor.fetchall()
            return foreign_keys
        except Exception as e:
            logging.error(f"❌ Error obteniendo claves foráneas de {table_name}: {e}")
            return []
    
    def get_table_count(self, table_name):
        """Obtener número de registros en una tabla"""
        try:
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            logging.error(f"❌ Error contando registros en {table_name}: {e}")
            return 0
    
    def show_complete_structure(self):
        """Mostrar estructura completa de la base de datos"""
        print("\n" + "="*80)
        print("🗄️  ESTRUCTURA COMPLETA DE LA BASE DE DATOS MEJORADA")
        print("="*80)
        
        tables = self.get_all_tables()
        
        # Agrupar tablas por categoría
        web_scraping_tables = ['paginas', 'botones', 'inputs', 'links', 'formularios', 'tablas_html', 'logs_exploracion', 'estadisticas']
        order_system_tables = ['orders', 'delivery_agents', 'order_events', 'whatsapp_messages', 'detected_buttons', 'products', 'order_products']
        enhanced_tables = ['customers', 'delivery_zones', 'operating_hours', 'product_categories', 'inventory', 'pricing', 'payment_methods', 'payment_transactions', 'reviews', 'notifications', 'system_config', 'audit_logs', 'analytics']
        
        categories = [
            ("🌐 TABLAS DE EXPLORACIÓN WEB", web_scraping_tables),
            ("📦 TABLAS DEL SISTEMA DE PEDIDOS", order_system_tables),
            ("🚀 TABLAS COMPLEMENTARIAS MEJORADAS", enhanced_tables)
        ]
        
        total_tables = 0
        
        for category_name, category_tables in categories:
            print(f"\n{category_name}")
            print("-" * len(category_name))
            
            for table_name in category_tables:
                if table_name in tables:
                    total_tables += 1
                    count = self.get_table_count(table_name)
                    print(f"\n📋 {table_name.upper()} ({count} registros)")
                    
                    # Mostrar estructura
                    columns = self.get_table_structure(table_name)
                    for col in columns:
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                        length = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                        print(f"   ├── {col['column_name']}: {col['data_type']}{length} {nullable}{default}")
                    
                    # Mostrar claves foráneas
                    foreign_keys = self.get_foreign_keys(table_name)
                    if foreign_keys:
                        print("   └── 🔗 Claves foráneas:")
                        for fk in foreign_keys:
                            print(f"       ├── {fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        print(f"\n" + "="*80)
        print(f"📊 RESUMEN: {total_tables} tablas en total")
        print("="*80)
        
        # Mostrar relaciones principales
        print("\n🔗 RELACIONES PRINCIPALES DEL SISTEMA:")
        print("-" * 50)
        print("📦 orders → customers (cliente del pedido)")
        print("📦 orders → delivery_agents (repartidor asignado)")
        print("📦 orders → delivery_zones (zona de entrega)")
        print("📦 order_products → orders + products (productos del pedido)")
        print("📦 order_events → orders (eventos del pedido)")
        print("📦 whatsapp_messages → orders (mensajes relacionados)")
        print("📦 payment_transactions → orders (transacciones de pago)")
        print("📦 reviews → orders + customers (calificaciones)")
        print("📦 notifications → orders (notificaciones)")
        print("📦 products → product_categories (categoría del producto)")
        print("📦 inventory → products (inventario del producto)")
        print("📦 pricing → products (precios del producto)")
        print("📦 paginas → botones, inputs, links, formularios, tablas_html (elementos web)")
        
        print("\n🎯 FUNCIONALIDADES DISPONIBLES:")
        print("-" * 40)
        print("✅ Exploración web automatizada")
        print("✅ Gestión completa de pedidos")
        print("✅ Sistema de clientes")
        print("✅ Gestión de repartidores")
        print("✅ Zonas de entrega con tarifas")
        print("✅ Categorización de productos")
        print("✅ Control de inventario")
        print("✅ Sistema de precios y promociones")
        print("✅ Múltiples métodos de pago")
        print("✅ Sistema de calificaciones")
        print("✅ Notificaciones automáticas")
        print("✅ Configuración del sistema")
        print("✅ Logs de auditoría")
        print("✅ Analytics y reportes")
        print("✅ Integración con WhatsApp")

def main():
    """Función principal"""
    viewer = DatabaseStructureViewer(DATABASE_URL)
    
    if viewer.connect():
        viewer.show_complete_structure()
        viewer.disconnect()

if __name__ == "__main__":
    main() 