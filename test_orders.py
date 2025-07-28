#!/usr/bin/env python3
"""
Script de prueba para el sistema de pedidos
Demuestra las funcionalidades de gestión de pedidos, repartidores y eventos
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
import random

# Configuración de la base de datos
DATABASE_URL = "postgresql://***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***/***DB_OCULTA***?sslmode=require&channel_binding=require"

class OrderSystemTest:
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
    
    def test_delivery_agents(self):
        """Probar inserción de repartidores"""
        print("\n🚚 PROBANDO SISTEMA DE REPARTIDORES:")
        print("-" * 50)
        
        # Insertar repartidores de prueba
        agents_data = [
            ("Juan Pérez", "+52 55 1234 5678", "Centro Histórico, CDMX"),
            ("María García", "+52 55 9876 5432", "Polanco, CDMX"),
            ("Carlos López", "+52 55 5555 1234", "Condesa, CDMX"),
            ("Ana Martínez", "+52 55 7777 8888", "Roma Norte, CDMX"),
            ("Roberto Silva", "+52 55 1111 2222", "Coyoacán, CDMX")
        ]
        
        agent_ids = []
        for name, contact, location in agents_data:
            try:
                self.cursor.execute("""
                    INSERT INTO delivery_agents (name, contact_info, current_location)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (name, contact, location))
                
                agent_id = self.cursor.fetchone()['id']
                agent_ids.append(agent_id)
                print(f"✅ Repartidor creado: {name} (ID: {agent_id})")
                
            except Exception as e:
                print(f"⚠️ Repartidor ya existe: {name}")
        
        self.conn.commit()
        return agent_ids
    
    def test_orders(self, agent_ids):
        """Probar inserción de pedidos"""
        print("\n📦 PROBANDO SISTEMA DE PEDIDOS:")
        print("-" * 50)
        
        # Datos de pedidos de prueba
        orders_data = [
            {
                "order_number": "ORD-2024-001",
                "pickup_address": "Av. Insurgentes Sur 123, Condesa",
                "delivery_address": "Av. Tamaulipas 45, Condesa",
                "distance_km": 2.5,
                "product_type": "Comida",
                "priority_level": "high",
                "agent_id": agent_ids[0] if agent_ids else None
            },
            {
                "order_number": "ORD-2024-002",
                "pickup_address": "Av. Presidente Masaryk 456, Polanco",
                "delivery_address": "Av. Ejército Nacional 789, Polanco",
                "distance_km": 1.8,
                "product_type": "Documentos",
                "priority_level": "normal",
                "agent_id": agent_ids[1] if len(agent_ids) > 1 else None
            },
            {
                "order_number": "ORD-2024-003",
                "pickup_address": "Av. Álvaro Obregón 321, Roma Norte",
                "delivery_address": "Av. Yucatán 654, Roma Norte",
                "distance_km": 3.2,
                "product_type": "Flores",
                "priority_level": "high",
                "agent_id": agent_ids[2] if len(agent_ids) > 2 else None
            },
            {
                "order_number": "ORD-2024-004",
                "pickup_address": "Av. Universidad 987, Coyoacán",
                "delivery_address": "Av. Miguel Ángel de Quevedo 147, Coyoacán",
                "distance_km": 4.1,
                "product_type": "Electrónicos",
                "priority_level": "normal",
                "agent_id": agent_ids[3] if len(agent_ids) > 3 else None
            },
            {
                "order_number": "ORD-2024-005",
                "pickup_address": "Av. Reforma 258, Centro",
                "delivery_address": "Av. Juárez 369, Centro",
                "distance_km": 1.5,
                "product_type": "Ropa",
                "priority_level": "low",
                "agent_id": agent_ids[4] if len(agent_ids) > 4 else None
            }
        ]
        
        order_ids = []
        for order_data in orders_data:
            try:
                self.cursor.execute("""
                    INSERT INTO orders (order_number, status, pickup_address, delivery_address,
                                      distance_km, product_type, priority_level, delivery_agent_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (order_data["order_number"], "pending", order_data["pickup_address"],
                      order_data["delivery_address"], order_data["distance_km"],
                      order_data["product_type"], order_data["priority_level"],
                      order_data["agent_id"]))
                
                order_id = self.cursor.fetchone()['id']
                order_ids.append(order_id)
                print(f"✅ Pedido creado: {order_data['order_number']} (ID: {order_id})")
                
            except Exception as e:
                print(f"⚠️ Pedido ya existe: {order_data['order_number']}")
        
        self.conn.commit()
        return order_ids
    
    def test_order_events(self, order_ids):
        """Probar inserción de eventos de pedidos"""
        print("\n📊 PROBANDO EVENTOS DE PEDIDOS:")
        print("-" * 50)
        
        event_types = ["click", "status_change", "ocr_text", "button_detected", "location_update"]
        
        for order_id in order_ids:
            # Crear varios eventos para cada pedido
            for i in range(random.randint(3, 8)):
                event_type = random.choice(event_types)
                coordinates = f"x:{random.randint(100, 1920)},y:{random.randint(100, 1080)}"
                raw_data = {
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": "SmartAgent/1.0",
                    "session_id": f"session_{order_id}_{i}",
                    "additional_info": f"Evento {i+1} para pedido {order_id}"
                }
                
                try:
                    self.cursor.execute("""
                        INSERT INTO order_events (order_id, event_type, screen_coordinates, raw_data)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, event_type, coordinates, json.dumps(raw_data)))
                    
                    print(f"✅ Evento creado: {event_type} para pedido {order_id}")
                    
                except Exception as e:
                    print(f"❌ Error creando evento: {e}")
        
        self.conn.commit()
    
    def test_whatsapp_messages(self, order_ids):
        """Probar inserción de mensajes de WhatsApp"""
        print("\n💬 PROBANDO MENSAJES DE WHATSAPP:")
        print("-" * 50)
        
        senders = ["cliente", "repartidor", "sistema"]
        sample_messages = [
            "Hola, ¿cuándo llegará mi pedido?",
            "Pedido en camino, llegará en 15 minutos",
            "Pedido entregado exitosamente",
            "¿Puedo cambiar la dirección de entrega?",
            "Confirmo recepción del pedido",
            "Problema con el pedido, necesito ayuda",
            "Pedido cancelado por el cliente",
            "Reprogramando entrega para mañana"
        ]
        
        for order_id in order_ids:
            # Crear varios mensajes para cada pedido
            for i in range(random.randint(2, 5)):
                sender = random.choice(senders)
                message = random.choice(sample_messages)
                xpath = f"//div[@class='message'][{i+1}]"
                raw_html = f"<div class='message'><span class='sender'>{sender}</span><p>{message}</p></div>"
                
                try:
                    self.cursor.execute("""
                        INSERT INTO whatsapp_messages (order_id, sender, message, xpath_used, raw_html)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, sender, message, xpath, raw_html))
                    
                    print(f"✅ Mensaje creado: {sender} para pedido {order_id}")
                    
                except Exception as e:
                    print(f"❌ Error creando mensaje: {e}")
        
        self.conn.commit()
    
    def test_detected_buttons(self, order_ids):
        """Probar inserción de botones detectados"""
        print("\n🔘 PROBANDO BOTONES DETECTADOS:")
        print("-" * 50)
        
        button_texts = ["Confirmar", "Cancelar", "Aceptar", "Rechazar", "Editar", "Eliminar", "Guardar", "Enviar"]
        
        for order_id in order_ids:
            # Crear varios botones detectados para cada pedido
            for i in range(random.randint(2, 6)):
                button_text = random.choice(button_texts)
                xpath = f"//button[contains(text(), '{button_text}')]"
                position = f"x:{random.randint(100, 1920)},y:{random.randint(100, 1080)}"
                confidence = round(random.uniform(0.7, 0.99), 2)
                
                try:
                    self.cursor.execute("""
                        INSERT INTO detected_buttons (order_id, button_text, xpath, position, confidence)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, button_text, xpath, position, confidence))
                    
                    print(f"✅ Botón detectado: {button_text} (confianza: {confidence}) para pedido {order_id}")
                    
                except Exception as e:
                    print(f"❌ Error creando botón detectado: {e}")
        
        self.conn.commit()
    
    def show_statistics(self):
        """Mostrar estadísticas del sistema"""
        print("\n📊 ESTADÍSTICAS DEL SISTEMA:")
        print("-" * 50)
        
        try:
            # Estadísticas generales
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_orders,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders
                FROM orders
            """)
            
            order_stats = self.cursor.fetchone()
            print(f"📦 Pedidos totales: {order_stats['total_orders']}")
            print(f"⏳ Pendientes: {order_stats['pending_orders']}")
            print(f"🚚 En progreso: {order_stats['in_progress_orders']}")
            print(f"✅ Entregados: {order_stats['delivered_orders']}")
            
            # Repartidores
            self.cursor.execute("SELECT COUNT(*) as total_agents FROM delivery_agents")
            agent_count = self.cursor.fetchone()['total_agents']
            print(f"🚚 Repartidores: {agent_count}")
            
            # Eventos
            self.cursor.execute("SELECT COUNT(*) as total_events FROM order_events")
            event_count = self.cursor.fetchone()['total_events']
            print(f"📊 Eventos: {event_count}")
            
            # Mensajes WhatsApp
            self.cursor.execute("SELECT COUNT(*) as total_messages FROM whatsapp_messages")
            message_count = self.cursor.fetchone()['total_messages']
            print(f"💬 Mensajes WhatsApp: {message_count}")
            
            # Botones detectados
            self.cursor.execute("SELECT COUNT(*) as total_buttons FROM detected_buttons")
            button_count = self.cursor.fetchone()['total_buttons']
            print(f"🔘 Botones detectados: {button_count}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def show_sample_data(self):
        """Mostrar datos de ejemplo"""
        print("\n📋 DATOS DE EJEMPLO:")
        print("-" * 50)
        
        try:
            # Mostrar pedidos recientes
            print("📦 ÚLTIMOS PEDIDOS:")
            self.cursor.execute("""
                SELECT o.order_number, o.status, o.product_type, da.name as agent_name
                FROM orders o
                LEFT JOIN delivery_agents da ON o.delivery_agent_id = da.id
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            
            orders = self.cursor.fetchall()
            for order in orders:
                print(f"  {order['order_number']} - {order['status']} - {order['product_type']} - {order['agent_name'] or 'Sin asignar'}")
            
            # Mostrar eventos recientes
            print("\n📊 ÚLTIMOS EVENTOS:")
            self.cursor.execute("""
                SELECT oe.event_type, o.order_number, oe.event_timestamp
                FROM order_events oe
                JOIN orders o ON oe.order_id = o.id
                ORDER BY oe.event_timestamp DESC
                LIMIT 5
            """)
            
            events = self.cursor.fetchall()
            for event in events:
                print(f"  {event['event_type']} - {event['order_number']} - {event['event_timestamp']}")
            
            # Mostrar mensajes recientes
            print("\n💬 ÚLTIMOS MENSAJES:")
            self.cursor.execute("""
                SELECT wm.sender, wm.message, o.order_number
                FROM whatsapp_messages wm
                JOIN orders o ON wm.order_id = o.id
                ORDER BY wm.received_at DESC
                LIMIT 5
            """)
            
            messages = self.cursor.fetchall()
            for message in messages:
                print(f"  {message['sender']}: {message['message'][:50]}... - {message['order_number']}")
            
        except Exception as e:
            print(f"❌ Error mostrando datos de ejemplo: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("    SISTEMA DE PEDIDOS - PRUEBAS")
    print("=" * 60)
    
    test_system = OrderSystemTest(DATABASE_URL)
    
    if not test_system.connect():
        return
    
    try:
        # Ejecutar todas las pruebas
        agent_ids = test_system.test_delivery_agents()
        order_ids = test_system.test_orders(agent_ids)
        test_system.test_order_events(order_ids)
        test_system.test_whatsapp_messages(order_ids)
        test_system.test_detected_buttons(order_ids)
        
        # Mostrar resultados
        test_system.show_statistics()
        test_system.show_sample_data()
        
        print("\n✅ Todas las pruebas completadas exitosamente")
        print("\n📝 Próximos pasos:")
        print("1. Usar consultar_db.py para ver más detalles")
        print("2. Integrar con SmartAgent para automatización")
        print("3. Crear interfaz web para gestión de pedidos")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
    finally:
        test_system.disconnect()

if __name__ == "__main__":
    main() 