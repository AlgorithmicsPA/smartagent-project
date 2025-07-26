#!/usr/bin/env python3
"""
Monitor de Diagnóstico - Para entender qué está pasando en la página
"""
import time
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

class DiagnosticMonitor:
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
            
            # Intentar múltiples estrategias para el login
            login_success = False
            
            # Estrategia 1: Buscar botón de submit
            try:
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                print("✅ Login con botón submit")
                login_success = True
            except:
                print("⚠️ Botón submit no encontrado")
            
            # Estrategia 2: Presionar Enter en el campo de contraseña
            if not login_success:
                try:
                    password_field.send_keys(Keys.RETURN)
                    print("✅ Login con Enter")
                    login_success = True
                except:
                    print("⚠️ Enter no funcionó")
            
            if not login_success:
                print("❌ No se pudo realizar el login")
                return False
            
            # Esperar a que se complete el login
            time.sleep(3)
            
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
            time.sleep(3)
            print("✅ Página de tareas cargada")
            return True
        except Exception as e:
            print(f"❌ Error navegando a tareas: {e}")
            return False
    
    def diagnose_page(self):
        """Diagnosticar la página actual"""
        try:
            print("\n🔍 DIAGNÓSTICO DE LA PÁGINA")
            print("=" * 50)
            
            # Mostrar URL actual
            print(f"📍 URL actual: {self.driver.current_url}")
            
            # Mostrar título de la página
            print(f"📄 Título: {self.driver.title}")
            
            # Buscar todos los botones en la página
            print("\n🔘 BUSCANDO BOTONES:")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"📊 Total de botones encontrados: {len(buttons)}")
            
            for i, button in enumerate(buttons[:10]):  # Mostrar solo los primeros 10
                try:
                    text = button.text.strip()
                    button_type = button.get_attribute("type")
                    button_class = button.get_attribute("class")
                    print(f"  Botón {i+1}: Texto='{text}', Tipo='{button_type}', Clase='{button_class}'")
                except:
                    print(f"  Botón {i+1}: Error al obtener información")
            
            # Buscar elementos con clase "btn"
            print("\n🎯 BUSCANDO ELEMENTOS CON CLASE 'btn':")
            btn_elements = self.driver.find_elements(By.CLASS_NAME, "btn")
            print(f"📊 Total de elementos con clase 'btn': {len(btn_elements)}")
            
            for i, btn in enumerate(btn_elements[:10]):  # Mostrar solo los primeros 10
                try:
                    text = btn.text.strip()
                    btn_class = btn.get_attribute("class")
                    print(f"  Btn {i+1}: Texto='{text}', Clase='{btn_class}'")
                except:
                    print(f"  Btn {i+1}: Error al obtener información")
            
            # Buscar elementos que contengan "Active orders"
            print("\n🔍 BUSCANDO ELEMENTOS CON 'Active orders':")
            active_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Active orders')]")
            print(f"📊 Total de elementos con 'Active orders': {len(active_elements)}")
            
            for i, elem in enumerate(active_elements):
                try:
                    text = elem.text.strip()
                    tag_name = elem.tag_name
                    elem_class = elem.get_attribute("class")
                    print(f"  Elemento {i+1}: Tag='{tag_name}', Texto='{text}', Clase='{elem_class}'")
                except:
                    print(f"  Elemento {i+1}: Error al obtener información")
            
            # Buscar elementos con clase "label"
            print("\n🏷️ BUSCANDO ELEMENTOS CON CLASE 'label':")
            label_elements = self.driver.find_elements(By.CLASS_NAME, "label")
            print(f"📊 Total de elementos con clase 'label': {len(label_elements)}")
            
            for i, label in enumerate(label_elements[:10]):  # Mostrar solo los primeros 10
                try:
                    text = label.text.strip()
                    print(f"  Label {i+1}: Texto='{text}'")
                except:
                    print(f"  Label {i+1}: Error al obtener información")
            
            # Buscar elementos con clase "value"
            print("\n💎 BUSCANDO ELEMENTOS CON CLASE 'value':")
            value_elements = self.driver.find_elements(By.CLASS_NAME, "value")
            print(f"📊 Total de elementos con clase 'value': {len(value_elements)}")
            
            for i, value in enumerate(value_elements[:10]):  # Mostrar solo los primeros 10
                try:
                    text = value.text.strip()
                    print(f"  Value {i+1}: Texto='{text}'")
                except:
                    print(f"  Value {i+1}: Error al obtener información")
            
            # Mostrar el HTML de la página (primeros 1000 caracteres)
            print("\n📄 HTML DE LA PÁGINA (primeros 1000 caracteres):")
            page_source = self.driver.page_source
            print(page_source[:1000] + "..." if len(page_source) > 1000 else page_source)
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
    
    def run_diagnostic(self):
        """Ejecutar diagnóstico completo"""
        try:
            print("🔬 DIAGNÓSTICO DEL MONITOR DE ÓRDENES")
            print("=" * 50)
            
            # Login inicial
            if not self.login():
                print("❌ No se pudo hacer login")
                return
            
            # Ir a la página de tareas
            if not self.go_to_tasks_page():
                print("❌ No se pudo ir a la página de tareas")
                return
            
            # Ejecutar diagnóstico
            self.diagnose_page()
            
            # Esperar un poco para que el usuario pueda ver los resultados
            print("\n⏰ Esperando 30 segundos para que puedas revisar los resultados...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
        finally:
            self.close_driver()
    
    def close_driver(self):
        """Cerrar el WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver cerrado")

def main():
    monitor = DiagnosticMonitor()
    monitor.run_diagnostic()

if __name__ == "__main__":
    main() 