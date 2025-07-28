#!/usr/bin/env python3
"""
Debug Rápido - Para ver qué hay en la página después del login
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configuración
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks"
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "***CONTRASEÑA_OCULTA***"

class QuickDebug:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configurar Chrome WebDriver"""
        try:
            print("🚀 Configurando Chrome WebDriver...")
            
            # Configurar opciones de Chrome
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Crear el driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Configurar timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            print("✅ Chrome WebDriver configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando Chrome WebDriver: {e}")
            raise
    
    def login(self):
        """Iniciar sesión"""
        try:
            print("🔐 Iniciando sesión...")
            
            # Ir a la página de login
            self.driver.get(LOGIN_URL)
            time.sleep(2)
            
            # Esperar a que aparezcan los campos de login
            wait = WebDriverWait(self.driver, 10)
            
            # Buscar campo de usuario
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "uid")))
            print("✅ Campo usuario encontrado")
            
            # Limpiar y llenar campo de usuario
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            
            # Buscar campo de contraseña
            password_field = self.driver.find_element(By.NAME, "password")
            print("✅ Campo contraseña encontrado")
            
            # Limpiar y llenar campo de contraseña
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Presionar Enter para hacer login
            password_field.send_keys(Keys.RETURN)
            print("✅ Login con Enter")
            
            # Esperar a que se complete el login
            time.sleep(5)
            
            print("✅ Login exitoso")
            return True
            
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def go_to_tasks_page(self):
        """Ir a la página de tareas"""
        try:
            print("📄 Navegando a la página de tareas...")
            self.driver.get(TASKS_URL)
            
            # Esperar a que se cargue la página completamente
            print("⏳ Esperando a que se cargue la página...")
            time.sleep(15)
            
            print("✅ Página de tareas cargada")
            return True
        except Exception as e:
            print(f"❌ Error navegando a tareas: {e}")
            return False
    
    def debug_page_content(self):
        """Debug del contenido de la página"""
        try:
            print("\n🔍 DEBUG DEL CONTENIDO DE LA PÁGINA")
            print("=" * 50)
            
            # Mostrar URL actual
            print(f"📍 URL actual: {self.driver.current_url}")
            
            # Mostrar título de la página
            print(f"📄 Título: {self.driver.title}")
            
            # Contar elementos por tipo
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            divs = self.driver.find_elements(By.TAG_NAME, "div")
            spans = self.driver.find_elements(By.TAG_NAME, "span")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            print(f"📊 Elementos encontrados:")
            print(f"  - Botones: {len(buttons)}")
            print(f"  - Divs: {len(divs)}")
            print(f"  - Spans: {len(spans)}")
            print(f"  - Inputs: {len(inputs)}")
            
            # Buscar elementos con clase "btn"
            btn_elements = self.driver.find_elements(By.CLASS_NAME, "btn")
            print(f"  - Elementos con clase 'btn': {len(btn_elements)}")
            
            # Buscar elementos que contengan "Active"
            active_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Active')]")
            print(f"  - Elementos con 'Active': {len(active_elements)}")
            
            # Buscar elementos que contengan "orders"
            orders_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'orders')]")
            print(f"  - Elementos con 'orders': {len(orders_elements)}")
            
            # Mostrar texto de todos los botones
            print("\n🔘 TODOS LOS BOTONES:")
            for i, button in enumerate(buttons):
                try:
                    text = button.text.strip()
                    button_type = button.get_attribute("type")
                    button_class = button.get_attribute("class")
                    print(f"  Botón {i+1}: Texto='{text}', Tipo='{button_type}', Clase='{button_class}'")
                except:
                    print(f"  Botón {i+1}: Error al obtener información")
            
            # Mostrar texto de los primeros 10 divs
            print("\n📦 PRIMEROS 10 DIVS:")
            for i, div in enumerate(divs[:10]):
                try:
                    text = div.text.strip()
                    div_class = div.get_attribute("class")
                    if text:  # Solo mostrar divs con texto
                        print(f"  Div {i+1}: Texto='{text[:100]}...', Clase='{div_class}'")
                except:
                    print(f"  Div {i+1}: Error al obtener información")
            
            # Mostrar texto de todos los spans
            print("\n🏷️ TODOS LOS SPANS:")
            for i, span in enumerate(spans):
                try:
                    text = span.text.strip()
                    span_class = span.get_attribute("class")
                    if text:  # Solo mostrar spans con texto
                        print(f"  Span {i+1}: Texto='{text}', Clase='{span_class}'")
                except:
                    print(f"  Span {i+1}: Error al obtener información")
            
            # Buscar elementos con clases específicas
            print("\n🎯 ELEMENTOS CON CLASES ESPECÍFICAS:")
            class_names = ["btn", "button", "label", "value", "orders", "active", "task", "dashboard", "nav", "menu"]
            for class_name in class_names:
                elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                if len(elements) > 0:
                    print(f"  - Clase '{class_name}': {len(elements)} elementos")
                    # Mostrar texto del primer elemento
                    try:
                        first_text = elements[0].text.strip()
                        if first_text:
                            print(f"    Primer elemento: '{first_text[:50]}...'")
                    except:
                        print(f"    Primer elemento: Error al obtener texto")
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
    
    def run_debug(self):
        """Ejecutar debug completo"""
        try:
            print("🔬 DEBUG RÁPIDO DEL MONITOR DE ÓRDENES")
            print("=" * 50)
            
            # Login inicial
            if not self.login():
                print("❌ No se pudo hacer login")
                return
            
            # Ir a la página de tareas
            if not self.go_to_tasks_page():
                print("❌ No se pudo ir a la página de tareas")
                return
            
            # Ejecutar debug
            self.debug_page_content()
            
            # Esperar un poco para que el usuario pueda ver los resultados
            print("\n⏰ Esperando 30 segundos para que puedas revisar los resultados...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
        finally:
            self.close_driver()
    
    def close_driver(self):
        """Cerrar el WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver cerrado")

def main():
    debug = QuickDebug()
    debug.run_debug()

if __name__ == "__main__":
    main() 