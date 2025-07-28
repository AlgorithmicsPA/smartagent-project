#!/usr/bin/env python3
"""
Script de mejora de base de datos PostgreSQL para SmartAgent
Agrega tablas complementarias y relaciones adicionales
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***/***DB_OCULTA***?sslmode=require&channel_binding=require")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseEnhancer:
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
    
    def create_enhanced_tables(self):
        """Crear tablas complementarias para mejorar el sistema"""
        try:
            # ===== TABLAS COMPLEMENTARIAS PARA GESTIÓN AVANZADA =====
            
            # Tabla de clientes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de zonas de entrega
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS delivery_zones (
                    id SERIAL PRIMARY KEY,
                    zone_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    estimated_delivery_time_minutes INTEGER,
                    delivery_fee DECIMAL(8,2),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de horarios de operación
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS operating_hours (
                    id SERIAL PRIMARY KEY,
                    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6),
                    open_time TIME,
                    close_time TIME,
                    is_open BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de categorías de productos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_category_id INTEGER REFERENCES product_categories(id),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de inventario
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    quantity_available INTEGER DEFAULT 0,
                    quantity_reserved INTEGER DEFAULT 0,
                    reorder_point INTEGER DEFAULT 10,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de precios y promociones
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pricing (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    base_price DECIMAL(10,2) NOT NULL,
                    sale_price DECIMAL(10,2),
                    discount_percentage DECIMAL(5,2),
                    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    valid_until TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabla de métodos de pago
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de transacciones de pago
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    payment_method_id INTEGER REFERENCES payment_methods(id),
                    amount DECIMAL(10,2) NOT NULL,
                    transaction_id VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'pending',
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de calificaciones y reseñas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    customer_id INTEGER REFERENCES customers(id),
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de notificaciones
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    notification_type VARCHAR(50), -- 'sms', 'email', 'push', 'whatsapp'
                    recipient VARCHAR(100),
                    message TEXT,
                    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de configuración del sistema
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id SERIAL PRIMARY KEY,
                    config_key VARCHAR(100) UNIQUE NOT NULL,
                    config_value TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de logs de auditoría
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    table_name VARCHAR(50),
                    record_id INTEGER,
                    action VARCHAR(20), -- 'INSERT', 'UPDATE', 'DELETE'
                    old_values JSONB,
                    new_values JSONB,
                    user_id VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de reportes y analytics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    report_date DATE DEFAULT CURRENT_DATE,
                    total_orders INTEGER DEFAULT 0,
                    total_revenue DECIMAL(12,2) DEFAULT 0,
                    average_order_value DECIMAL(10,2) DEFAULT 0,
                    orders_by_status JSONB,
                    top_products JSONB,
                    delivery_performance JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(report_date)
                )
            """)
            
            # ===== MEJORAS A TABLAS EXISTENTES =====
            
            # Agregar columna customer_id a orders si no existe
            try:
                self.cursor.execute("""
                    ALTER TABLE orders 
                    ADD COLUMN IF NOT EXISTS customer_id INTEGER REFERENCES customers(id)
                """)
            except Exception as e:
                logging.warning(f"Columna customer_id ya existe o error: {e}")
            
            # Agregar columna delivery_zone_id a orders si no existe
            try:
                self.cursor.execute("""
                    ALTER TABLE orders 
                    ADD COLUMN IF NOT EXISTS delivery_zone_id INTEGER REFERENCES delivery_zones(id)
                """)
            except Exception as e:
                logging.warning(f"Columna delivery_zone_id ya existe o error: {e}")
            
            # Agregar columna category_id a products si no existe
            try:
                self.cursor.execute("""
                    ALTER TABLE products 
                    ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES product_categories(id)
                """)
            except Exception as e:
                logging.warning(f"Columna category_id ya existe o error: {e}")
            
            self.conn.commit()
            logging.info("✅ Tablas complementarias creadas exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creando tablas complementarias: {e}")
            self.conn.rollback()
            return False
    
    def insert_sample_data(self):
        """Insertar datos de ejemplo para las nuevas tablas"""
        try:
            # Insertar métodos de pago
            payment_methods = [
                ("Efectivo", "Pago en efectivo al momento de la entrega"),
                ("Tarjeta de Crédito", "Pago con tarjeta de crédito"),
                ("Tarjeta de Débito", "Pago con tarjeta de débito"),
                ("Transferencia", "Transferencia bancaria"),
                ("PayPal", "Pago a través de PayPal")
            ]
            
            for name, description in payment_methods:
                self.cursor.execute("""
                    INSERT INTO payment_methods (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, description))
            
            # Insertar zonas de entrega
            delivery_zones = [
                ("Centro", "Zona centro de la ciudad", 30, 0.00),
                ("Norte", "Zona norte de la ciudad", 45, 5.00),
                ("Sur", "Zona sur de la ciudad", 45, 5.00),
                ("Este", "Zona este de la ciudad", 60, 8.00),
                ("Oeste", "Zona oeste de la ciudad", 60, 8.00)
            ]
            
            for name, description, time, fee in delivery_zones:
                self.cursor.execute("""
                    INSERT INTO delivery_zones (zone_name, description, estimated_delivery_time_minutes, delivery_fee)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (zone_name) DO NOTHING
                """, (name, description, time, fee))
            
            # Insertar categorías de productos
            categories = [
                ("Comida Rápida", "Hamburguesas, pizzas, tacos", None),
                ("Bebidas", "Refrescos, jugos, café", None),
                ("Postres", "Helados, pasteles, galletas", None),
                ("Hamburguesas", "Variedad de hamburguesas", 1),
                ("Pizzas", "Pizzas de diferentes sabores", 1),
                ("Refrescos", "Bebidas carbonatadas", 2),
                ("Café", "Café y bebidas calientes", 2)
            ]
            
            for name, description, parent_id in categories:
                self.cursor.execute("""
                    INSERT INTO product_categories (name, description, parent_category_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, description, parent_id))
            
            # Insertar configuración del sistema
            configs = [
                ("delivery_fee_base", "5.00", "Tarifa base de entrega"),
                ("min_order_amount", "10.00", "Monto mínimo para pedidos"),
                ("max_delivery_distance", "15", "Distancia máxima de entrega en km"),
                ("order_timeout_minutes", "30", "Tiempo de espera para confirmar pedido"),
                ("auto_assign_orders", "true", "Asignación automática de pedidos")
            ]
            
            for key, value, description in configs:
                self.cursor.execute("""
                    INSERT INTO system_config (config_key, config_value, description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (config_key) DO UPDATE SET
                        config_value = EXCLUDED.config_value,
                        updated_at = CURRENT_TIMESTAMP
                """, (key, value, description))
            
            self.conn.commit()
            logging.info("✅ Datos de ejemplo insertados exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error insertando datos de ejemplo: {e}")
            self.conn.rollback()
            return False
    
    def create_indexes(self):
        """Crear índices para mejorar el rendimiento"""
        try:
            # Índices para orders
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_delivery_agent_id ON orders(delivery_agent_id)")
            
            # Índices para order_events
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_events_order_id ON order_events(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_events_event_type ON order_events(event_type)")
            
            # Índices para whatsapp_messages
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_order_id ON whatsapp_messages(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_sender ON whatsapp_messages(sender)")
            
            # Índices para payment_transactions
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_transactions_order_id ON payment_transactions(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status)")
            
            # Índices para notifications
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_order_id ON notifications(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status)")
            
            # Índices para audit_logs
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)")
            
            self.conn.commit()
            logging.info("✅ Índices creados exitosamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creando índices: {e}")
            self.conn.rollback()
            return False

def main():
    """Función principal"""
    enhancer = DatabaseEnhancer(DATABASE_URL)
    
    if enhancer.connect():
        logging.info("🚀 Iniciando mejora de base de datos...")
        
        # Crear tablas complementarias
        if enhancer.create_enhanced_tables():
            # Insertar datos de ejemplo
            enhancer.insert_sample_data()
            
            # Crear índices
            enhancer.create_indexes()
            
            logging.info("🎉 Base de datos mejorada exitosamente!")
            logging.info("📊 Nuevas funcionalidades disponibles:")
            logging.info("   - Gestión de clientes")
            logging.info("   - Zonas de entrega")
            logging.info("   - Categorías de productos")
            logging.info("   - Sistema de pagos")
            logging.info("   - Calificaciones y reseñas")
            logging.info("   - Notificaciones")
            logging.info("   - Configuración del sistema")
            logging.info("   - Logs de auditoría")
            logging.info("   - Analytics y reportes")
        
        enhancer.disconnect()

if __name__ == "__main__":
    main() 