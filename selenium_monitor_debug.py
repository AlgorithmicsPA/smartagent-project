#!/usr/bin/env python3
"""
Monitor de Pedidos con Selenium - Versión Debug
Versión que muestra información detallada sobre la carga de contenido
"""
import time
import hashlib
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuración
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks"
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "28ZwnPHQRC*H4BmfmEB-YHcC"

class SeleniumMonitorDebug:
    def __init__(self):
        self.driver = None
        self.known_orders = set()
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
            time.sleep(15)  # Aumentar el tiempo de espera
            
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
            
            # Mostrar texto de los primeros 5 botones
            print("\n🔘 PRIMEROS 5 BOTONES:")
            for i, button in enumerate(buttons[:5]):
                try:
                    text = button.text.strip()
                    button_type = button.get_attribute("type")
                    button_class = button.get_attribute("class")
                    print(f"  Botón {i+1}: Texto='{text}', Tipo='{button_type}', Clase='{button_class}'")
                except:
                    print(f"  Botón {i+1}: Error al obtener información")
            
            # Mostrar texto de los primeros 5 divs
            print("\n📦 PRIMEROS 5 DIVS:")
            for i, div in enumerate(divs[:5]):
                try:
                    text = div.text.strip()
                    div_class = div.get_attribute("class")
                    print(f"  Div {i+1}: Texto='{text[:50]}...', Clase='{div_class}'")
                except:
                    print(f"  Div {i+1}: Error al obtener información")
            
            # Mostrar texto de los primeros 5 spans
            print("\n🏷️ PRIMEROS 5 SPANS:")
            for i, span in enumerate(spans[:5]):
                try:
                    text = span.text.strip()
                    span_class = span.get_attribute("class")
                    print(f"  Span {i+1}: Texto='{text}', Clase='{span_class}'")
                except:
                    print(f"  Span {i+1}: Error al obtener información")
            
            # Buscar elementos con clases específicas
            print("\n🎯 ELEMENTOS CON CLASES ESPECÍFICAS:")
            class_names = ["btn", "button", "label", "value", "orders", "active", "task", "dashboard"]
            for class_name in class_names:
                elements = self.driver.find_elements(By.CLASS_NAME, class_name)
                if len(elements) > 0:
                    print(f"  - Clase '{class_name}': {len(elements)} elementos")
                    # Mostrar texto del primer elemento
                    try:
                        first_text = elements[0].text.strip()
                        print(f"    Primer elemento: '{first_text[:50]}...'")
                    except:
                        print(f"    Primer elemento: Error al obtener texto")
            
            # Mostrar el HTML de la página (primeros 2000 caracteres)
            print("\n📄 HTML DE LA PÁGINA (primeros 2000 caracteres):")
            page_source = self.driver.page_source
            print(page_source[:2000] + "..." if len(page_source) > 2000 else page_source)
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
    
    def wait_for_content_to_load(self, max_wait=120):
        """Esperar a que se cargue el contenido dinámicamente"""
        print("⏳ Esperando a que se cargue el contenido...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                # Hacer debug cada 10 segundos
                if int(time.time() - start_time) % 10 == 0:
                    self.debug_page_content()
                
                # Buscar elementos que indiquen que el contenido se ha cargado
                elements = self.driver.find_elements(By.CLASS_NAME, "btn")
                if len(elements) > 0:
                    print(f"✅ Contenido cargado - Encontrados {len(elements)} elementos con clase 'btn'")
                    return True
                
                # También buscar elementos con "Active orders"
                active_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Active orders')]")
                if len(active_elements) > 0:
                    print(f"✅ Contenido cargado - Encontrados {len(active_elements)} elementos con 'Active orders'")
                    return True
                
                # Buscar elementos con "Active"
                active_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Active')]")
                if len(active_elements) > 0:
                    print(f"✅ Contenido cargado - Encontrados {len(active_elements)} elementos con 'Active'")
                    return True
                
                # Esperar un poco más
                time.sleep(2)
                print("⏳ Esperando...")
                
            except Exception as e:
                print(f"⚠️ Error esperando contenido: {e}")
                time.sleep(2)
        
        print("⚠️ Tiempo de espera agotado para cargar contenido")
        return False
    
    def click_active_orders_button(self):
        """Hacer clic en el botón Active orders"""
        try:
            print("🎯 Buscando botón Active orders...")
            
            # Primero esperar a que se cargue el contenido
            if not self.wait_for_content_to_load():
                print("⚠️ No se pudo cargar el contenido")
                return False
            
            wait = WebDriverWait(self.driver, 10)
            
            # Buscar el botón Active orders con diferentes estrategias
            active_orders_button = None
            
            # Estrategia 1: Buscar por texto exacto
            try:
                active_orders_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//div[@class='btn']//span[@class='label'][contains(text(), 'Active orders')]/.."
                )))
            except:
                pass
            
            # Estrategia 2: Buscar por clase y contenido
            if not active_orders_button:
                try:
                    buttons = self.driver.find_elements(By.CLASS_NAME, "btn")
                    for button in buttons:
                        try:
                            label = button.find_element(By.CLASS_NAME, "label")
                            if "Active orders" in label.text:
                                active_orders_button = button
                                break
                        except:
                            continue
                except:
                    pass
            
            # Estrategia 3: Buscar por texto parcial
            if not active_orders_button:
                try:
                    active_orders_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Active orders')]")
                except:
                    pass
            
            # Estrategia 4: Buscar cualquier botón que contenga "Active"
            if not active_orders_button:
                try:
                    active_orders_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Active')]")
                except:
                    pass
            
            if active_orders_button:
                # Obtener el valor antes del clic
                try:
                    value_span = active_orders_button.find_element(By.CLASS_NAME, "value")
                    active_count = value_span.text
                    print(f"📊 Botón Active orders encontrado con {active_count} órdenes")
                except:
                    print("📊 Botón Active orders encontrado")
                
                # Hacer clic en el botón
                active_orders_button.click()
                print("✅ Botón Active orders activado")
                
                # Esperar a que se cargue la tabla
                time.sleep(3)
                
                return True
            else:
                print("⚠️ Botón Active orders no encontrado")
                return False
            
        except Exception as e:
            print(f"❌ Error activando botón: {e}")
            return False
    
    def monitor_orders(self):
        """Monitorear órdenes continuamente"""
        try:
            print("🎯 MONITOR DE ÓRDENES CON SELENIUM - VERSIÓN DEBUG")
            print("=" * 50)
            print("💡 Presiona Ctrl+C para detener")
            print("=" * 50)
            
            # Login inicial
            if not self.login():
                print("❌ No se pudo hacer login")
                return
            
            # Ir a la página de tareas
            if not self.go_to_tasks_page():
                print("❌ No se pudo ir a la página de tareas")
                return
            
            # Hacer debug inicial
            self.debug_page_content()
            
            # Intentar hacer clic en el botón Active orders
            if self.click_active_orders_button():
                print("✅ Botón Active orders activado exitosamente")
            else:
                print("❌ No se pudo activar el botón Active orders")
            
            # Esperar un poco para que el usuario pueda ver los resultados
            print("\n⏰ Esperando 60 segundos para que puedas revisar los resultados...")
            time.sleep(60)
            
        except Exception as e:
            print(f"❌ Error en el monitoreo: {e}")
        finally:
            self.close_driver()
    
    def close_driver(self):
        """Cerrar el WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver cerrado")

def main():
    monitor = SeleniumMonitorDebug()
    monitor.monitor_orders()

if __name__ == "__main__":
    main() 