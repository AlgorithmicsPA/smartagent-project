#!/usr/bin/env python3
"""
SmartAgent Orders - Sistema Integrado
Combina exploración web con gestión de pedidos
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
from datetime import datetime
import json, time, os, threading, logging, signal, sys
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del proyecto
CHROMEDRIVER_PATH = "chromedriver.exe"
START_URL = os.getenv("START_URL", "https://admin.besmartdelivery.mx/")
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
PROFILE_DIR = f"./besmart_profile_{int(time.time())}"
JSON_PATH = "estructura.json"
TXT_PATH = "flujo.txt"
LOG_PATH = "logs/smartagent_orders.log"

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***/***DB_OCULTA***?sslmode=require&channel_binding=require")

# Credenciales del admin panel
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "manus")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "***CONTRASEÑA_OCULTA***")

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
            logging.info(f"💾 Datos guardados en PostgreSQL: {url}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error guardando datos en PostgreSQL {url}: {e}")
            self.conn.rollback()
            return False
    
    def create_sample_order(self, order_number, product_type="Comida"):
        """Crear un pedido de muestra"""
        try:
            # Obtener un repartidor aleatorio
            self.cursor.execute("SELECT id FROM delivery_agents ORDER BY RANDOM() LIMIT 1")
            agent_result = self.cursor.fetchone()
            agent_id = agent_result['id'] if agent_result else None
            
            # Crear pedido
            self.cursor.execute("""
                INSERT INTO orders (order_number, status, pickup_address, delivery_address,
                                  distance_km, product_type, priority_level, delivery_agent_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (order_number, "pending", "Dirección de recogida", "Dirección de entrega",
                  round(random.uniform(1.0, 10.0), 2), product_type, "normal", agent_id))
            
            order_id = self.cursor.fetchone()['id']
            
            # Crear evento de creación
            self.cursor.execute("""
                INSERT INTO order_events (order_id, event_type, screen_coordinates, raw_data)
                VALUES (%s, %s, %s, %s)
            """, (order_id, "order_created", "x:100,y:100", json.dumps({"source": "smartagent"})))
            
            # Crear mensaje de confirmación
            self.cursor.execute("""
                INSERT INTO whatsapp_messages (order_id, sender, message)
                VALUES (%s, %s, %s)
            """, (order_id, "sistema", f"Pedido {order_number} creado automáticamente por SmartAgent"))
            
            self.conn.commit()
            logging.info(f"📦 Pedido de muestra creado: {order_number} (ID: {order_id})")
            return order_id
            
        except Exception as e:
            logging.error(f"❌ Error creando pedido de muestra: {e}")
            self.conn.rollback()
            return None
    
    def get_orders_summary(self):
        """Obtener resumen de pedidos"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_orders,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders
                FROM orders
            """)
            
            return self.cursor.fetchone()
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo resumen de pedidos: {e}")
            return None

class SmartAgentOrders:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.db = DatabaseManager(DATABASE_URL)
        self.setup_driver()
        self.setup_database()
    
    def setup_database(self):
        """Configurar conexión a la base de datos"""
        if not self.db.connect():
            logging.error("❌ No se pudo conectar a la base de datos")
            raise Exception("Error de conexión a la base de datos")
    
    def setup_driver(self):
        """Configurar el navegador Chrome"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                logging.info("✅ ChromeDriver automático instalado")
            except ImportError:
                service = Service(CHROMEDRIVER_PATH)
                logging.info("⚠️ Usando ChromeDriver manual")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            logging.info("✅ Navegador configurado correctamente")
            
        except Exception as e:
            logging.error(f"❌ Error configurando navegador: {e}")
            raise
    
    def login(self):
        """Realizar login en el admin panel"""
        try:
            logging.info("🔐 Iniciando proceso de login...")
            self.driver.get(LOGIN_URL)
            time.sleep(5)
            
            # Buscar campos de login
            username_field = None
            password_field = None
            
            # Estrategias para username
            selectors_username = [
                (By.NAME, "uid"),
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]
            
            for selector_type, selector_value in selectors_username:
                try:
                    username_field = self.driver.find_element(selector_type, selector_value)
                    logging.info(f"✅ Campo username encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            # Estrategias para password
            selectors_password = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]
            
            for selector_type, selector_value in selectors_password:
                try:
                    password_field = self.driver.find_element(selector_type, selector_value)
                    logging.info(f"✅ Campo password encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not username_field or not password_field:
                logging.error("❌ No se pudieron encontrar los campos de login")
                return False
            
            # Ingresar credenciales
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            logging.info("✅ Credenciales ingresadas")
            
            # Buscar botón de login
            login_button = None
            button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.CSS_SELECTOR, "button"),
                (By.XPATH, "//button")
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    logging.info(f"✅ Botón de login encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not login_button:
                logging.error("❌ No se pudo encontrar el botón de login")
                return False
            
            # Hacer clic en el botón
            login_button.click()
            logging.info("✅ Botón de login clickeado")
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            logging.info(f"📍 URL actual después del login: {current_url}")
            
            if "login" not in current_url.lower() and "auth" not in current_url.lower():
                logging.info("✅ Login exitoso")
                return True
            else:
                logging.error("❌ Login fallido - aún en página de login")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error durante el login: {e}")
            return False
    
    def extract_page_data(self, url):
        """Extraer datos de la página actual"""
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            datos = {
                "url": url,
                "titulo": soup.title.string if soup.title else "",
                "timestamp": datetime.now().isoformat(),
                "botones": [],
                "inputs": [],
                "links": [],
                "forms": [],
                "tables": []
            }
            
            # Extraer botones
            for button in soup.find_all("button"):
                btn_text = button.get_text(strip=True)
                btn_type = button.get("type", "")
                btn_id = button.get("id", "")
                datos["botones"].append({
                    "texto": btn_text,
                    "tipo": btn_type,
                    "id": btn_id
                })
            
            # Extraer inputs
            for input_elem in soup.find_all("input"):
                input_data = {
                    "tipo": input_elem.get("type", "text"),
                    "nombre": input_elem.get("name", ""),
                    "id": input_elem.get("id", ""),
                    "placeholder": input_elem.get("placeholder", "")
                }
                datos["inputs"].append(input_data)
            
            # Extraer links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(self.driver.current_url, href)
                if START_URL in full_url and full_url not in visited_urls:
                    datos["links"].append({
                        "url": full_url,
                        "texto": link.get_text(strip=True)
                    })
                    if full_url not in cola:
                        cola.append(full_url)
            
            # Extraer formularios
            for form in soup.find_all("form"):
                form_data = {
                    "action": form.get("action", ""),
                    "method": form.get("method", "get"),
                    "id": form.get("id", "")
                }
                datos["forms"].append(form_data)
            
            # Extraer tablas
            for table in soup.find_all("table"):
                table_data = {
                    "id": table.get("id", ""),
                    "class": table.get("class", []),
                    "rows": len(table.find_all("tr"))
                }
                datos["tables"].append(table_data)
            
            return datos
            
        except Exception as e:
            logging.error(f"❌ Error extrayendo datos de {url}: {e}")
            return None
    
    def explore_page(self, url):
        """Explorar una página específica"""
        try:
            logging.info(f"🔍 Explorando: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Esperar a que la página cargue
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            datos = self.extract_page_data(url)
            if datos:
                with lock:
                    estructura[url] = datos
                    visited_urls.add(url)
                
                # Guardar en base de datos
                titulo = datos.get('titulo', '')
                if self.db.insert_pagina(url, titulo, datos):
                    logging.info(f"✅ Datos extraídos y guardados en DB: {url}")
                else:
                    logging.warning(f"⚠️ Datos extraídos pero error guardando en DB: {url}")
                
                # Crear pedido de muestra ocasionalmente
                if random.random() < 0.1:  # 10% de probabilidad
                    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                    self.db.create_sample_order(order_number)
            
        except Exception as e:
            logging.error(f"❌ Error explorando {url}: {e}")
    
    def run_exploration(self):
        """Ejecutar la exploración completa"""
        try:
            # Realizar login primero
            if not self.login():
                logging.error("❌ No se pudo realizar el login. Deteniendo exploración.")
                return
            
            logging.info("🚀 Iniciando exploración del admin panel...")
            
            while cola:
                url = cola.pop(0)
                if url in visited_urls:
                    continue
                
                self.explore_page(url)
                
                # Pausa entre páginas para no sobrecargar el servidor
                time.sleep(2)
                
        except KeyboardInterrupt:
            logging.info("⛔ Exploración detenida por el usuario.")
        except Exception as e:
            logging.error(f"❌ Error durante la exploración: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()
            logging.info("✅ Navegador cerrado correctamente.")
        
        if self.db:
            self.db.disconnect()
            logging.info("✅ Conexión a base de datos cerrada.")

def main():
    """Función principal"""
    logging.info("🤖 Iniciando SmartAgent Orders - Sistema Integrado")
    
    try:
        # Crear y ejecutar el agente
        agent = SmartAgentOrders()
        
        # Mostrar resumen de pedidos antes de empezar
        summary = agent.db.get_orders_summary()
        if summary:
            logging.info(f"📊 Estado inicial - Pedidos: {summary['total_orders']}, Pendientes: {summary['pending_orders']}")
        
        agent.run_exploration()
        
        # Mostrar resumen final
        summary = agent.db.get_orders_summary()
        if summary:
            logging.info(f"📊 Estado final - Pedidos: {summary['total_orders']}, Pendientes: {summary['pending_orders']}")
        
    except Exception as e:
        logging.error(f"❌ Error en SmartAgent Orders: {e}")
    finally:
        logging.info("✅ SmartAgent Orders finalizado")

if __name__ == "__main__":
    main() 