"""
Parser de órdenes para monitores
Funcionalidades específicas para extraer y procesar órdenes
"""

import re
from datetime import datetime
from bs4 import BeautifulSoup
from .utils import OrderParser, BaseLogger

class OrderExtractor:
    """Extractor de órdenes con funcionalidades específicas"""
    
    def __init__(self, analytics=None):
        self.analytics = analytics
        self.parser = OrderParser()
    
    def find_order_containers(self, soup):
        """Encontrar contenedores de órdenes"""
        containers = []
        
        # Estrategia 1: Buscar el botón "Active orders" y extraer el valor
        active_orders_button = soup.find('div', class_='btn')
        if active_orders_button:
            active_orders_label = active_orders_button.find('span', class_='label')
            if active_orders_label and 'Active orders' in active_orders_label.get_text():
                value_span = active_orders_button.find('span', class_='value')
                if value_span:
                    active_count = value_span.get_text().strip()
                    BaseLogger.info(f"Botón Active orders encontrado con {active_count} órdenes")
        
        # Estrategia 2: Buscar tabla específica de órdenes
        orders_table = soup.find('table', class_='responsive-table')
        if orders_table:
            tbody = orders_table.find('tbody')
            if tbody:
                # Buscar filas con clase 'orders-list-item'
                order_rows = tbody.find_all('tr', class_='orders-list-item')
                containers.extend(order_rows)
                BaseLogger.info(f"Tabla de órdenes encontrada con {len(order_rows)} filas")
        
        # Estrategia 3: Buscar cualquier fila de tabla con datos de órdenes
        if not containers:
            tables = soup.find_all('table')
            for table in tables:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        # Verificar que sea una fila de orden (tiene celdas con datos)
                        cells = row.find_all('td')
                        if len(cells) >= 5:  # Mínimo 5 columnas para ser una orden
                            # Verificar que tenga datos de orden
                            row_text = row.get_text().lower()
                            if any(keyword in row_text for keyword in ['vendor', 'customer', 'price', 'total']):
                                containers.append(row)
        
        BaseLogger.detection(f"Encontrados {len(containers)} contenedores de órdenes")
        
        # Debug: Mostrar información de los contenedores encontrados
        if containers:
            BaseLogger.info(f"📋 Contenedores encontrados: {len(containers)}")
            for i, container in enumerate(containers[:3]):  # Mostrar solo los primeros 3
                container_text = container.get_text()[:100] + "..." if len(container.get_text()) > 100 else container.get_text()
                BaseLogger.info(f"   Contenedor {i+1}: {container_text}")
        else:
            BaseLogger.warning("⚠️ No se encontraron contenedores de órdenes")
        
        return containers
    
    def parse_order_container(self, container):
        """Parsear contenedor de orden"""
        try:
            order_data = {
                'timestamp': datetime.now().isoformat(),
                'raw_html': str(container)[:1000],  # Limitar tamaño
                'type': 'terminal_order'
            }
            
            # Extraer datos de la fila de tabla según la estructura específica
            cells = container.find_all('td')
            if cells and len(cells) >= 10:  # La tabla tiene 11 columnas
                # Columna 1: # (ID de orden)
                if len(cells) > 0:
                    order_id_cell = cells[0]
                    order_id_field = order_id_cell.find('div', class_='order-id-field')
                    if order_id_field:
                        # Extraer el número de orden (está después del checkbox)
                        order_text = order_id_field.get_text(strip=True)
                        # Buscar el número al final del texto
                        numbers = re.findall(r'\d+', order_text)
                        if numbers:
                            order_data['order_id'] = numbers[-1]  # Último número encontrado
                
                # Columna 2: Vendor (Restaurante)
                if len(cells) > 1:
                    vendor_cell = cells[1]
                    vendor_field = vendor_cell.find('div', class_='vendor-field')
                    if vendor_field:
                        vendor_link = vendor_field.find('a', class_='link')
                        if vendor_link:
                            order_data['restaurant'] = vendor_link.get_text(strip=True)
                
                # Columna 3: Customer (Cliente)
                if len(cells) > 2:
                    customer_cell = cells[2]
                    customer_field = customer_cell.find('div', class_='customer-field')
                    if customer_field:
                        customer_link = customer_field.find('a', class_='link')
                        if customer_link:
                            order_data['customer_name'] = customer_link.get_text(strip=True)
                
                # Columna 4: Zone (Zona/Dirección)
                if len(cells) > 3:
                    zone_cell = cells[3]
                    zone_text = zone_cell.get_text(strip=True)
                    if zone_text and zone_text != '':
                        order_data['delivery_address'] = zone_text
                
                # Columna 5: Total (Monto)
                if len(cells) > 4:
                    total_cell = cells[4]
                    price_span = total_cell.find('span', class_='price')
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        # Extraer solo el número
                        numbers = re.findall(r'[\d,]+\.?\d*', price_text)
                        if numbers:
                            order_data['total_amount'] = numbers[0]
                
                # Columna 6: Created at (Hora de creación)
                if len(cells) > 5:
                    created_cell = cells[5]
                    created_text = created_cell.get_text(strip=True)
                    if created_text:
                        order_data['created_at'] = created_text
                
                # Columna 7: CT (Cooking time)
                if len(cells) > 6:
                    ct_cell = cells[6]
                    ct_text = ct_cell.get_text(strip=True)
                    if ct_text:
                        order_data['cooking_time'] = ct_text
                
                # Columna 8: DT (Delivery time)
                if len(cells) > 7:
                    dt_cell = cells[7]
                    dt_text = dt_cell.get_text(strip=True)
                    if dt_text:
                        order_data['delivery_time'] = dt_text
                
                # Columna 9: Rider (Repartidor)
                if len(cells) > 8:
                    rider_cell = cells[8]
                    rider_text = rider_cell.get_text(strip=True)
                    if rider_text:
                        order_data['rider'] = rider_text
                
                # Estado de la orden (basado en las clases CSS)
                order_classes = container.get('class', [])
                if 'processed' in order_classes:
                    order_data['status'] = 'Procesado'
                elif 'inpreparation' in order_classes:
                    order_data['status'] = 'En Preparación'
                elif 'readyforcollection' in order_classes:
                    order_data['status'] = 'Listo para Recoger'
                elif 'ontheway' in order_classes:
                    order_data['status'] = 'En Camino'
                elif 'atlocation' in order_classes:
                    order_data['status'] = 'En Ubicación'
                else:
                    order_data['status'] = 'Desconocido'
            
            # Si no se encontraron datos en las celdas, usar métodos de fallback
            if not order_data.get('order_id'):
                order_id = self.parser.extract_order_id(container)
                if order_id:
                    order_data['order_id'] = order_id
            
            if not order_data.get('customer_name'):
                customer_name = self.parser.extract_customer_info(container)
                if customer_name:
                    order_data['customer_name'] = customer_name
            
            if not order_data.get('delivery_address'):
                address = self.parser.extract_address(container)
                if address:
                    order_data['delivery_address'] = address
            
            if not order_data.get('restaurant'):
                restaurant = self.parser.extract_restaurant(container)
                if restaurant:
                    order_data['restaurant'] = restaurant
            
            if not order_data.get('total_amount'):
                amount = self.parser.extract_amount(container)
                if amount:
                    order_data['total_amount'] = amount
            
            if not order_data.get('status'):
                status = self.parser.extract_status(container)
                if status:
                    order_data['status'] = status
            
            # Determinar prioridad
            priority = self.parser.determine_priority(order_data, self.analytics)
            order_data['priority'] = priority
            
            # Debug: Mostrar información de la orden parseada
            if order_data.get('order_id'):
                BaseLogger.success(f"✅ Orden parseada: ID={order_data.get('order_id')}, Cliente={order_data.get('customer_name', 'N/A')}, Total=${order_data.get('total_amount', 'N/A')}")
            else:
                BaseLogger.warning("⚠️ No se pudo extraer ID de orden del contenedor")
            
            return order_data if order_data.get('order_id') else None
            
        except Exception as e:
            BaseLogger.error(f"Error parseando contenedor: {e}")
            return None
    
    def extract_new_orders(self, html_content, known_hashes):
        """Extraer nuevas órdenes de la página HTML"""
        try:
            BaseLogger.detection("Extrayendo órdenes de la página...")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            new_orders = []
            current_time = datetime.now()
            
            # Buscar contenedores de órdenes
            order_containers = self.find_order_containers(soup)
            
            BaseLogger.detection(f"Encontrados {len(order_containers)} contenedores de órdenes")
            
            # Procesar cada contenedor
            for container in order_containers:
                order_data = self.parse_order_container(container)
                if order_data:
                    order_hash = self.parser.generate_order_hash(order_data)
                    
                    if order_hash not in known_hashes:
                        # Es una orden nueva
                        order_data['order_hash'] = order_hash
                        order_data['detected_at'] = current_time.isoformat()
                        order_data['source'] = 'terminal_monitor'
                        order_data['page'] = '/tasks'
                        
                        new_orders.append(order_data)
                        known_hashes.add(order_hash)
                        
                        # Agregar a analytics si está disponible
                        if self.analytics:
                            self.analytics.add_order(order_data)
                        
                        BaseLogger.notification(f"Nueva orden detectada: {order_data.get('order_id', 'N/A')}")
            
            return new_orders
            
        except Exception as e:
            BaseLogger.error(f"Error extrayendo órdenes: {e}")
            return []
    
    def validate_order_data(self, order_data):
        """Validar datos de la orden"""
        required_fields = ['order_id', 'customer_name', 'restaurant']
        
        for field in required_fields:
            if not order_data.get(field):
                return False
        
        return True
    
    def clean_order_data(self, order_data):
        """Limpiar y normalizar datos de la orden"""
        try:
            # Limpiar strings
            for key, value in order_data.items():
                if isinstance(value, str):
                    order_data[key] = value.strip()
            
            # Normalizar estado
            status = order_data.get('status', '').lower()
            if 'preparación' in status or 'preparation' in status:
                order_data['status'] = 'En Preparación'
            elif 'activo' in status or 'active' in status:
                order_data['status'] = 'Activo'
            elif 'pendiente' in status or 'pending' in status:
                order_data['status'] = 'Pendiente'
            
            # Normalizar prioridad
            priority = order_data.get('priority', 'normal').lower()
            if priority not in ['urgent', 'high', 'normal', 'low']:
                order_data['priority'] = 'normal'
            
            return order_data
            
        except Exception as e:
            BaseLogger.error(f"Error limpiando datos de orden: {e}")
            return order_data 