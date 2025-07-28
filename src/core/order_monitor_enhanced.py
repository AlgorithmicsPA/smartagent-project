#!/usr/bin/env python3
"""
Monitor de Pedidos en Tiempo Real - SmartAgent Enhanced
Versión mejorada con detección más precisa, mejor rendimiento y funcionalidades avanzadas
"""

import sys
import os
from pathlib import Path
import time
import json
import logging
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import hashlib
import re

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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import random

# Cargar variables de entorno
load_dotenv(project_root / "config" / ".env")

# Configuración mejorada
MONITOR_CONFIG = {
    "check_interval": 15,           # Segundos entre verificaciones (más frecuente)
    "order_timeout": 300,           # Segundos para considerar un pedido como "nuevo"
    "max_retries": 5,               # Máximo de reintentos en caso de error
    "notification_sound": True,     # Sonido de notificación
    "log_level": "INFO",
    "max_known_orders": 1000,       # Máximo de órdenes conocidas en memoria
    "page_load_timeout": 30,        # Timeout para cargar página
    "element_wait_timeout": 10,     # Timeout para esperar elementos
    "enable_auto_refresh": True,    # Auto-refresh de página
    "refresh_interval": 300,        # Segundos entre auto-refresh
    "enable_debug_mode": False,     # Modo debug para desarrollo
    "save_screenshots": True,       # Guardar screenshots de nuevas órdenes
    "enable_webhook": False,        # Habilitar webhooks para notificaciones
    "webhook_url": "",             # URL del webhook
    "enable_database_logging": True, # Logging detallado en base de datos
    "enable_performance_monitoring": True, # Monitoreo de rendimiento
    "max_concurrent_orders": 50,    # Máximo de órdenes concurrentes
    "order_priority_levels": ["urgent", "high", "normal", "low"], # Niveles de prioridad
    "enable_order_analytics": True, # Análisis de órdenes
    "enable_restaurant_tracking": True, # Seguimiento de restaurantes
    "enable_customer_tracking": True,   # Seguimiento de clientes
    "enable_delivery_optimization": True, # Optimización de entregas
}

# Configuración de logging mejorada
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, MONITOR_CONFIG["log_level"]),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/order_monitor_enhanced.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Variables globales
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "federico")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "***CONTRASEÑA_OCULTA***")
DATABASE_URL = os.getenv("DATABASE_URL")

class EnhancedConsoleLogger:
    """Logger mejorado para consola con colores y emojis"""
    
    @staticmethod
    def log(message, level="INFO", emoji="ℹ️"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
    
    @staticmethod
    def info(message):
        EnhancedConsoleLogger.log(message, "INFO", "ℹ️")
    
    @staticmethod
    def success(message):
        EnhancedConsoleLogger.log(message, "SUCCESS", "✅")
    
    @staticmethod
    def warning(message):
        EnhancedConsoleLogger.log(message, "WARNING", "⚠️")
    
    @staticmethod
    def error(message):
        EnhancedConsoleLogger.log(message, "ERROR", "❌")
    
    @staticmethod
    def monitor(message):
        EnhancedConsoleLogger.log(message, "MONITOR", "🎯")
    
    @staticmethod
    def detection(message):
        EnhancedConsoleLogger.log(message, "DETECTION", "🔍")
    
    @staticmethod
    def notification(message):
        EnhancedConsoleLogger.log(message, "NOTIFICATION", "🔔")
    
    @staticmethod
    def performance(message):
        EnhancedConsoleLogger.log(message, "PERFORMANCE", "⚡")
    
    @staticmethod
    def analytics(message):
        EnhancedConsoleLogger.log(message, "ANALYTICS", "📊")

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

class EnhancedOrderMonitor:
    """Monitor de órdenes mejorado con funcionalidades avanzadas"""
    
    def __init__(self):
        self.driver = None
        self.db_conn = None
        self.db_cursor = None
        self.is_running = False
        self.last_check_time = None
        self.known_orders = set()
        self.order_hashes = set()  # Para detección más precisa
        self.order_stats = defaultdict(int)
        self.analytics = OrderAnalytics()
        self.performance_start_time = None
        self.last_refresh_time = None
        self.error_count = 0
        self.success_count = 0
        self.setup_database()
        
    def setup_database(self):
        """Configurar conexión a la base de datos con manejo de errores mejorado"""
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            logging.info("✅ Conexión a base de datos establecida")
            EnhancedConsoleLogger.success("Conexión a base de datos establecida")
            
            # Crear tabla de órdenes si no existe
            self.create_orders_table()
            
        except Exception as e:
            logging.error(f"❌ Error conectando a la base de datos: {e}")
            EnhancedConsoleLogger.error(f"Error conectando a la base de datos: {e}")
    
    def create_orders_table(self):
        """Crear tabla de órdenes con estructura mejorada"""
        try:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS enhanced_orders (
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
            logging.info("✅ Tabla de órdenes mejorada creada/verificada")
            
        except Exception as e:
            logging.error(f"❌ Error creando tabla de órdenes: {e}")
    
    def setup_driver(self):
        """Configurar ChromeDriver con opciones optimizadas"""
        try:
            chrome_path = ChromeDriverManager().install()
            service = Service(chrome_path)
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Optimizaciones de rendimiento
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # No cargar imágenes para mayor velocidad
            chrome_options.add_argument("--disable-javascript")  # Deshabilitar JS si no es necesario
            chrome_options.add_argument("--disable-css")  # Deshabilitar CSS si no es necesario
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            
            # User agent realista
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Configurar timeouts
            self.driver.set_page_load_timeout(MONITOR_CONFIG["page_load_timeout"])
            self.driver.implicitly_wait(MONITOR_CONFIG["element_wait_timeout"])
            
            logging.info("✅ ChromeDriver configurado con optimizaciones")
            EnhancedConsoleLogger.success("ChromeDriver configurado con optimizaciones")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error configurando ChromeDriver: {e}")
            EnhancedConsoleLogger.error(f"Error configurando ChromeDriver: {e}")
            return False
    
    def login(self):
        """Iniciar sesión con manejo de errores mejorado"""
        try:
            EnhancedConsoleLogger.info(f"Intentando login con usuario: {ADMIN_USERNAME}")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            
            # Guardar screenshot para debugging
            if MONITOR_CONFIG["save_screenshots"]:
                self.driver.save_screenshot("login_page_enhanced.png")
            
            # Estrategias de login mejoradas
            login_strategies = [
                self._try_login_strategy_1,
                self._try_login_strategy_2,
                self._try_login_strategy_3
            ]
            
            for strategy in login_strategies:
                if strategy():
                    EnhancedConsoleLogger.success("Login exitoso")
                    return True
            
            EnhancedConsoleLogger.error("No se pudo iniciar sesión con ninguna estrategia")
            return False
            
        except Exception as e:
            logging.error(f"❌ Error en login: {e}")
            EnhancedConsoleLogger.error(f"Error en login: {e}")
            return False
    
    def _try_login_strategy_1(self):
        """Estrategia de login 1: Campos básicos"""
        try:
            # Buscar campo de usuario
            username_field = self.driver.find_element(By.NAME, "uid")
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            
            # Buscar campo de contraseña
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Buscar botón de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.button.login.main")
            login_button.click()
            
            time.sleep(5)
            return "admin" in self.driver.current_url.lower()
            
        except Exception:
            return False
    
    def _try_login_strategy_2(self):
        """Estrategia de login 2: Selectores alternativos"""
        try:
            # Buscar por múltiples selectores
            username_selectors = ["input[name='uid']", "input[type='text']", "#username"]
            password_selectors = ["input[name='password']", "input[type='password']", "#password"]
            login_selectors = ["button[type='submit']", "input[type='submit']", ".login-button"]
            
            # Encontrar campos
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not username_field:
                return False
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_field:
                return False
            
            # Llenar campos
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Encontrar botón de login
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                time.sleep(5)
                return "admin" in self.driver.current_url.lower()
            
            return False
            
        except Exception:
            return False
    
    def _try_login_strategy_3(self):
        """Estrategia de login 3: JavaScript injection"""
        try:
            # Inyectar JavaScript para llenar campos
            self.driver.execute_script("""
                var usernameField = document.querySelector('input[name="uid"]') || 
                                  document.querySelector('input[type="text"]') ||
                                  document.getElementById('username');
                var passwordField = document.querySelector('input[name="password"]') || 
                                  document.querySelector('input[type="password"]') ||
                                  document.getElementById('password');
                
                if (usernameField && passwordField) {
                    usernameField.value = arguments[0];
                    passwordField.value = arguments[1];
                    return true;
                }
                return false;
            """, ADMIN_USERNAME, ADMIN_PASSWORD)
            
            # Buscar y hacer clic en botón de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.button.login.main")
            login_button.click()
            
            time.sleep(5)
            return "admin" in self.driver.current_url.lower()
            
        except Exception:
            return False
    
    def find_orders_page(self):
        """Navegar a la página de órdenes con manejo de errores mejorado"""
        try:
            EnhancedConsoleLogger.info("Navegando a la página de órdenes...")
            
            # Intentar navegar directamente a /tasks
            self.driver.get(f"{LOGIN_URL.rstrip('/')}/tasks")
            time.sleep(3)
            
            # Verificar si estamos en la página correcta
            if "tasks" in self.driver.current_url.lower():
                EnhancedConsoleLogger.success("Página de órdenes cargada correctamente")
                return True
            
            # Si no funciona, buscar enlaces en la página
            try:
                tasks_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'tasks') or contains(text(), 'Tasks') or contains(text(), 'Tareas')]")
                tasks_link.click()
                time.sleep(3)
                EnhancedConsoleLogger.success("Navegación a página de órdenes exitosa")
                return True
            except:
                pass
            
            EnhancedConsoleLogger.warning("No se pudo navegar a la página de órdenes específica")
            return True  # Continuar con la página actual
            
        except Exception as e:
            logging.error(f"❌ Error navegando a página de órdenes: {e}")
            EnhancedConsoleLogger.error(f"Error navegando a página de órdenes: {e}")
            return False
    
    def generate_order_hash(self, order_data):
        """Generar hash único para la orden basado en sus datos"""
        hash_string = f"{order_data.get('order_id', '')}{order_data.get('customer_name', '')}{order_data.get('delivery_address', '')}{order_data.get('timestamp', '')}"
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def extract_new_orders(self):
        """Extraer nuevas órdenes con detección mejorada"""
        try:
            start_time = time.time()
            EnhancedConsoleLogger.detection("Extrayendo órdenes de la página...")
            
            # Auto-refresh si está habilitado
            if MONITOR_CONFIG["enable_auto_refresh"]:
                current_time = time.time()
                if not self.last_refresh_time or (current_time - self.last_refresh_time) > MONITOR_CONFIG["refresh_interval"]:
                    self.driver.refresh()
                    time.sleep(3)
                    self.last_refresh_time = current_time
                    EnhancedConsoleLogger.info("Página refrescada automáticamente")
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            new_orders = []
            current_time = datetime.now()
            
            # Estrategias de detección mejoradas
            order_containers = self._find_order_containers(soup)
            
            EnhancedConsoleLogger.detection(f"Encontrados {len(order_containers)} contenedores de órdenes")
            
            # Procesar cada contenedor
            for container in order_containers:
                order_data = self._parse_order_container(container)
                if order_data:
                    order_hash = self.generate_order_hash(order_data)
                    
                    if order_hash not in self.order_hashes:
                        # Es una orden nueva
                        order_data['order_hash'] = order_hash
                        order_data['detected_at'] = current_time.isoformat()
                        order_data['source'] = 'enhanced_monitor'
                        order_data['page'] = '/tasks'
                        
                        new_orders.append(order_data)
                        self.order_hashes.add(order_hash)
                        self.order_stats['new_orders'] += 1
                        
                        # Agregar a analytics
                        self.analytics.add_order(order_data)
                        
                        EnhancedConsoleLogger.notification(f"Nueva orden detectada: {order_data.get('order_id', 'N/A')}")
                        
                        # Limpiar hashes antiguos si excede el límite
                        if len(self.order_hashes) > MONITOR_CONFIG["max_known_orders"]:
                            self.order_hashes.clear()
                            self.known_orders.clear()
            
            # Mostrar tabla de nuevas órdenes
            if new_orders:
                self._display_orders_table(new_orders)
            
            # Métricas de rendimiento
            if MONITOR_CONFIG["enable_performance_monitoring"]:
                processing_time = time.time() - start_time
                EnhancedConsoleLogger.performance(f"Procesamiento completado en {processing_time:.2f}s")
            
            return new_orders
            
        except Exception as e:
            logging.error(f"❌ Error extrayendo órdenes: {e}")
            EnhancedConsoleLogger.error(f"Error extrayendo órdenes: {e}")
            self.error_count += 1
            return []
    
    def _find_order_containers(self, soup):
        """Encontrar contenedores de órdenes con estrategias mejoradas"""
        containers = []
        
        # Estrategia 1: Buscar por selectores específicos
        specific_selectors = [
            "tr.orders-list-item",
            "tr[class*='orders-list-item']",
            "tr[class*='inpreparation']",
            "div[class*='active_orders'] tbody tr",
            "div[class*='task'] tbody tr",
            "table[class*='orders'] tbody tr",
            "table[class*='tasks'] tbody tr"
        ]
        
        for selector in specific_selectors:
            containers.extend(soup.select(selector))
        
        # Estrategia 2: Buscar por contenido de texto
        if not containers:
            all_elements = soup.find_all(['tr', 'div', 'li'])
            for element in all_elements:
                text = element.get_text().lower()
                if any(keyword in text for keyword in ['order', 'pedido', 'task', 'tarea', 'preparation', 'preparación']):
                    containers.append(element)
        
        # Estrategia 3: Buscar por estructura de tabla
        if not containers:
            tables = soup.find_all('table')
            for table in tables:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        if len(row.find_all('td')) >= 3:  # Al menos 3 columnas
                            containers.append(row)
        
        return containers
    
    def _parse_order_container(self, container):
        """Parsear contenedor de orden con extracción mejorada"""
        try:
            order_data = {
                'timestamp': datetime.now().isoformat(),
                'raw_html': str(container)[:1000],  # Limitar tamaño
                'type': 'enhanced_order'
            }
            
            # Extraer ID de orden
            order_id = self._extract_order_id(container)
            if order_id:
                order_data['order_id'] = order_id
            
            # Extraer información del cliente
            customer_name = self._extract_customer_info(container)
            if customer_name:
                order_data['customer_name'] = customer_name
            
            # Extraer dirección
            address = self._extract_address(container)
            if address:
                order_data['delivery_address'] = address
            
            # Extraer restaurante
            restaurant = self._extract_restaurant(container)
            if restaurant:
                order_data['restaurant'] = restaurant
            
            # Extraer monto
            amount = self._extract_amount(container)
            if amount:
                order_data['total_amount'] = amount
            
            # Extraer estado
            status = self._extract_status(container)
            if status:
                order_data['status'] = status
            
            # Determinar prioridad
            priority = self._determine_priority(order_data)
            order_data['priority'] = priority
            
            return order_data if order_data.get('order_id') else None
            
        except Exception as e:
            logging.error(f"❌ Error parseando contenedor: {e}")
            return None
    
    def _extract_order_id(self, container):
        """Extraer ID de orden con múltiples estrategias"""
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
    
    def _extract_customer_info(self, container):
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
    
    def _extract_address(self, container):
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
    
    def _extract_restaurant(self, container):
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
    
    def _extract_amount(self, container):
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
    
    def _extract_status(self, container):
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
    
    def _determine_priority(self, order_data):
        """Determinar prioridad de la orden"""
        # Lógica de prioridad basada en múltiples factores
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
        customer = order_data.get('customer_name', '')
        if customer in self.analytics.customer_stats and self.analytics.customer_stats[customer] > 5:
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
    
    def _display_orders_table(self, orders):
        """Mostrar tabla de órdenes con formato mejorado"""
        print("\n" + "="*120)
        print("🎯 NUEVAS ÓRDENES DETECTADAS - MONITOR MEJORADO")
        print("="*120)
        print(f"{'ID':<8} {'Prioridad':<10} {'Estado':<15} {'Restaurante':<25} {'Cliente':<20} {'Dirección':<30} {'Precio':<12} {'Hora':<8}")
        print("-"*120)
        
        for order_data in orders:
            order_id = order_data.get('order_id', 'N/A')
            priority = order_data.get('priority', 'normal').upper()
            status = order_data.get('status', 'N/A')
            restaurant = order_data.get('restaurant', 'N/A')
            customer = order_data.get('customer_name', 'N/A')
            address = order_data.get('delivery_address', 'N/A')
            if len(address) > 29:
                address = address[:29] + "..."
            price = order_data.get('total_amount', 'N/A')
            time_str = datetime.now().strftime('%H:%M')
            
            print(f"{order_id:<8} {priority:<10} {status:<15} {restaurant:<25} {customer:<20} {address:<30} {price:<12} {time_str:<8}")
        
        print("-"*120)
        print(f"📊 Nuevas órdenes detectadas: {len(orders)}")
        print("="*120 + "\n")
    
    def save_order_to_database(self, order_data):
        """Guardar orden en base de datos con estructura mejorada"""
        try:
            insert_query = """
            INSERT INTO enhanced_orders (
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
            analytics_data = json.dumps(self.analytics.get_analytics_report())
            performance_data = json.dumps({
                'processing_time': time.time() - self.performance_start_time if self.performance_start_time else 0,
                'error_count': self.error_count,
                'success_count': self.success_count
            })
            
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
            
            self.success_count += 1
            EnhancedConsoleLogger.success(f"Orden guardada en BD: {order_data.get('order_id', 'N/A')}")
            
        except Exception as e:
            logging.error(f"❌ Error guardando orden en BD: {e}")
            EnhancedConsoleLogger.error(f"Error guardando orden en BD: {e}")
            self.error_count += 1
    
    def play_notification_sound(self):
        """Reproducir sonido de notificación"""
        if MONITOR_CONFIG["notification_sound"]:
            try:
                # Usar beep del sistema
                import winsound
                winsound.Beep(1000, 500)  # Frecuencia 1000Hz, duración 500ms
            except:
                # Fallback: imprimir caracteres especiales
                print("\a")  # Bell character
    
    def display_enhanced_stats(self):
        """Mostrar estadísticas mejoradas"""
        analytics_report = self.analytics.get_analytics_report()
        
        print(f"\n📊 ESTADÍSTICAS DEL MONITOR MEJORADO")
        print("="*60)
        print(f"   Verificaciones totales: {self.order_stats['total_checks']}")
        print(f"   Nuevas órdenes detectadas: {self.order_stats['new_orders']}")
        print(f"   Órdenes en memoria: {len(self.order_hashes)}")
        print(f"   Última verificación: {self.last_check_time.strftime('%H:%M:%S') if self.last_check_time else 'N/A'}")
        print(f"   Tasa de éxito: {(self.success_count / max(self.success_count + self.error_count, 1)) * 100:.1f}%")
        print(f"   Errores totales: {self.error_count}")
        
        if analytics_report['total_orders'] > 0:
            print(f"\n📈 ANÁLISIS DE ÓRDENES:")
            print(f"   Total de órdenes procesadas: {analytics_report['total_orders']}")
            print(f"   Promedio por hora: {analytics_report['avg_orders_per_hour']:.1f}")
            
            if analytics_report['top_restaurants']:
                print(f"   Restaurante más activo: {analytics_report['top_restaurants'][0][0]}")
            
            if analytics_report['peak_hours']:
                print(f"   Hora pico: {analytics_report['peak_hours'][0][0]}:00")
    
    def monitor_orders(self):
        """Función principal de monitoreo mejorada"""
        EnhancedConsoleLogger.monitor("Iniciando monitoreo mejorado de órdenes...")
        
        while self.is_running:
            try:
                self.performance_start_time = time.time()
                current_time = datetime.now()
                
                # Extraer nuevas órdenes
                new_orders = self.extract_new_orders()
                
                # Procesar nuevas órdenes
                for order_data in new_orders:
                    self.save_order_to_database(order_data)
                    self.play_notification_sound()
                
                # Actualizar estadísticas
                self.order_stats['total_checks'] += 1
                self.last_check_time = current_time
                
                # Mostrar estadísticas cada 20 verificaciones
                if self.order_stats['total_checks'] % 20 == 0:
                    self.display_enhanced_stats()
                
                # Esperar antes de la siguiente verificación
                time.sleep(MONITOR_CONFIG["check_interval"])
                
            except Exception as e:
                logging.error(f"❌ Error en monitoreo: {e}")
                EnhancedConsoleLogger.error(f"Error en monitoreo: {e}")
                self.error_count += 1
                time.sleep(MONITOR_CONFIG["check_interval"])
    
    def start_monitoring(self):
        """Iniciar el monitoreo mejorado"""
        try:
            EnhancedConsoleLogger.monitor("🚀 Iniciando Monitor de Órdenes Mejorado")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.find_orders_page():
                return False
            
            self.is_running = True
            self.last_check_time = datetime.now()
            self.last_refresh_time = time.time()
            
            print("\n" + "="*80)
            print("🎯 MONITOR DE ÓRDENES MEJORADO - SMARTAGENT ENHANCED")
            print("="*80)
            print("✅ Sistema iniciado correctamente")
            print(f"🌐 Página monitoreada: /tasks")
            print(f"⏱️  Intervalo de verificación: {MONITOR_CONFIG['check_interval']} segundos")
            print(f"🔄 Auto-refresh: {'Activado' if MONITOR_CONFIG['enable_auto_refresh'] else 'Desactivado'}")
            print(f"🔔 Notificaciones: {'Activadas' if MONITOR_CONFIG['notification_sound'] else 'Desactivadas'}")
            print(f"📊 Analytics: {'Activado' if MONITOR_CONFIG['enable_order_analytics'] else 'Desactivado'}")
            print(f"⚡ Performance monitoring: {'Activado' if MONITOR_CONFIG['enable_performance_monitoring'] else 'Desactivado'}")
            print("="*80)
            print("💡 Presiona Ctrl+C para detener el monitoreo")
            print("="*80)
            
            # Iniciar monitoreo en hilo separado
            monitor_thread = threading.Thread(target=self.monitor_orders)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Mantener el hilo principal vivo
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                EnhancedConsoleLogger.info("⏹️ Detención solicitada por el usuario")
                self.stop_monitoring()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error iniciando monitoreo: {e}")
            EnhancedConsoleLogger.error(f"Error iniciando monitoreo: {e}")
            return False
    
    def stop_monitoring(self):
        """Detener el monitoreo"""
        EnhancedConsoleLogger.info("🛑 Deteniendo monitoreo...")
        self.is_running = False
        
        if self.driver:
            self.driver.quit()
        
        if self.db_cursor:
            self.db_cursor.close()
        
        if self.db_conn:
            self.db_conn.close()
        
        self.display_enhanced_stats()
        EnhancedConsoleLogger.success("✅ Monitoreo detenido correctamente")

def main():
    """Función principal del monitor mejorado"""
    monitor = EnhancedOrderMonitor()
    
    try:
        success = monitor.start_monitoring()
        if not success:
            EnhancedConsoleLogger.error("❌ No se pudo iniciar el monitoreo")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Error general en monitor: {e}")
        EnhancedConsoleLogger.error(f"Error general en monitor: {e}")
        monitor.stop_monitoring()
        sys.exit(1)

if __name__ == "__main__":
    main() 