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

# Configuración del proyecto
CHROMEDRIVER_PATH = "chromedriver.exe"  # Actualizado para Windows
START_URL = "https://admin.besmartdelivery.mx/"
LOGIN_URL = "https://admin.besmartdelivery.mx/"
PROFILE_DIR = f"./besmart_profile_{int(time.time())}"  # Directorio único con timestamp
JSON_PATH = "estructura.json"
TXT_PATH = "flujo.txt"
LOG_PATH = "logs/smartagent.log"

# Configuración de la base de datos
DATABASE_URL = "postgresql://***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***/***DB_OCULTA***?sslmode=require&channel_binding=require"

# Credenciales del admin panel
ADMIN_USERNAME = "manus"
ADMIN_PASSWORD = "***CONTRASEÑA_OCULTA***"

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

estructura = {}
visited_urls = set()
cola = [START_URL]
lock = threading.Lock()

def cargar_datos_previos():
    """Cargar datos de ejecuciones anteriores si existen"""
    global estructura, visited_urls, cola
    
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                estructura = json.load(f)
            logging.info(f"✅ Datos previos cargados: {len(estructura)} páginas")
            
            # Recuperar URLs visitadas
            visited_urls = set(estructura.keys())
            
            # Reconstruir cola con nuevos links encontrados
            for url, datos in estructura.items():
                for link in datos.get("links", []):
                    if isinstance(link, dict):
                        link_url = link.get("url", "")
                    else:
                        link_url = link
                    if link_url and link_url not in visited_urls and link_url not in cola:
                        cola.append(link_url)
            
            logging.info(f"✅ Cola reconstruida: {len(cola)} URLs pendientes")
            return True
        except Exception as e:
            logging.error(f"❌ Error cargando datos previos: {e}")
            return False
    return False

def guardar_datos_finales():
    """Guardar datos finales cuando se cierra el script"""
    try:
        with lock:
            # Guardar JSON final
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(estructura, f, indent=2, ensure_ascii=False)
            
            # Guardar backup final
            backup_final = f"backup_final_{int(time.time())}.json"
            with open(backup_final, "w", encoding="utf-8") as f:
                json.dump(estructura, f, indent=2, ensure_ascii=False)
            
            # Crear reporte final
            with open("reporte_final.txt", "w", encoding="utf-8") as f:
                f.write(f"=== REPORTE FINAL SMARTAGENT ===\n")
                f.write(f"Fecha de finalización: {datetime.now()}\n")
                f.write(f"Total de páginas exploradas: {len(estructura)}\n")
                f.write(f"URLs visitadas: {len(visited_urls)}\n")
                f.write(f"URLs pendientes: {len(cola)}\n\n")
                
                f.write("RESUMEN DE EXPLORACIÓN:\n")
                f.write("=" * 50 + "\n")
                
                total_botones = sum(len(datos.get("botones", [])) for datos in estructura.values())
                total_inputs = sum(len(datos.get("inputs", [])) for datos in estructura.values())
                total_links = sum(len(datos.get("links", [])) for datos in estructura.values())
                total_forms = sum(len(datos.get("forms", [])) for datos in estructura.values())
                total_tables = sum(len(datos.get("tables", [])) for datos in estructura.values())
                
                f.write(f"Total botones encontrados: {total_botones}\n")
                f.write(f"Total inputs encontrados: {total_inputs}\n")
                f.write(f"Total links encontrados: {total_links}\n")
                f.write(f"Total formularios encontrados: {total_forms}\n")
                f.write(f"Total tablas encontradas: {total_tables}\n\n")
                
                f.write("PÁGINAS EXPLORADAS:\n")
                f.write("=" * 50 + "\n")
                for i, (url, datos) in enumerate(estructura.items(), 1):
                    f.write(f"{i}. {url}\n")
                    f.write(f"   Título: {datos.get('titulo', '')}\n")
                    f.write(f"   Botones: {len(datos.get('botones', []))}\n")
                    f.write(f"   Inputs: {len(datos.get('inputs', []))}\n")
                    f.write(f"   Links: {len(datos.get('links', []))}\n\n")
            
            logging.info(f"💾 Datos finales guardados - {len(estructura)} páginas exploradas")
            
    except Exception as e:
        logging.error(f"❌ Error guardando datos finales: {e}")

def signal_handler(signum, frame):
    """Manejador de señales para guardar datos al cerrar"""
    logging.info(f"🛑 Señal recibida ({signum}). Guardando datos...")
    guardar_datos_finales()
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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

class SmartAgent:
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
        """Configurar el navegador Chrome con opciones optimizadas"""
        try:
            options = Options()
            # Configuración básica sin directorio de usuario para evitar conflictos
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Intentar usar chromedriver automático si está disponible
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
            time.sleep(5)  # Más tiempo para cargar
            
            # Tomar screenshot para debug
            self.driver.save_screenshot("login_page.png")
            logging.info("📸 Screenshot guardado como login_page.png")
            
            # Obtener el HTML de la página para debug
            page_source = self.driver.page_source
            with open("login_page.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            logging.info("📄 HTML guardado como login_page.html")
            
            # Buscar campos de login con múltiples estrategias
            username_field = None
            password_field = None
            
            # Estrategias para username
            selectors_username = [
                (By.NAME, "uid"),  # Campo real encontrado
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.NAME, "user"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[placeholder*='usuario']"),
                (By.CSS_SELECTOR, "input[placeholder*='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='Username']"),
                (By.XPATH, "//input[@type='text']")
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
                (By.NAME, "pass"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
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
                logging.info("🔍 Elementos de input encontrados:")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for i, inp in enumerate(inputs):
                    logging.info(f"  Input {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
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
                (By.XPATH, "//button[contains(text(), 'Iniciar')]"),
                (By.XPATH, "//button[contains(text(), 'Entrar')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
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

def guardar_periodicamente():
    """Guardar datos periódicamente en archivos"""
    while True:
        time.sleep(10)  # Guardar cada 10 segundos para mayor seguridad
        try:
            with lock:
                # Guardar JSON principal
                with open(JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(estructura, f, indent=2, ensure_ascii=False)
                
                # Guardar backup con timestamp
                backup_path = f"backup_estructura_{int(time.time())}.json"
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(estructura, f, indent=2, ensure_ascii=False)
                
                # Guardar TXT legible
                with open(TXT_PATH, "w", encoding="utf-8") as f:
                    f.write(f"=== REPORTE SMARTAGENT - {datetime.now()} ===\n")
                    f.write(f"Páginas exploradas: {len(estructura)}\n")
                    f.write(f"URLs pendientes: {len(cola)}\n")
                    f.write(f"URLs visitadas: {len(visited_urls)}\n\n")
                    
                    for url, datos in estructura.items():
                        f.write(f"\n{'='*50}\n")
                        f.write(f"URL: {url}\n")
                        f.write(f"Título: {datos.get('titulo', '')}\n")
                        f.write(f"Timestamp: {datos.get('timestamp', '')}\n")
                        
                        f.write(f"\nBotones ({len(datos['botones'])}):\n")
                        for btn in datos["botones"]:
                            f.write(f"  - {btn['texto']} (tipo: {btn['tipo']}, id: {btn['id']})\n")
                        
                        f.write(f"\nInputs ({len(datos['inputs'])}):\n")
                        for inp in datos["inputs"]:
                            f.write(f"  - {inp['tipo']} - {inp['nombre']} (id: {inp['id']})\n")
                        
                        f.write(f"\nLinks ({len(datos['links'])}):\n")
                        for link in datos["links"]:
                            f.write(f"  - {link['texto']}: {link['url']}\n")
                        
                        f.write(f"\nFormularios ({len(datos['forms'])}):\n")
                        for form in datos["forms"]:
                            f.write(f"  - {form['method']} -> {form['action']}\n")
                        
                        f.write(f"\nTablas ({len(datos['tables'])}):\n")
                        for table in datos["tables"]:
                            f.write(f"  - {table['id']}: {table['rows']} filas\n")
                
                # Guardar resumen de progreso
                with open("progreso.txt", "w", encoding="utf-8") as f:
                    f.write(f"=== PROGRESO SMARTAGENT ===\n")
                    f.write(f"Última actualización: {datetime.now()}\n")
                    f.write(f"Páginas exploradas: {len(estructura)}\n")
                    f.write(f"URLs pendientes: {len(cola)}\n")
                    f.write(f"URLs visitadas: {len(visited_urls)}\n\n")
                    f.write("Últimas 5 páginas exploradas:\n")
                    for i, url in enumerate(list(estructura.keys())[-5:], 1):
                        f.write(f"{i}. {url}\n")
                    f.write(f"\nPróximas URLs a explorar:\n")
                    for i, url in enumerate(cola[:5], 1):
                        f.write(f"{i}. {url}\n")
                
                # Mostrar estadísticas de la base de datos
                try:
                    db = DatabaseManager(DATABASE_URL)
                    if db.connect():
                        stats = db.get_estadisticas()
                        if stats:
                            logging.info(f"💾 Guardado automático realizado - {len(estructura)} páginas exploradas")
                            logging.info(f"📊 DB Stats - Páginas: {stats['total_paginas']}, Botones: {stats['total_botones']}, Inputs: {stats['total_inputs']}")
                        db.disconnect()
                except Exception as e:
                    logging.error(f"❌ Error obteniendo estadísticas de DB: {e}")
                    logging.info(f"💾 Guardado automático realizado - {len(estructura)} páginas exploradas")
                
        except Exception as e:
            logging.error(f"❌ Error guardando datos: {e}")

def main():
    """Función principal"""
    logging.info("🤖 Iniciando SmartAgent para BeSmart Delivery Admin Panel")
    
    # Cargar datos previos si existen
    datos_cargados = cargar_datos_previos()
    if datos_cargados:
        logging.info("🔄 Continuando exploración desde punto anterior")
    else:
        logging.info("🚀 Iniciando nueva exploración")
    
    # Lanzar el guardado en hilo separado
    save_thread = threading.Thread(target=guardar_periodicamente, daemon=True)
    save_thread.start()
    
    try:
        # Crear y ejecutar el agente
        agent = SmartAgent()
        agent.run_exploration()
    except KeyboardInterrupt:
        logging.info("⛔ Exploración interrumpida por el usuario")
    except Exception as e:
        logging.error(f"❌ Error durante la exploración: {e}")
    finally:
        guardar_datos_finales()
        logging.info("✅ SmartAgent finalizado")

if __name__ == "__main__":
    main()