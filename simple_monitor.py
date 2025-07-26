#!/usr/bin/env python3
"""
Monitor de Pedidos Simplificado
Versión directa sin módulos complejos
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import hashlib

# Configuración
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks" # URL base sin parámetros
TASKS_URL_WITH_PARAMS = "https://admin.besmartdelivery.mx/tasks?status=REQUIRES_CONFIRMATION&status=PROCESSED&status=INPREPARATION&status=READYFORCOLLECTION&status=ONTHEWAY&status=ATLOCATION"
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "28ZwnPHQRC*H4BmfmEB-YHcC"

class SimpleMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.known_orders = set()
        self.setup_session()
    
    def setup_session(self):
        """Configurar sesión HTTP"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive'
        })
        self.session.timeout = 30
        print("✅ Sesión HTTP configurada")
    
    def login(self):
        """Iniciar sesión"""
        try:
            print(f"🔐 Intentando login con usuario: {ADMIN_USERNAME}")
            
            # Obtener página de login
            login_page = self.session.get(LOGIN_URL)
            login_page.raise_for_status()
            
            # Preparar datos de login
            login_data = {
                'uid': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
            
            # Intentar login
            login_response = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
            
            # Verificar si el login fue exitoso
            if 'admin' in login_response.url.lower() or 'dashboard' in login_response.text.lower():
                print("✅ Login exitoso")
                return True
            else:
                print("❌ Login falló")
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def get_orders_page(self):
        """Obtener página de órdenes y activar el botón Active orders"""
        try:
            print("📄 Obteniendo página de tareas...")
            
            # Headers para evitar caché
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # 1. Obtener página base de tareas
            import time
            timestamp = int(time.time())
            url_with_timestamp = f"{TASKS_URL}?_t={timestamp}"
            
            response = self.session.get(url_with_timestamp, headers=headers)
            response.raise_for_status()
            print("✅ Página base obtenida")
            
            # 2. Buscar el botón "Active orders"
            soup = BeautifulSoup(response.text, 'html.parser')
            active_orders_button = soup.find('div', class_='btn')
            
            if active_orders_button:
                active_orders_label = active_orders_button.find('span', class_='label')
                if active_orders_label and 'Active orders' in active_orders_label.get_text():
                    print("🎯 Botón Active orders encontrado, activando...")
                    
                    # Extraer el valor del botón para verificar
                    value_span = active_orders_button.find('span', class_='value')
                    if value_span:
                        active_count = value_span.get_text().strip()
                        print(f"📊 Botón Active orders tiene {active_count} órdenes")
                    
                    # 3. Simular clic en el botón usando la URL con parámetros
                    try:
                        print("🎯 Activando filtro de Active orders...")
                        
                        # Usar la URL con parámetros que simula el clic en el botón
                        active_timestamp = int(time.time())
                        active_url = f"{TASKS_URL_WITH_PARAMS}&_t={active_timestamp}"
                        
                        active_response = self.session.get(active_url, headers=headers)
                        active_response.raise_for_status()
                        
                        print("✅ Filtro Active orders activado")
                        return active_response.text
                        
                    except Exception as click_error:
                        print(f"⚠️ No se pudo activar el filtro: {click_error}")
                        # Continuar con la página original
                        return response.text
                else:
                    print("ℹ️ Botón encontrado pero no es Active orders")
            else:
                print("ℹ️ Botón Active orders no encontrado")
            
            # 4. Si no se pudo activar, intentar con la URL con parámetros directamente
            try:
                print("🔄 Intentando con URL con parámetros...")
                params_timestamp = int(time.time())
                params_url = f"{TASKS_URL_WITH_PARAMS}&_t={params_timestamp}"
                
                params_response = self.session.get(params_url, headers=headers)
                params_response.raise_for_status()
                
                print("✅ Página con parámetros obtenida")
                return params_response.text
                
            except Exception as params_error:
                print(f"⚠️ No se pudo obtener página con parámetros: {params_error}")
                return response.text
            
        except Exception as e:
            print(f"❌ Error obteniendo página: {e}")
            return None
    
    def extract_orders(self, html_content):
        """Extraer órdenes del HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Debug: Mostrar parte del HTML para verificar
            print(f"🔍 Analizando HTML de {len(html_content)} caracteres")
            
            # Buscar tabla de órdenes
            orders_table = soup.find('table', class_='responsive-table')
            if not orders_table:
                print("⚠️ No se encontró tabla de órdenes")
                # Debug: Buscar cualquier tabla
                all_tables = soup.find_all('table')
                print(f"🔍 Encontradas {len(all_tables)} tablas en total")
                for i, table in enumerate(all_tables):
                    print(f"   Tabla {i+1}: clases = {table.get('class', [])}")
                return []
            
            tbody = orders_table.find('tbody')
            if not tbody:
                print("⚠️ No se encontró tbody en la tabla")
                return []
            
            # Buscar filas de órdenes
            order_rows = tbody.find_all('tr', class_='orders-list-item')
            print(f"📋 Encontradas {len(order_rows)} filas de órdenes")
            
            new_orders = []
            
            for row in order_rows:
                order_data = self.parse_order_row(row)
                if order_data:
                    # Generar hash único
                    order_hash = hashlib.sha256(
                        f"{order_data.get('order_id', '')}{order_data.get('customer_name', '')}".encode()
                    ).hexdigest()
                    
                    if order_hash not in self.known_orders:
                        self.known_orders.add(order_hash)
                        new_orders.append(order_data)
                        print(f"🎯 Nueva orden detectada: {order_data.get('order_id', 'N/A')}")
            
            return new_orders
            
        except Exception as e:
            print(f"❌ Error extrayendo órdenes: {e}")
            return []
    
    def parse_order_row(self, row):
        """Parsear una fila de orden"""
        try:
            cells = row.find_all('td')
            if len(cells) < 10:
                return None
            
            order_data = {
                'timestamp': datetime.now().isoformat(),
                'status': 'Desconocido'
            }
            
            # Columna 1: ID de orden
            if len(cells) > 0:
                order_id_field = cells[0].find('div', class_='order-id-field')
                if order_id_field:
                    order_text = order_id_field.get_text(strip=True)
                    numbers = re.findall(r'\d+', order_text)
                    if numbers:
                        order_data['order_id'] = numbers[-1]
            
            # Columna 2: Restaurante
            if len(cells) > 1:
                vendor_field = cells[1].find('div', class_='vendor-field')
                if vendor_field:
                    vendor_link = vendor_field.find('a', class_='link')
                    if vendor_link:
                        order_data['restaurant'] = vendor_link.get_text(strip=True)
            
            # Columna 3: Cliente
            if len(cells) > 2:
                customer_field = cells[2].find('div', class_='customer-field')
                if customer_field:
                    customer_link = customer_field.find('a', class_='link')
                    if customer_link:
                        order_data['customer_name'] = customer_link.get_text(strip=True)
            
            # Columna 4: Zona
            if len(cells) > 3:
                zone_text = cells[3].get_text(strip=True)
                if zone_text:
                    order_data['delivery_address'] = zone_text
            
            # Columna 5: Total
            if len(cells) > 4:
                price_span = cells[4].find('span', class_='price')
                if price_span:
                    price_text = price_span.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+\.?\d*', price_text)
                    if numbers:
                        order_data['total_amount'] = numbers[0]
            
            # Columna 6: Hora de creación
            if len(cells) > 5:
                created_text = cells[5].get_text(strip=True)
                if created_text:
                    order_data['created_at'] = created_text
            
            # Estado basado en clases CSS
            order_classes = row.get('class', [])
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
            
            return order_data if order_data.get('order_id') else None
            
        except Exception as e:
            print(f"❌ Error parseando fila: {e}")
            return None
    
    def display_orders(self, orders):
        """Mostrar órdenes en consola"""
        if not orders:
            print("ℹ️ No hay nuevas órdenes")
            return
        
        print("\n" + "🚨 ¡NUEVAS ÓRDENES DETECTADAS! 🚨")
        print("="*80)
        print(f"{'ID':<8} {'Estado':<15} {'Restaurante':<25} {'Cliente':<20} {'Total':<10} {'Hora':<8}")
        print("-"*80)
        
        for order in orders:
            order_id = order.get('order_id', 'N/A')
            status = order.get('status', 'N/A')
            restaurant = order.get('restaurant', 'N/A')[:24]
            customer = order.get('customer_name', 'N/A')[:19]
            total = order.get('total_amount', 'N/A')
            created_at = order.get('created_at', 'N/A')
            
            print(f"{order_id:<8} {status:<15} {restaurant:<25} {customer:<20} {total:<10} {created_at:<8}")
        
        print("-"*80)
        print(f"📊 Total de nuevas órdenes: {len(orders)}")
        print("="*80 + "\n")
    
    def monitor_orders(self):
        """Función principal de monitoreo"""
        print("🎯 MONITOR DE ÓRDENES SIMPLIFICADO")
        print("="*50)
        
        if not self.login():
            print("❌ No se pudo iniciar sesión")
            return
        
        print("🔄 Iniciando monitoreo...")
        print("💡 Presiona Ctrl+C para detener")
        print("="*50)
        
        try:
            while True:
                html_content = self.get_orders_page()
                if html_content:
                    new_orders = self.extract_orders(html_content)
                    self.display_orders(new_orders)
                else:
                    print("❌ No se pudo obtener la página")
                
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Esperando 10 segundos...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoreo detenido por el usuario")
        except Exception as e:
            print(f"❌ Error en monitoreo: {e}")

def main():
    """Función principal"""
    monitor = SimpleMonitor()
    monitor.monitor_orders()

if __name__ == "__main__":
    main() 