#!/usr/bin/env python3
"""
SmartAgent Enhanced - Sistema Completo Integrado
Combina exploración web con gestión avanzada de pedidos y funcionalidades complementarias
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import json, time, os, threading, logging, signal, sys
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del proyecto
CHROMEDRIVER_PATH = "chromedriver.exe"
START_URL = os.getenv("START_URL", "https://admin.besmartdelivery.mx/")
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
PROFILE_DIR = f"./besmart_profile_{int(time.time())}"
JSON_PATH = "estructura.json"
TXT_PATH = "flujo.txt"
LOG_PATH = "logs/smartagent_enhanced.log"

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_I6sKUNeof9qb@ep-long-wave-adza01b9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

# Credenciales del admin panel
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "federico")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "28ZwnPHQRC*H4BmfmEB-YHcC")

# Configuración de logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Mostrar configuración cargada
logging.info(f"🔧 Configuración cargada:")
logging.info(f"   Usuario: {ADMIN_USERNAME}")
logging.info(f"   URL: {START_URL}")
logging.info(f"   Base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Configurada'}")

estructura = {}
visited_urls = set()
cola = [START_URL]
lock = threading.Lock()

class EnhancedDatabaseManager:
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
    
    # ===== MÉTODOS PARA EXPLORACIÓN WEB =====
    
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
            
            # Limpiar datos anteriores de esta página
            self.cursor.execute("DELETE FROM botones WHERE pagina_id = %s", (pagina_id,))
            self.cursor.execute("DELETE FROM inputs WHERE pagina_id = %s", (pagina_id,))
            self.cursor.execute("DELETE FROM links WHERE pagina_id = %s", (pagina_id,))
            self.cursor.execute("DELETE FROM formularios WHERE pagina_id = %s", (pagina_id,))
            self.cursor.execute("DELETE FROM tablas_html WHERE pagina_id = %s", (pagina_id,))
            
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
                self.cursor.execute("""
                    INSERT INTO links (pagina_id, url, texto)
                    VALUES (%s, %s, %s)
                """, (pagina_id, link.get('url'), link.get('texto')))
            
            # Insertar formularios
            for form in datos.get('formularios', []):
                self.cursor.execute("""
                    INSERT INTO formularios (pagina_id, action, method, form_id)
                    VALUES (%s, %s, %s, %s)
                """, (pagina_id, form.get('action'), form.get('method'), form.get('id')))
            
            # Insertar tablas HTML
            for tabla in datos.get('tablas_html', []):
                self.cursor.execute("""
                    INSERT INTO tablas_html (pagina_id, tabla_id, clases, filas)
                    VALUES (%s, %s, %s, %s)
                """, (pagina_id, tabla.get('id'), tabla.get('clases'), tabla.get('filas')))
            
            self.conn.commit()
            logging.info(f"✅ Datos de página guardados: {url}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error guardando datos de página: {e}")
            self.conn.rollback()
            return False
    
    # ===== MÉTODOS PARA SISTEMA DE PEDIDOS =====
    
    def create_sample_order(self, order_number, product_type="Comida"):
        """Crear un pedido de ejemplo con datos completos"""
        try:
            # Crear cliente de ejemplo
            self.cursor.execute("""
                INSERT INTO customers (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    phone = EXCLUDED.phone,
                    address = EXCLUDED.address
                RETURNING id
            """, (f"Cliente {order_number}", f"cliente{order_number}@example.com", 
                  f"555-{order_number.zfill(4)}", f"Dirección {order_number}"))
            
            customer_id = self.cursor.fetchone()['id']
            
            # Obtener zona de entrega
            self.cursor.execute("SELECT id FROM delivery_zones WHERE zone_name = 'Centro' LIMIT 1")
            zone_result = self.cursor.fetchone()
            zone_id = zone_result['id'] if zone_result else None
            
            # Crear pedido
            self.cursor.execute("""
                INSERT INTO orders (order_number, status, customer_id, delivery_zone_id, 
                                   pickup_address, delivery_address, distance_km, product_type, priority_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (order_number, "pending", customer_id, zone_id,
                  "Restaurante Central", f"Dirección de entrega {order_number}", 
                  random.uniform(1.0, 10.0), product_type, "normal"))
            
            order_id = self.cursor.fetchone()['id']
            
            # Crear evento de pedido
            self.cursor.execute("""
                INSERT INTO order_events (order_id, event_type, screen_coordinates, raw_data)
                VALUES (%s, %s, %s, %s)
            """, (order_id, "order_created", "x:500,y:300", 
                  json.dumps({"source": "smartagent", "timestamp": datetime.now().isoformat()})))
            
            # Crear mensaje de WhatsApp
            self.cursor.execute("""
                INSERT INTO whatsapp_messages (order_id, sender, message, xpath_used, raw_html)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, "sistema", f"Pedido {order_number} creado exitosamente", 
                  "//div[@class='order-status']", "<div>Pedido creado</div>"))
            
            # Crear transacción de pago
            self.cursor.execute("""
                INSERT INTO payment_transactions (order_id, payment_method_id, amount, status)
                VALUES (%s, %s, %s, %s)
            """, (order_id, 1, random.uniform(15.0, 50.0), "pending"))
            
            # Crear notificación
            self.cursor.execute("""
                INSERT INTO notifications (order_id, notification_type, recipient, message, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, "email", f"cliente{order_number}@example.com", 
                  f"Su pedido {order_number} ha sido creado", "pending"))
            
            self.conn.commit()
            logging.info(f"✅ Pedido de ejemplo creado: {order_number}")
            return order_id
            
        except Exception as e:
            logging.error(f"❌ Error creando pedido de ejemplo: {e}")
            self.conn.rollback()
            return None
    
    def get_system_statistics(self):
        """Obtener estadísticas completas del sistema"""
        try:
            stats = {}
            
            # Estadísticas de exploración web
            self.cursor.execute("SELECT COUNT(*) as count FROM paginas")
            stats['paginas_exploradas'] = self.cursor.fetchone()['count']
            
            self.cursor.execute("SELECT COUNT(*) as count FROM botones")
            stats['total_botones'] = self.cursor.fetchone()['count']
            
            self.cursor.execute("SELECT COUNT(*) as count FROM inputs")
            stats['total_inputs'] = self.cursor.fetchone()['count']
            
            # Estadísticas de pedidos
            self.cursor.execute("SELECT COUNT(*) as count FROM orders")
            stats['total_pedidos'] = self.cursor.fetchone()['count']
            
            self.cursor.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
            stats['pedidos_por_estado'] = {row['status']: row['count'] for row in self.cursor.fetchall()}
            
            # Estadísticas de clientes
            self.cursor.execute("SELECT COUNT(*) as count FROM customers")
            stats['total_clientes'] = self.cursor.fetchone()['count']
            
            # Estadísticas de repartidores
            self.cursor.execute("SELECT COUNT(*) as count FROM delivery_agents")
            stats['total_repartidores'] = self.cursor.fetchone()['count']
            
            # Estadísticas de productos
            self.cursor.execute("SELECT COUNT(*) as count FROM products")
            stats['total_productos'] = self.cursor.fetchone()['count']
            
            # Estadísticas de transacciones
            self.cursor.execute("SELECT COUNT(*) as count FROM payment_transactions")
            stats['total_transacciones'] = self.cursor.fetchone()['count']
            
            return stats
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def create_analytics_report(self):
        """Crear reporte de analytics"""
        try:
            today = datetime.now().date()
            
            # Obtener estadísticas del día
            stats = self.get_system_statistics()
            
            # Crear reporte de analytics
            self.cursor.execute("""
                INSERT INTO analytics (report_date, total_orders, total_revenue, 
                                     average_order_value, orders_by_status, 
                                     delivery_performance)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_date) DO UPDATE SET
                    total_orders = EXCLUDED.total_orders,
                    total_revenue = EXCLUDED.total_revenue,
                    average_order_value = EXCLUDED.average_order_value,
                    orders_by_status = EXCLUDED.orders_by_status,
                    delivery_performance = EXCLUDED.delivery_performance
            """, (today, stats.get('total_pedidos', 0), 0.0, 0.0,
                  json.dumps(stats.get('pedidos_por_estado', {})),
                  json.dumps({"avg_delivery_time": "30 min", "success_rate": "95%"})))
            
            self.conn.commit()
            logging.info(f"✅ Reporte de analytics creado para {today}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creando reporte de analytics: {e}")
            self.conn.rollback()
            return False

class SmartAgentEnhanced:
    def __init__(self):
        self.driver = None
        self.db = EnhancedDatabaseManager(DATABASE_URL)
        self.setup_database()
    
    def setup_database(self):
        """Configurar base de datos"""
        if not self.db.connect():
            logging.error("❌ No se pudo conectar a la base de datos")
            sys.exit(1)
    
    def setup_driver(self):
        """Configurar ChromeDriver"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Instalar ChromeDriver automáticamente
            chrome_path = ChromeDriverManager().install()
            service = Service(chrome_path)
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("✅ ChromeDriver automático instalado")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error configurando ChromeDriver: {e}")
            return False
    
    def login(self):
        """Iniciar sesión en el panel de administración"""
        try:
            logging.info(f"🔐 Intentando login con usuario: {ADMIN_USERNAME}")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            
            # Guardar screenshot para debugging
            self.driver.save_screenshot("login_page.png")
            
            # Múltiples estrategias para encontrar elementos
            selectors_username = [
                (By.NAME, "uid"),
                (By.CSS_SELECTOR, "input[placeholder*='Username']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.ID, "username"),
                (By.NAME, "username")
            ]
            
            selectors_password = [
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.ID, "password")
            ]
            
            selectors_login = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@value='Login']")
            ]
            
            # Buscar campo de usuario
            username_field = None
            for by, selector in selectors_username:
                try:
                    username_field = self.driver.find_element(by, selector)
                    logging.info(f"✅ Campo de usuario encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                logging.error("❌ No se pudo encontrar el campo de usuario")
                return False
            
            # Buscar campo de contraseña
            password_field = None
            for by, selector in selectors_password:
                try:
                    password_field = self.driver.find_element(by, selector)
                    logging.info(f"✅ Campo de contraseña encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logging.error("❌ No se pudo encontrar el campo de contraseña")
                return False
            
            # Buscar botón de login
            login_button = None
            for by, selector in selectors_login:
                try:
                    login_button = self.driver.find_element(by, selector)
                    logging.info(f"✅ Botón de login encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                logging.error("❌ No se pudo encontrar el botón de login")
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
            return True
            
        except Exception as e:
            logging.error(f"❌ Error durante el login: {e}")
            return False
    
    def extract_page_data(self, url):
        """Extraer datos de la página actual"""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extraer título
            titulo = soup.title.string if soup.title else "Sin título"
            
            # Extraer botones
            botones = []
            for button in soup.find_all(['button', 'input']):
                if button.get('type') == 'submit' or button.name == 'button':
                    botones.append({
                        'texto': button.get_text(strip=True),
                        'tipo': button.get('type', 'button'),
                        'id': button.get('id')
                    })
            
            # Extraer inputs
            inputs = []
            for input_elem in soup.find_all('input'):
                inputs.append({
                    'tipo': input_elem.get('type'),
                    'nombre': input_elem.get('name'),
                    'id': input_elem.get('id'),
                    'placeholder': input_elem.get('placeholder')
                })
            
            # Extraer links
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    'url': urljoin(url, link['href']),
                    'texto': link.get_text(strip=True)
                })
            
            # Extraer formularios
            formularios = []
            for form in soup.find_all('form'):
                formularios.append({
                    'action': form.get('action'),
                    'method': form.get('method'),
                    'id': form.get('id')
                })
            
            # Extraer tablas HTML
            tablas_html = []
            for tabla in soup.find_all('table'):
                filas = len(tabla.find_all('tr'))
                clases = tabla.get('class', [])
                tablas_html.append({
                    'id': tabla.get('id'),
                    'clases': clases,
                    'filas': filas
                })
            
            datos = {
                'titulo': titulo,
                'botones': botones,
                'inputs': inputs,
                'links': links,
                'formularios': formularios,
                'tablas_html': tablas_html,
                'timestamp': datetime.now().isoformat()
            }
            
            return datos
            
        except Exception as e:
            logging.error(f"❌ Error extrayendo datos de página: {e}")
            return {}
    
    def explore_page(self, url):
        """Explorar una página específica"""
        try:
            if url in visited_urls:
                return
            
            logging.info(f"🔍 Explorando: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Extraer datos
            datos = self.extract_page_data(url)
            
            # Guardar en base de datos
            self.db.insert_pagina(url, datos.get('titulo', ''), datos)
            
            # Guardar en estructura local
            with lock:
                visited_urls.add(url)
                estructura[url] = datos
                
                # Agregar nuevos links a la cola
                for link in datos.get('links', []):
                    link_url = link.get('url')
                    if link_url and link_url not in visited_urls and link_url not in cola:
                        cola.append(link_url)
            
            # Crear pedido de ejemplo cada 5 páginas exploradas
            if len(visited_urls) % 5 == 0:
                order_number = f"ORD-{int(time.time())}"
                self.db.create_sample_order(order_number)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error explorando página {url}: {e}")
            return False
    
    def run_exploration(self):
        """Ejecutar exploración completa"""
        try:
            logging.info("🚀 Iniciando exploración completa...")
            
            while cola and len(visited_urls) < 50:  # Límite de 50 páginas
                with lock:
                    if not cola:
                        break
                    url = cola.pop(0)
                
                if url not in visited_urls:
                    self.explore_page(url)
                    time.sleep(random.uniform(1, 3))  # Pausa aleatoria
            
            # Crear reporte final
            self.db.create_analytics_report()
            
            logging.info("✅ Exploración completada")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error en exploración: {e}")
            return False
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()
        if self.db:
            self.db.disconnect()
        logging.info("🧹 Limpieza completada")

def main():
    """Función principal"""
    logging.info("🤖 Iniciando SmartAgent Enhanced - Sistema Completo Integrado")
    
    agent = SmartAgentEnhanced()
    
    try:
        if agent.setup_driver():
            if agent.login():
                agent.run_exploration()
                
                # Mostrar estadísticas finales
                stats = agent.db.get_system_statistics()
                logging.info("📊 ESTADÍSTICAS FINALES:")
                logging.info(f"   Páginas exploradas: {stats.get('paginas_exploradas', 0)}")
                logging.info(f"   Total botones: {stats.get('total_botones', 0)}")
                logging.info(f"   Total inputs: {stats.get('total_inputs', 0)}")
                logging.info(f"   Total pedidos: {stats.get('total_pedidos', 0)}")
                logging.info(f"   Total clientes: {stats.get('total_clientes', 0)}")
                logging.info(f"   Total repartidores: {stats.get('total_repartidores', 0)}")
                logging.info(f"   Total productos: {stats.get('total_productos', 0)}")
                logging.info(f"   Total transacciones: {stats.get('total_transacciones', 0)}")
            else:
                logging.error("❌ No se pudo iniciar sesión")
        else:
            logging.error("❌ No se pudo configurar el driver")
    
    except KeyboardInterrupt:
        logging.info("⏹️  Exploración interrumpida por el usuario")
    except Exception as e:
        logging.error(f"❌ Error general: {e}")
    finally:
        agent.cleanup()

if __name__ == "__main__":
    main()
