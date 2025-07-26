#!/usr/bin/env python3
"""
Monitor de Pedidos en Tiempo Real - SmartAgent
Escucha continuamente nuevos pedidos entrantes sin extraer toda la información
"""

import sys
import os
from pathlib import Path
import time
import json
import logging
from datetime import datetime, timedelta
import threading
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import random

# Cargar variables de entorno
load_dotenv(project_root / "config" / ".env")

# Configuración
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "federico")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "28ZwnPHQRC*H4BmfmEB-YHcC")
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración del monitor
MONITOR_CONFIG = {
    "check_interval": 30,  # Segundos entre verificaciones
    "order_timeout": 300,  # Segundos para considerar un pedido como "nuevo"
    "max_retries": 3,      # Máximo de reintentos en caso de error
    "notification_sound": True,  # Sonido de notificación
    "log_level": "INFO"
}

# Configurar logging para consola con formato más visible
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, MONITOR_CONFIG["log_level"]),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/order_monitor.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Función para logs de consola más visibles
def console_log(message, level="INFO"):
    """Log más visible para la consola"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if level == "INFO":
        print(f"[{timestamp}] ℹ️  {message}")
    elif level == "SUCCESS":
        print(f"[{timestamp}] ✅ {message}")
    elif level == "WARNING":
        print(f"[{timestamp}] ⚠️  {message}")
    elif level == "ERROR":
        print(f"[{timestamp}] ❌ {message}")
    elif level == "MONITOR":
        print(f"[{timestamp}] 🎯 {message}")
    elif level == "DETECTION":
        print(f"[{timestamp}] 🔍 {message}")
    elif level == "NOTIFICATION":
        print(f"[{timestamp}] 🔔 {message}")

class OrderMonitor:
    def __init__(self):
        self.driver = None
        self.db_conn = None
        self.db_cursor = None
        self.is_running = False
        self.last_check_time = None
        self.known_orders = set()
        self.order_stats = defaultdict(int)
        self.setup_database()
        
    def setup_database(self):
        """Configurar conexión a la base de datos"""
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            logging.info("✅ Conexión a base de datos establecida")
            console_log("Conexión a base de datos establecida", "SUCCESS")
        except Exception as e:
            logging.error(f"❌ Error conectando a la base de datos: {e}")
            console_log(f"Error conectando a la base de datos: {e}", "ERROR")
            sys.exit(1)
    
    def setup_driver(self):
        """Configurar ChromeDriver para monitoreo"""
        try:
            console_log("Configurando ChromeDriver...", "INFO")
            chrome_path = ChromeDriverManager().install()
            service = Service(chrome_path)
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logging.info("✅ ChromeDriver configurado para monitoreo")
            console_log("ChromeDriver configurado para monitoreo", "SUCCESS")
            return True
        except Exception as e:
            logging.error(f"❌ Error configurando ChromeDriver: {e}")
            console_log(f"Error configurando ChromeDriver: {e}", "ERROR")
            return False
    
    def login(self):
        """Iniciar sesión en el panel de administración"""
        try:
            logging.info(f"🔐 Iniciando sesión con usuario: {ADMIN_USERNAME}")
            console_log(f"Iniciando sesión con usuario: {ADMIN_USERNAME}", "INFO")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            
            # Buscar elementos de login
            username_field = self.driver.find_element(By.NAME, "uid")
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Estrategias para botón de login
            login_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[@class='button login main']"),
                (By.CSS_SELECTOR, "button.button.login.main"),
                (By.XPATH, "//button[text()='Login']")
            ]
            
            login_button = None
            for by, selector in login_selectors:
                try:
                    login_button = self.driver.find_element(by, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                logging.error("❌ No se pudo encontrar el botón de login")
                console_log("No se pudo encontrar el botón de login", "ERROR")
                return False
            
            # Realizar login
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            time.sleep(1)
            
            login_button.click()
            time.sleep(5)
            
            logging.info("✅ Login exitoso")
            console_log("Login exitoso", "SUCCESS")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error durante el login: {e}")
            console_log(f"Error durante el login: {e}", "ERROR")
            return False
    
    def find_orders_page(self):
        """Navegar a la página específica de active_orders en /tasks"""
        try:
            # Navegar directamente a la página /tasks
            task_url = LOGIN_URL.rstrip('/') + '/tasks'
            logging.info(f"🎯 Navegando a página específica: {task_url}")
            console_log(f"Navegando a página específica: {task_url}", "MONITOR")
            
            self.driver.get(task_url)
            time.sleep(5)
            
            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            if '/tasks' in current_url:
                logging.info(f"✅ Navegado exitosamente a página /tasks: {current_url}")
                console_log(f"Navegado exitosamente a página /tasks: {current_url}", "SUCCESS")
                
                # Buscar y hacer clic en el botón "Active orders"
                active_orders_button_selectors = [
                    "//div[contains(@class, 'btn')]//span[contains(@class, 'label') and contains(text(), 'Active orders')]",
                    "//div[contains(@class, 'btn')]//span[contains(text(), 'Active orders')]",
                    "//span[contains(@class, 'label') and contains(text(), 'Active orders')]",
                    "//span[contains(text(), 'Active orders')]",
                    "//div[contains(@class, 'btn')]//span[contains(text(), 'Active')]",
                    "//div[contains(@class, 'btn')]//span[contains(text(), 'orders')]"
                ]
                
                active_orders_button_clicked = False
                for selector in active_orders_button_selectors:
                    try:
                        active_orders_button = self.driver.find_element(By.XPATH, selector)
                        # Hacer clic en el botón
                        active_orders_button.click()
                        time.sleep(3)  # Esperar a que se despliegue la tabla
                        logging.info(f"✅ Botón Active orders encontrado y clickeado: {selector}")
                        console_log(f"Botón Active orders encontrado y clickeado: {selector}", "SUCCESS")
                        active_orders_button_clicked = True
                        break
                    except NoSuchElementException:
                        continue
                
                if not active_orders_button_clicked:
                    logging.warning("⚠️ No se pudo encontrar el botón Active orders")
                    console_log("No se pudo encontrar el botón Active orders", "WARNING")
                
                # Buscar elementos específicos de active_orders después del clic
                active_orders_selectors = [
                    "//div[contains(@class, 'active_orders')]",
                    "//div[contains(@id, 'active_orders')]",
                    "//section[contains(@class, 'active_orders')]",
                    "//div[contains(text(), 'Active Orders')]",
                    "//div[contains(text(), 'Pedidos Activos')]",
                    "//div[contains(text(), 'Tareas Activas')]",
                    "//table[contains(@class, 'active_orders')]",
                    "//ul[contains(@class, 'active_orders')]"
                ]
                
                for selector in active_orders_selectors:
                    try:
                        active_orders_element = self.driver.find_element(By.XPATH, selector)
                        logging.info(f"✅ Elemento active_orders encontrado: {selector}")
                        console_log(f"Elemento active_orders encontrado: {selector}", "SUCCESS")
                        return True
                    except NoSuchElementException:
                        continue
                
                # Si no se encuentra específicamente, continuar con la página actual
                logging.info("✅ En página /tasks, continuando con monitoreo")
                console_log("En página /tasks, continuando con monitoreo", "SUCCESS")
                return True
            else:
                logging.warning(f"⚠️ No se pudo navegar a /tasks, URL actual: {current_url}")
                console_log(f"No se pudo navegar a /tasks, URL actual: {current_url}", "WARNING")
                return False
            
        except Exception as e:
            logging.error(f"❌ Error navegando a página /tasks: {e}")
            return False
    
    def extract_new_orders(self):
        """Extraer nuevos active_orders de la página /tasks"""
        try:
            console_log("Extrayendo active_orders de la página /tasks...", "DETECTION")
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            new_orders = []
            current_time = datetime.now()
            
            # Buscar específicamente elementos de active_orders
            active_orders_containers = []
            
            # Estrategias específicas para active_orders basadas en la estructura real
            active_orders_selectors = [
                # Selectores específicos para la estructura de órdenes en tabla desplegada
                "tr.orders-list-item",
                "tr[class*='orders-list-item']",
                "tr[class*='inpreparation']",
                "tbody tr",
                "table tbody tr",
                # Selectores para tablas desplegadas
                "div[class*='active_orders'] tbody tr",
                "div[class*='active_orders'] table tr",
                "section[class*='active_orders'] tbody tr",
                "section[class*='active_orders'] table tr",
                # Selectores genéricos como respaldo
                "div[class*='active_orders']",
                "div[id*='active_orders']",
                "section[class*='active_orders']",
                "table[class*='active_orders']",
                "ul[class*='active_orders']",
                "div[class*='task']",
                "div[class*='active']",
                "tr[class*='active']",
                "li[class*='active']",
                ".active-orders",
                ".active_orders",
                ".task-item",
                ".active-item"
            ]
            
            # Buscar contenedores de active_orders
            for selector in active_orders_selectors:
                containers = soup.select(selector)
                active_orders_containers.extend(containers)
            
            # Si no se encuentran contenedores específicos, buscar en toda la página
            if not active_orders_containers:
                logging.info("🔍 No se encontraron contenedores específicos de active_orders, buscando en toda la página")
                console_log("No se encontraron contenedores específicos de active_orders, buscando en toda la página", "DETECTION")
                
                # Buscar específicamente en tablas con órdenes (incluyendo tablas desplegadas)
                tables = soup.find_all('table')
                for table in tables:
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        for row in rows:
                            # Verificar si es una fila de orden
                            if 'orders-list-item' in row.get('class', []) or 'inpreparation' in row.get('class', []):
                                active_orders_containers.append(row)
                
                # Buscar también en divs que puedan contener tablas desplegadas
                active_orders_divs = soup.find_all('div', class_=lambda x: x and 'active_orders' in x)
                for div in active_orders_divs:
                    # Buscar tablas dentro del div
                    tables_in_div = div.find_all('table')
                    for table in tables_in_div:
                        tbody = table.find('tbody')
                        if tbody:
                            rows = tbody.find_all('tr')
                            for row in rows:
                                if 'orders-list-item' in row.get('class', []) or 'inpreparation' in row.get('class', []):
                                    active_orders_containers.append(row)
                
                # Si aún no se encuentran, buscar elementos que contengan "order"
                if not active_orders_containers:
                    all_elements = soup.find_all(['div', 'tr', 'li', 'section'])
                    for element in all_elements:
                        element_text = element.get_text().lower()
                        if 'order' in element_text or 'preparation' in element_text:
                            active_orders_containers.append(element)
            
            logging.info(f"📊 Encontrados {len(active_orders_containers)} contenedores de active_orders")
            console_log(f"Encontrados {len(active_orders_containers)} contenedores de active_orders", "DETECTION")
            
            # Procesar cada contenedor de active_orders
            new_orders_found = []
            existing_orders = []
            
            for container in active_orders_containers:
                order_data = self.parse_active_order_container(container)
                if order_data:
                    order_id = order_data.get('order_id') or order_data.get('order_number') or order_data.get('task_id')
                    
                    if order_id and order_id not in self.known_orders:
                        # Es una orden nueva
                        new_orders_found.append(order_data)
                    else:
                        # Es una orden existente
                        existing_orders.append(order_data)
            
            # Mostrar tabla solo si hay órdenes nuevas
            if new_orders_found:
                print("\n" + "="*100)
                print("🎯 NUEVAS ÓRDENES DETECTADAS")
                print("="*100)
                print(f"{'ID':<5} {'Estado':<15} {'Restaurante':<25} {'Cliente':<20} {'Dirección':<25} {'Precio':<12} {'Hora':<8}")
                print("-"*100)
                
                for order_data in new_orders_found:
                    # Imprimir información de la orden en formato tabla
                    order_id = order_data.get('order_id', 'N/A')
                    status = order_data.get('status', 'N/A')
                    restaurant = order_data.get('restaurant', 'N/A')
                    customer = order_data.get('customer_name', 'N/A')
                    address = order_data.get('delivery_address', 'N/A')
                    if len(address) > 24:
                        address = address[:24] + "..."
                    price = order_data.get('total_amount', 'N/A')
                    time = order_data.get('time', 'N/A')
                    
                    print(f"{order_id:<5} {status:<15} {restaurant:<25} {customer:<20} {address:<25} {price:<12} {time:<8}")
                
                print("-"*100)
                print(f"📊 Nuevas órdenes detectadas: {len(new_orders_found)}")
                print("="*100 + "\n")
            
                        # Procesar solo las órdenes nuevas
            for order_data in new_orders_found:
                order_id = order_data.get('order_id') or order_data.get('order_number') or order_data.get('task_id')
                if order_id:
                    # Verificar si es realmente nuevo (últimos 5 minutos)
                    order_time = order_data.get('timestamp', current_time)
                    if isinstance(order_time, str):
                        try:
                            order_time = datetime.fromisoformat(order_time.replace('Z', '+00:00'))
                        except:
                            order_time = current_time
                    
                    time_diff = (current_time - order_time).total_seconds()
                    if time_diff <= MONITOR_CONFIG["order_timeout"]:
                        order_data['detected_at'] = current_time.isoformat()
                        order_data['source'] = 'active_orders'
                        order_data['page'] = '/tasks'
                        new_orders.append(order_data)
                        self.known_orders.add(order_id)
                        self.order_stats['new_orders'] += 1
                        logging.info(f"🎯 Nuevo active_order detectado: {order_id}")
                        console_log(f"Nuevo active_order detectado: {order_id}", "NOTIFICATION")
                        
                        # Mostrar notificación de nueva orden
                        self.display_order_notification(order_data)
                        self.save_order_to_database(order_data)
                        self.play_notification_sound()
            
            # Mostrar resumen de monitoreo
            if new_orders_found:
                console_log(f"Procesadas {len(new_orders_found)} nuevas órdenes", "SUCCESS")
            elif existing_orders:
                console_log(f"Monitoreando {len(existing_orders)} órdenes existentes", "INFO")
            else:
                console_log("No se encontraron órdenes activas", "INFO")
            
            return new_orders
            
        except Exception as e:
            logging.error(f"❌ Error extrayendo active_orders: {e}")
            console_log(f"Error extrayendo active_orders: {e}", "ERROR")
            return []
    
    def parse_active_order_container(self, container):
        """Parsear un contenedor de active_order para extraer información"""
        try:
            order_data = {
                'timestamp': datetime.now().isoformat(),
                'raw_html': str(container),
                'type': 'active_order'
            }
            
            # Buscar ID de orden basado en la estructura real
            order_id_selectors = [
                ".order-id-field",
                "div[class*='order-id']",
                "td[data-label='#'] .order-id-field",
                "td[data-label='#'] div",
                "span[class*='order-id']",
                "td[class*='order-id']",
                ".order-id",
                ".active-id"
            ]
            
            for selector in order_id_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['order_id'] = element.get_text(strip=True)
                    break
            
            # Buscar número de pedido (usar el mismo ID de orden)
            order_number_selectors = [
                ".order-id-field",
                "div[class*='order-id']",
                "td[data-label='#'] .order-id-field",
                "span[class*='order-number']",
                "td[class*='order-number']",
                ".order-number"
            ]
            
            for selector in order_number_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['order_number'] = element.get_text(strip=True)
                    break
            
            # Si no se encuentra con selectores específicos, buscar en el texto
            if 'order_number' not in order_data and 'task_id' not in order_data:
                text = container.get_text()
                # Buscar patrones de números de tareas/pedidos
                import re
                patterns = [
                    r'Task[:\s]*([A-Z0-9-]+)',
                    r'Tarea[:\s]*([A-Z0-9-]+)',
                    r'Order[:\s]*([A-Z0-9-]+)',
                    r'Pedido[:\s]*([A-Z0-9-]+)',
                    r'#([A-Z0-9-]+)',
                    r'([A-Z]{2,3}-\d{4,})',
                    r'ID[:\s]*([A-Z0-9-]+)',
                    r'Active[:\s]*([A-Z0-9-]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        if 'task_id' not in order_data:
                            order_data['task_id'] = match.group(1)
                        if 'order_number' not in order_data:
                            order_data['order_number'] = match.group(1)
                        break
            
            # Buscar información del cliente basado en la estructura real
            customer_selectors = [
                ".customer-field a .link",
                ".customer-field span.link",
                "td .customer-field a",
                "td .customer-field span",
                "span[class*='customer']",
                "span[class*='cliente']",
                "span[class*='user']",
                "td[class*='customer']",
                "td[class*='cliente']",
                "td[class*='user']"
            ]
            
            for selector in customer_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['customer_name'] = element.get_text(strip=True)
                    break
            
            # Buscar dirección de entrega (tercera columna en la estructura real)
            address_selectors = [
                "td:nth-child(4) div",  # Tercera columna con dirección
                "td:nth-child(4) .cell div",
                "span[class*='address']",
                "span[class*='direccion']",
                "span[class*='location']",
                "td[class*='address']",
                "td[class*='direccion']",
                "td[class*='location']"
            ]
            
            for selector in address_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['delivery_address'] = element.get_text(strip=True)
                    break
            
            # Buscar estado de la orden basado en la estructura real
            status_selectors = [
                "tr[class*='inpreparation']",  # Estado en la clase del tr
                "tr[class*='orders-list-item']",  # Clase que indica orden activa
                ".purchase-status-field",
                "td[class*='status']",
                "span[class*='status']",
                "span[class*='estado']",
                "span[class*='state']",
                "td[class*='estado']",
                "td[class*='state']"
            ]
            
            for selector in status_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['status'] = element.get_text(strip=True)
                    break
            
            # Buscar monto total basado en la estructura real
            amount_selectors = [
                ".price",
                "span.price",
                "td .price",
                "td:nth-child(5) .price",  # Quinta columna con precio
                "td:nth-child(5) span",
                "span[class*='amount']",
                "span[class*='total']",
                "span[class*='monto']",
                "span[class*='price']",
                "td[class*='amount']",
                "td[class*='total']",
                "td[class*='monto']",
                "td[class*='price']"
            ]
            
            for selector in amount_selectors:
                element = container.select_one(selector)
                if element:
                    amount_text = element.get_text(strip=True)
                    # Extraer números del texto
                    import re
                    numbers = re.findall(r'[\d,]+\.?\d*', amount_text)
                    if numbers:
                        order_data['total_amount'] = numbers[0]
                    break
            
            # Buscar información adicional de la orden
            description_selectors = [
                ".vendor-field a .link",  # Nombre del restaurante/vendor
                ".vendor-field span.link",
                "td .vendor-field a",
                "td .vendor-field span",
                ".rider-name a .link",  # Nombre del repartidor
                ".rider-name span.link",
                "td .rider-name a",
                "td .rider-name span",
                "span[class*='description']",
                "span[class*='descripcion']",
                "span[class*='task-desc']",
                "td[class*='description']",
                "td[class*='descripcion']",
                "td[class*='task-desc']"
            ]
            
            for selector in description_selectors:
                element = container.select_one(selector)
                if element:
                    order_data['description'] = element.get_text(strip=True)
                    break
            
            # Solo retornar si se encontró al menos un ID de orden o número de pedido
            if 'order_id' in order_data or 'order_number' in order_data:
                return order_data
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Error parseando contenedor de active_order: {e}")
            return None
    
    def save_order_to_database(self, order_data):
        """Guardar active_order en la base de datos"""
        try:
            # Crear cliente si no existe
            customer_name = order_data.get('customer_name', 'Cliente Desconocido')
            
            # Verificar si el cliente ya existe
            self.db_cursor.execute("SELECT id FROM customers WHERE name = %s", (customer_name,))
            customer_result = self.db_cursor.fetchone()
            
            if customer_result:
                customer_id = customer_result['id']
            else:
                # Crear nuevo cliente
                self.db_cursor.execute("""
                    INSERT INTO customers (name, email, phone)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (customer_name, f"{customer_name.lower().replace(' ', '')}@example.com", "N/A"))
                customer_id = self.db_cursor.fetchone()['id']
            
            # Verificar si el pedido ya existe
            order_number = order_data.get('order_number') or order_data.get('order_id')
            self.db_cursor.execute("SELECT id FROM orders WHERE order_number = %s", (order_number,))
            order_result = self.db_cursor.fetchone()
            
            if order_result:
                # Actualizar pedido existente
                order_id = order_result['id']
                self.db_cursor.execute("""
                    UPDATE orders SET 
                        status = %s,
                        delivery_address = %s,
                        notes = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    order_data.get('status', 'active'),
                    order_data.get('delivery_address', 'Dirección no especificada'),
                    f"Active Order from /tasks - {order_data.get('description', 'Sin descripción')} - ID: {order_data.get('order_id', 'N/A')}",
                    order_id
                ))
            else:
                # Crear nuevo pedido
                self.db_cursor.execute("""
                    INSERT INTO orders (order_number, status, customer_id, delivery_address, 
                                       product_type, priority_level, created_at, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    order_number,
                    order_data.get('status', 'active'),
                    customer_id,
                    order_data.get('delivery_address', 'Dirección no especificada'),
                    'Active Order',  # Tipo específico para active_orders
                    'high',  # Prioridad alta para active_orders
                    datetime.now(),
                    f"Active Order from /tasks - {order_data.get('description', 'Sin descripción')} - ID: {order_data.get('order_id', 'N/A')}"
                ))
                order_id = self.db_cursor.fetchone()['id']
            
            # Crear evento de detección específico
            self.db_cursor.execute("""
                INSERT INTO order_events (order_id, event_type, screen_coordinates, raw_data)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                'active_order_detected',
                'x:0,y:0',
                json.dumps(order_data)
            ))
            
            # Crear notificación específica
            self.db_cursor.execute("""
                INSERT INTO notifications (order_id, notification_type, recipient, message, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id,
                'system',
                'admin@besmartdelivery.mx',
                f"Nuevo active_order detectado en /tasks: {order_number}",
                'sent'
            ))
            
            self.db_conn.commit()
            logging.info(f"✅ Active_order guardado en BD: {order_number}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error guardando active_order en BD: {e}")
            self.db_conn.rollback()
            return False
    
    def play_notification_sound(self):
        """Reproducir sonido de notificación"""
        if MONITOR_CONFIG["notification_sound"]:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                # Fallback para sistemas sin winsound
                print('\a')  # Beep del sistema
    
    def display_order_notification(self, order_data):
        """Mostrar notificación de nuevo active_order"""
        order_id = order_data.get('order_id', 'N/A')
        order_number = order_data.get('order_number', 'N/A')
        customer_name = order_data.get('customer_name', 'Cliente Desconocido')
        delivery_address = order_data.get('delivery_address', 'Dirección no especificada')
        total_amount = order_data.get('total_amount', 'N/A')
        description = order_data.get('description', 'Sin descripción')
        status = order_data.get('status', 'En Preparación')
        
        print("\n" + "="*60)
        print("🚨 ¡NUEVA ORDEN ACTIVA DETECTADA! 🚨")
        print("="*60)
        print(f"🎯 ID de Orden: {order_id}")
        print(f"📦 Número de Pedido: {order_number}")
        print(f"👤 Cliente: {customer_name}")
        print(f"📍 Dirección: {delivery_address}")
        print(f"💰 Monto: {total_amount}")
        print(f"🏪 Restaurante/Repartidor: {description}")
        print(f"📊 Estado: {status}")
        print(f"🌐 Página: /tasks")
        print(f"⏰ Detectado: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        # Reproducir sonido
        self.play_notification_sound()
    
    def monitor_orders(self):
        """Función principal de monitoreo de active_orders"""
        logging.info("🔍 Iniciando monitoreo de active_orders en /tasks...")
        console_log("Iniciando monitoreo de active_orders en /tasks...", "MONITOR")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Extraer nuevos active_orders
                new_orders = self.extract_new_orders()
                
                # Procesar nuevos active_orders
                for order_data in new_orders:
                    self.display_order_notification(order_data)
                    self.save_order_to_database(order_data)
                
                # Actualizar estadísticas
                self.order_stats['total_checks'] += 1
                self.last_check_time = current_time
                
                # Mostrar estadísticas cada 10 verificaciones
                if self.order_stats['total_checks'] % 10 == 0:
                    self.display_stats()
                
                # Esperar antes de la siguiente verificación
                time.sleep(MONITOR_CONFIG["check_interval"])
                
            except Exception as e:
                logging.error(f"❌ Error en monitoreo de active_orders: {e}")
                console_log(f"Error en monitoreo de active_orders: {e}", "ERROR")
                time.sleep(MONITOR_CONFIG["check_interval"])
    
    def display_stats(self):
        """Mostrar estadísticas del monitoreo de active_orders"""
        print(f"\n📊 Estadísticas del Monitor de Active_Orders:")
        print(f"   Verificaciones totales: {self.order_stats['total_checks']}")
        print(f"   Nuevos active_orders detectados: {self.order_stats['new_orders']}")
        print(f"   Última verificación: {self.last_check_time.strftime('%H:%M:%S')}")
        print(f"   Active_orders conocidos: {len(self.known_orders)}")
        print(f"   Página monitoreada: /task")
    
    def start_monitoring(self):
        """Iniciar el monitoreo de active_orders"""
        try:
            logging.info("🚀 Iniciando Monitor de Active_Orders en /tasks")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.find_orders_page():
                return False
            
            self.is_running = True
            self.last_check_time = datetime.now()
            
            print("\n" + "="*60)
            print("🎯 MONITOR DE ACTIVE_ORDERS EN /TASKS")
            print("="*60)
            print("✅ Sistema iniciado correctamente")
            print(f"🌐 Página monitoreada: /tasks")
            print(f"⏱️  Intervalo de verificación: {MONITOR_CONFIG['check_interval']} segundos")
            print(f"🔔 Notificaciones de sonido: {'Activadas' if MONITOR_CONFIG['notification_sound'] else 'Desactivadas'}")
            print("="*60)
            print("💡 Presiona Ctrl+C para detener el monitoreo")
            print("="*60)
            
            # Iniciar monitoreo en hilo separado
            monitor_thread = threading.Thread(target=self.monitor_orders)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Mantener el hilo principal vivo
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("⏹️ Detención solicitada por el usuario")
                self.stop_monitoring()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error iniciando monitoreo de active_orders: {e}")
            return False
    
    def stop_monitoring(self):
        """Detener el monitoreo"""
        logging.info("🛑 Deteniendo monitoreo...")
        self.is_running = False
        
        if self.driver:
            self.driver.quit()
        
        if self.db_cursor:
            self.db_cursor.close()
        
        if self.db_conn:
            self.db_conn.close()
        
        self.display_stats()
        logging.info("✅ Monitoreo detenido correctamente")

def main():
    """Función principal del monitor de active_orders"""
    monitor = OrderMonitor()
    
    try:
        success = monitor.start_monitoring()
        if not success:
            logging.error("❌ No se pudo iniciar el monitoreo de active_orders")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Error general en monitor de active_orders: {e}")
        monitor.stop_monitoring()
        sys.exit(1)

if __name__ == "__main__":
    main() 