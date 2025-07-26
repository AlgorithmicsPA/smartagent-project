"""
Utilidades comunes para monitores de órdenes
Funciones y clases compartidas entre diferentes versiones de monitores
"""

import logging
import sys
import os
from datetime import datetime
from collections import defaultdict, deque
import hashlib
import re
import json
import time

class BaseLogger:
    """Logger base con funcionalidades comunes"""
    
    @staticmethod
    def log(message, level="INFO", emoji="ℹ️"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
    
    @staticmethod
    def info(message):
        BaseLogger.log(message, "INFO", "ℹ️")
    
    @staticmethod
    def success(message):
        BaseLogger.log(message, "SUCCESS", "✅")
    
    @staticmethod
    def warning(message):
        BaseLogger.log(message, "WARNING", "⚠️")
    
    @staticmethod
    def error(message):
        BaseLogger.log(message, "ERROR", "❌")
    
    @staticmethod
    def monitor(message):
        BaseLogger.log(message, "MONITOR", "🎯")
    
    @staticmethod
    def detection(message):
        BaseLogger.log(message, "DETECTION", "🔍")
    
    @staticmethod
    def notification(message):
        BaseLogger.log(message, "NOTIFICATION", "🔔")
    
    @staticmethod
    def performance(message):
        BaseLogger.log(message, "PERFORMANCE", "⚡")
    
    @staticmethod
    def analytics(message):
        BaseLogger.log(message, "ANALYTICS", "📊")

class OrderAnalytics:
    """Clase para análisis y estadísticas de órdenes"""
    
    def __init__(self):
        self.order_history = deque(maxlen=1000)
        self.restaurant_stats = defaultdict(int)
        self.customer_stats = defaultdict(int)
        self.time_stats = defaultdict(int)
        self.status_stats = defaultdict(int)
        self.performance_metrics = {
            'total_checks': 0,
            'total_orders': 0,
            'avg_response_time': 0,
            'peak_hours': [],
            'busy_restaurants': [],
            'frequent_customers': []
        }
    
    def add_order(self, order_data):
        """Agregar orden para análisis"""
        self.order_history.append(order_data)
        
        # Estadísticas por restaurante
        restaurant = order_data.get('restaurant', 'Unknown')
        self.restaurant_stats[restaurant] += 1
        
        # Estadísticas por cliente
        customer = order_data.get('customer_name', 'Unknown')
        self.customer_stats[customer] += 1
        
        # Estadísticas por hora
        hour = datetime.now().hour
        self.time_stats[hour] += 1
        
        # Estadísticas por estado
        status = order_data.get('status', 'Unknown')
        self.status_stats[status] += 1
        
        self.performance_metrics['total_orders'] += 1
    
    def get_analytics_report(self):
        """Generar reporte de análisis"""
        report = {
            'total_orders': self.performance_metrics['total_orders'],
            'top_restaurants': sorted(self.restaurant_stats.items(), key=lambda x: x[1], reverse=True)[:5],
            'top_customers': sorted(self.customer_stats.items(), key=lambda x: x[1], reverse=True)[:5],
            'peak_hours': sorted(self.time_stats.items(), key=lambda x: x[1], reverse=True)[:3],
            'status_distribution': dict(self.status_stats),
            'avg_orders_per_hour': sum(self.time_stats.values()) / max(len(self.time_stats), 1)
        }
        return report

class OrderParser:
    """Clase para parsear órdenes con funcionalidades comunes"""
    
    @staticmethod
    def generate_order_hash(order_data):
        """Generar hash único para la orden"""
        hash_string = f"{order_data.get('order_id', '')}{order_data.get('customer_name', '')}{order_data.get('delivery_address', '')}{order_data.get('timestamp', '')}"
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    @staticmethod
    def extract_order_id(container):
        """Extraer ID de orden"""
        # Estrategia 1: Selectores específicos
        selectors = [
            ".order-id-field",
            "div[class*='order-id']",
            "td[data-label='#'] div",
            "span[class*='order-id']",
            ".order-id",
            ".task-id"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Estrategia 2: Buscar en texto con regex
        text = container.get_text()
        patterns = [
            r'Task[:\s]*([A-Z0-9-]+)',
            r'Order[:\s]*([A-Z0-9-]+)',
            r'#([A-Z0-9-]+)',
            r'([A-Z]{2,3}-\d{4,})',
            r'ID[:\s]*([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_customer_info(container):
        """Extraer información del cliente"""
        selectors = [
            ".customer-field a",
            ".customer-field span",
            "span[class*='customer']",
            "span[class*='cliente']",
            "td[class*='customer']"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    @staticmethod
    def extract_address(container):
        """Extraer dirección de entrega"""
        selectors = [
            "td:nth-child(4) div",
            "span[class*='address']",
            "span[class*='direccion']",
            "td[class*='address']"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    @staticmethod
    def extract_restaurant(container):
        """Extraer información del restaurante"""
        selectors = [
            ".vendor-field a",
            ".vendor-field span",
            "span[class*='vendor']",
            "span[class*='restaurant']",
            "td[class*='vendor']"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    @staticmethod
    def extract_amount(container):
        """Extraer monto total"""
        selectors = [
            ".price",
            "span.price",
            "td .price",
            "span[class*='amount']",
            "span[class*='total']"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                amount_text = element.get_text(strip=True)
                numbers = re.findall(r'[\d,]+\.?\d*', amount_text)
                if numbers:
                    return numbers[0]
        
        return None
    
    @staticmethod
    def extract_status(container):
        """Extraer estado de la orden"""
        # Verificar clases del contenedor
        classes = container.get('class', [])
        for class_name in classes:
            if 'inpreparation' in class_name:
                return 'En Preparación'
            elif 'active' in class_name:
                return 'Activo'
            elif 'pending' in class_name:
                return 'Pendiente'
        
        # Buscar en elementos hijos
        selectors = [
            "span[class*='status']",
            "td[class*='status']",
            ".status-field"
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return 'Desconocido'
    
    @staticmethod
    def determine_priority(order_data, analytics=None):
        """Determinar prioridad de la orden"""
        priority_score = 0
        
        # Factor 1: Estado de la orden
        status = order_data.get('status', '').lower()
        if 'urgent' in status or 'urgente' in status:
            priority_score += 3
        elif 'high' in status or 'alta' in status:
            priority_score += 2
        elif 'normal' in status:
            priority_score += 1
        
        # Factor 2: Tiempo desde detección
        detected_at = order_data.get('detected_at')
        if detected_at:
            try:
                detected_time = datetime.fromisoformat(detected_at.replace('Z', '+00:00'))
                time_diff = (datetime.now() - detected_time).total_seconds()
                if time_diff > 300:  # Más de 5 minutos
                    priority_score += 2
                elif time_diff > 180:  # Más de 3 minutos
                    priority_score += 1
            except:
                pass
        
        # Factor 3: Cliente frecuente
        if analytics:
            customer = order_data.get('customer_name', '')
            if customer in analytics.customer_stats and analytics.customer_stats[customer] > 5:
                priority_score += 1
        
        # Determinar nivel de prioridad
        if priority_score >= 4:
            return 'urgent'
        elif priority_score >= 2:
            return 'high'
        elif priority_score >= 1:
            return 'normal'
        else:
            return 'low'

class NotificationManager:
    """Gestor de notificaciones"""
    
    @staticmethod
    def play_notification_sound():
        """Reproducir sonido de notificación"""
        try:
            # Usar beep del sistema
            import winsound
            winsound.Beep(1000, 500)  # Frecuencia 1000Hz, duración 500ms
        except:
            # Fallback: imprimir caracteres especiales
            print("\a")  # Bell character
    
    @staticmethod
    def display_orders_table(orders, monitor_type="TERMINAL"):
        """Mostrar tabla de órdenes"""
        print("\n" + "="*140)
        print(f"🎯 NUEVAS ÓRDENES DETECTADAS - MONITOR {monitor_type}")
        print("="*140)
        print(f"{'ID':<8} {'Estado':<15} {'Restaurante':<25} {'Cliente':<20} {'Zona':<25} {'Total':<10} {'Hora':<8} {'CT':<8} {'DT':<8} {'Rider':<12}")
        print("-"*140)
        
        for order_data in orders:
            order_id = order_data.get('order_id', 'N/A')
            status = order_data.get('status', 'N/A')
            restaurant = order_data.get('restaurant', 'N/A')
            if len(restaurant) > 24:
                restaurant = restaurant[:24] + "..."
            customer = order_data.get('customer_name', 'N/A')
            if len(customer) > 19:
                customer = customer[:19] + "..."
            zone = order_data.get('delivery_address', 'N/A')
            if len(zone) > 24:
                zone = zone[:24] + "..."
            total = order_data.get('total_amount', 'N/A')
            created_at = order_data.get('created_at', 'N/A')
            cooking_time = order_data.get('cooking_time', 'N/A')
            delivery_time = order_data.get('delivery_time', 'N/A')
            rider = order_data.get('rider', 'N/A')
            if len(rider) > 11:
                rider = rider[:11] + "..."
            
            print(f"{order_id:<8} {status:<15} {restaurant:<25} {customer:<20} {zone:<25} {total:<10} {created_at:<8} {cooking_time:<8} {delivery_time:<8} {rider:<12}")
        
        print("-"*140)
        print(f"📊 Nuevas órdenes detectadas: {len(orders)}")
        print("="*140 + "\n")

class DatabaseManager:
    """Gestor de base de datos"""
    
    def __init__(self, db_conn, db_cursor):
        self.db_conn = db_conn
        self.db_cursor = db_cursor
    
    def create_orders_table(self, table_name="terminal_orders"):
        """Crear tabla de órdenes"""
        try:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(50) UNIQUE,
                order_number VARCHAR(50),
                task_id VARCHAR(50),
                customer_name VARCHAR(255),
                delivery_address TEXT,
                restaurant VARCHAR(255),
                total_amount DECIMAL(10,2),
                status VARCHAR(100),
                priority VARCHAR(20) DEFAULT 'normal',
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                order_hash VARCHAR(64),
                source VARCHAR(50),
                page VARCHAR(100),
                raw_html TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analytics_data JSONB,
                performance_metrics JSONB
            );
            """
            
            self.db_cursor.execute(create_table_query)
            self.db_conn.commit()
            logging.info(f"✅ Tabla {table_name} creada/verificada")
            
        except Exception as e:
            logging.error(f"❌ Error creando tabla {table_name}: {e}")
    
    def save_order(self, order_data, table_name="terminal_orders", analytics=None, performance_metrics=None):
        """Guardar orden en base de datos"""
        try:
            insert_query = f"""
            INSERT INTO {table_name} (
                order_id, order_number, task_id, customer_name, delivery_address,
                restaurant, total_amount, status, priority, detected_at,
                order_hash, source, page, raw_html, analytics_data, performance_metrics
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                priority = EXCLUDED.priority,
                processed_at = CURRENT_TIMESTAMP,
                analytics_data = EXCLUDED.analytics_data,
                performance_metrics = EXCLUDED.performance_metrics
            """
            
            # Preparar datos
            analytics_data = json.dumps(analytics.get_analytics_report() if analytics else {})
            performance_data = json.dumps(performance_metrics or {})
            
            values = (
                order_data.get('order_id'),
                order_data.get('order_number'),
                order_data.get('task_id'),
                order_data.get('customer_name'),
                order_data.get('delivery_address'),
                order_data.get('restaurant'),
                order_data.get('total_amount'),
                order_data.get('status'),
                order_data.get('priority'),
                order_data.get('detected_at'),
                order_data.get('order_hash'),
                order_data.get('source'),
                order_data.get('page'),
                order_data.get('raw_html'),
                analytics_data,
                performance_data
            )
            
            self.db_cursor.execute(insert_query, values)
            self.db_conn.commit()
            
            BaseLogger.success(f"Orden guardada en BD: {order_data.get('order_id', 'N/A')}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error guardando orden en BD: {e}")
            BaseLogger.error(f"Error guardando orden en BD: {e}")
            return False 