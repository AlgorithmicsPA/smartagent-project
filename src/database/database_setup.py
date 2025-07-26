#!/usr/bin/env python3
"""
Script de configuración de base de datos PostgreSQL para SmartAgent
Conecta con Neon DB y crea las tablas necesarias
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
import os

# Configuración de la base de datos
DATABASE_URL = "postgresql://neondb_owner:npg_I6sKUNeof9qb@ep-long-wave-adza01b9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseManager:
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
    
    def create_tables(self):
        """Crear las tablas necesarias para SmartAgent"""
        try:
            # ===== TABLAS PARA EXPLORACIÓN WEB =====
            
            # Tabla de páginas exploradas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS paginas (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    titulo TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de botones
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS botones (
                    id SERIAL PRIMARY KEY,
                    pagina_id INTEGER REFERENCES paginas(id) ON DELETE CASCADE,
                    texto TEXT,
                    tipo TEXT,
                    boton_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de inputs
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS inputs (
                    id SERIAL PRIMARY KEY,
                    pagina_id INTEGER REFERENCES paginas(id) ON DELETE CASCADE,
                    tipo TEXT,
                    nombre TEXT,
                    input_id TEXT,
                    placeholder TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de links
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id SERIAL PRIMARY KEY,
                    pagina_id INTEGER REFERENCES paginas(id) ON DELETE CASCADE,
                    url TEXT,
                    texto TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de formularios
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS formularios (
                    id SERIAL PRIMARY KEY,
                    pagina_id INTEGER REFERENCES paginas(id) ON DELETE CASCADE,
                    action TEXT,
                    method TEXT,
                    form_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de tablas HTML
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tablas_html (
                    id SERIAL PRIMARY KEY,
                    pagina_id INTEGER REFERENCES paginas(id) ON DELETE CASCADE,
                    tabla_id TEXT,
                    clases TEXT[],
                    filas INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de logs de exploración
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs_exploracion (
                    id SERIAL PRIMARY KEY,
                    mensaje TEXT,
                    nivel TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de estadísticas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS estadisticas (
                    id SERIAL PRIMARY KEY,
                    fecha DATE DEFAULT CURRENT_DATE,
                    paginas_exploradas INTEGER DEFAULT 0,
                    total_botones INTEGER DEFAULT 0,
                    total_inputs INTEGER DEFAULT 0,
                    total_links INTEGER DEFAULT 0,
                    total_formularios INTEGER DEFAULT 0,
                    total_tablas INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(fecha)
                )
            """)
            
            # ===== TABLAS PARA SISTEMA DE PEDIDOS =====
            
            # Tabla de repartidores
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS delivery_agents (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    contact_info VARCHAR(100),
                    current_location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla principal de pedidos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(50) NOT NULL UNIQUE,
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    pickup_address TEXT,
                    delivery_address TEXT,
                    distance_km DECIMAL(5, 2),
                    estimated_delivery_time INTERVAL,
                    actual_delivery_time INTERVAL,
                    product_type VARCHAR(100),
                    priority_level VARCHAR(50),
                    delivery_agent_id INTEGER REFERENCES delivery_agents(id)
                )
            """)
            
            # Productos y variantes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    is_perishable BOOLEAN DEFAULT FALSE,
                    average_waiting_time_minutes INTEGER,
                    notes TEXT
                )
            """)
            
            # Relación de productos con pedidos (muchos a muchos)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_products (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    quantity INTEGER DEFAULT 1
                )
            """)
            
            # Eventos del pedido (clicks, cambios de estado, OCR, etc.)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_events (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    event_type VARCHAR(100), -- Ej: 'click', 'status_change', 'ocr_text', etc.
                    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    screen_coordinates TEXT,
                    raw_data JSONB
                )
            """)
            
            # Tabla de historial de mensajes de WhatsApp relacionados a pedidos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_messages (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    sender VARCHAR(50), -- Ej: 'cliente', 'repartidor', 'sistema'
                    message TEXT,
                    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    xpath_used TEXT,
                    raw_html TEXT
                )
            """)
            
            # Tabla de botones detectados visualmente o por OCR
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detected_buttons (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    button_text VARCHAR(100),
                    xpath TEXT,
                    position TEXT, -- Ej: "x:1024,y:300"
                    confidence DECIMAL(5,2),
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logging.info("✅ Tablas creadas exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creando tablas: {e}")
            self.conn.rollback()
            return False
    
    def insert_pagina(self, url, titulo, datos):
        """Insertar datos de una página"""
        try:
            # Insertar página
            self.cursor.execute("""
                INSERT INTO paginas (url, titulo, timestamp)
                VALUES (%s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    titulo = EXCLUDED.titulo,
                    timestamp = EXCLUDED.timestamp
                RETURNING id
            """, (url, titulo, datos.get('timestamp')))
            
            pagina_id = self.cursor.fetchone()['id']
            
            # Insertar botones
            for boton in datos.get('botones', []):
                self.cursor.execute("""
                    INSERT INTO botones (pagina_id, texto, tipo, boton_id)
                    VALUES (%s, %s, %s, %s)
                """, (pagina_id, boton.get('texto'), boton.get('tipo'), boton.get('id')))
            
            # Insertar inputs
            for input_elem in datos.get('inputs', []):
                self.cursor.execute("""
                    INSERT INTO inputs (pagina_id, tipo, nombre, input_id, placeholder)
                    VALUES (%s, %s, %s, %s, %s)
                """, (pagina_id, input_elem.get('tipo'), input_elem.get('nombre'), 
                      input_elem.get('id'), input_elem.get('placeholder')))
            
            # Insertar links
            for link in datos.get('links', []):
                if isinstance(link, dict):
                    link_url = link.get('url', '')
                    link_texto = link.get('texto', '')
                else:
                    link_url = link
                    link_texto = ''
                self.cursor.execute("""
                    INSERT INTO links (pagina_id, url, texto)
                    VALUES (%s, %s, %s)
                """, (pagina_id, link_url, link_texto))
            
            # Insertar formularios
            for form in datos.get('forms', []):
                self.cursor.execute("""
                    INSERT INTO formularios (pagina_id, action, method, form_id)
                    VALUES (%s, %s, %s, %s)
                """, (pagina_id, form.get('action'), form.get('method'), form.get('id')))
            
            # Insertar tablas
            for tabla in datos.get('tables', []):
                self.cursor.execute("""
                    INSERT INTO tablas_html (pagina_id, tabla_id, clases, filas)
                    VALUES (%s, %s, %s, %s)
                """, (pagina_id, tabla.get('id'), tabla.get('class'), tabla.get('rows')))
            
            self.conn.commit()
            logging.info(f"✅ Datos de página insertados: {url}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error insertando datos de página {url}: {e}")
            self.conn.rollback()
            return False
    
    def get_estadisticas(self):
        """Obtener estadísticas de la base de datos"""
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
            logging.error(f"❌ Error obteniendo estadísticas: {e}")
            return None
    
    # ===== MÉTODOS PARA SISTEMA DE PEDIDOS =====
    
    def insert_delivery_agent(self, name, contact_info, current_location=None):
        """Insertar un repartidor"""
        try:
            self.cursor.execute("""
                INSERT INTO delivery_agents (name, contact_info, current_location)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (name, contact_info, current_location))
            
            agent_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logging.info(f"✅ Repartidor insertado: {name} (ID: {agent_id})")
            return agent_id
            
        except Exception as e:
            logging.error(f"❌ Error insertando repartidor: {e}")
            self.conn.rollback()
            return None
    
    def insert_order(self, order_number, status="pending", pickup_address=None, 
                    delivery_address=None, distance_km=None, product_type=None, 
                    priority_level="normal", delivery_agent_id=None):
        """Insertar un pedido"""
        try:
            self.cursor.execute("""
                INSERT INTO orders (order_number, status, pickup_address, delivery_address,
                                  distance_km, product_type, priority_level, delivery_agent_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (order_number, status, pickup_address, delivery_address,
                  distance_km, product_type, priority_level, delivery_agent_id))
            
            order_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logging.info(f"✅ Pedido insertado: {order_number} (ID: {order_id})")
            return order_id
            
        except Exception as e:
            logging.error(f"❌ Error insertando pedido: {e}")
            self.conn.rollback()
            return None
    
    def insert_order_event(self, order_id, event_type, screen_coordinates=None, raw_data=None):
        """Insertar un evento de pedido"""
        try:
            self.cursor.execute("""
                INSERT INTO order_events (order_id, event_type, screen_coordinates, raw_data)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (order_id, event_type, screen_coordinates, raw_data))
            
            event_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logging.info(f"✅ Evento insertado: {event_type} para pedido {order_id}")
            return event_id
            
        except Exception as e:
            logging.error(f"❌ Error insertando evento: {e}")
            self.conn.rollback()
            return None
    
    def insert_whatsapp_message(self, order_id, sender, message, xpath_used=None, raw_html=None):
        """Insertar mensaje de WhatsApp"""
        try:
            self.cursor.execute("""
                INSERT INTO whatsapp_messages (order_id, sender, message, xpath_used, raw_html)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (order_id, sender, message, xpath_used, raw_html))
            
            message_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logging.info(f"✅ Mensaje WhatsApp insertado: {sender} para pedido {order_id}")
            return message_id
            
        except Exception as e:
            logging.error(f"❌ Error insertando mensaje WhatsApp: {e}")
            self.conn.rollback()
            return None
    
    def insert_detected_button(self, order_id, button_text, xpath=None, position=None, confidence=None):
        """Insertar botón detectado"""
        try:
            self.cursor.execute("""
                INSERT INTO detected_buttons (order_id, button_text, xpath, position, confidence)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (order_id, button_text, xpath, position, confidence))
            
            button_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logging.info(f"✅ Botón detectado insertado: {button_text} para pedido {order_id}")
            return button_id
            
        except Exception as e:
            logging.error(f"❌ Error insertando botón detectado: {e}")
            self.conn.rollback()
            return None
    
    def get_orders_by_status(self, status):
        """Obtener pedidos por estado"""
        try:
            self.cursor.execute("""
                SELECT o.*, da.name as agent_name
                FROM orders o
                LEFT JOIN delivery_agents da ON o.delivery_agent_id = da.id
                WHERE o.status = %s
                ORDER BY o.created_at DESC
            """, (status,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo pedidos por estado: {e}")
            return []
    
    def get_order_events(self, order_id):
        """Obtener eventos de un pedido"""
        try:
            self.cursor.execute("""
                SELECT * FROM order_events
                WHERE order_id = %s
                ORDER BY event_timestamp DESC
            """, (order_id,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo eventos de pedido: {e}")
            return []
    
    def update_order_status(self, order_id, new_status):
        """Actualizar estado de un pedido"""
        try:
            self.cursor.execute("""
                UPDATE orders SET status = %s WHERE id = %s
            """, (new_status, order_id))
            
            self.conn.commit()
            logging.info(f"✅ Estado de pedido {order_id} actualizado a: {new_status}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error actualizando estado de pedido: {e}")
            self.conn.rollback()
            return False
    
    def cargar_datos_json(self, json_file):
        """Cargar datos desde archivo JSON a la base de datos"""
        if not os.path.exists(json_file):
            logging.error(f"❌ Archivo no encontrado: {json_file}")
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            logging.info(f"📊 Cargando {len(datos)} páginas desde {json_file}")
            
            for url, pagina_data in datos.items():
                titulo = pagina_data.get('titulo', '')
                self.insert_pagina(url, titulo, pagina_data)
            
            logging.info("✅ Datos cargados exitosamente a la base de datos")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error cargando datos desde JSON: {e}")
            return False

def main():
    """Función principal"""
    print("=" * 60)
    print("    SMARTAGENT - CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Crear instancia del gestor de base de datos
    db = DatabaseManager(DATABASE_URL)
    
    if not db.connect():
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        # Crear tablas
        print("\n🔧 Creando tablas...")
        if db.create_tables():
            print("✅ Tablas creadas exitosamente")
        else:
            print("❌ Error creando tablas")
            return
        
        # Mostrar estadísticas iniciales
        print("\n📊 Estadísticas iniciales:")
        stats = db.get_estadisticas()
        if stats:
            print(f"  Páginas: {stats['total_paginas']}")
            print(f"  Botones: {stats['total_botones']}")
            print(f"  Inputs: {stats['total_inputs']}")
            print(f"  Links: {stats['total_links']}")
            print(f"  Formularios: {stats['total_formularios']}")
            print(f"  Tablas: {stats['total_tablas']}")
        
        # Cargar datos existentes si hay archivo JSON
        if os.path.exists("estructura.json"):
            print("\n📥 ¿Cargar datos existentes desde estructura.json? (s/n): ", end="")
            respuesta = input().lower().strip()
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                if db.cargar_datos_json("estructura.json"):
                    print("✅ Datos cargados exitosamente")
                    
                    # Mostrar estadísticas después de la carga
                    print("\n📊 Estadísticas después de la carga:")
                    stats = db.get_estadisticas()
                    if stats:
                        print(f"  Páginas: {stats['total_paginas']}")
                        print(f"  Botones: {stats['total_botones']}")
                        print(f"  Inputs: {stats['total_inputs']}")
                        print(f"  Links: {stats['total_links']}")
                        print(f"  Formularios: {stats['total_formularios']}")
                        print(f"  Tablas: {stats['total_tablas']}")
        
        print("\n✅ Configuración de base de datos completada")
        print("\n📝 Próximos pasos:")
        print("1. Actualizar smartagent.py para usar la base de datos")
        print("2. Ejecutar: python smartagent.py")
        print("3. Los datos se guardarán automáticamente en PostgreSQL")
        
    except Exception as e:
        logging.error(f"❌ Error en la configuración: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main() 