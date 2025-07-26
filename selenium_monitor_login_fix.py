#!/usr/bin/env python3
"""
Monitor de Pedidos con Selenium - Versión con Fix de Login
Versión que verifica el login y usa diferentes estrategias
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

class SeleniumMonitorLoginFix:
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
    
    def check_if_logged_in(self):
        """Verificar si el usuario está logueado"""
        try:
            # Buscar elementos que indiquen que estamos logueados
            login_form = self.driver.find_elements(By.XPATH, "//form[contains(@action, 'login') or contains(@class, 'login')]")
            login_button = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Login')]")
            
            # Si encontramos el formulario de login, no estamos logueados
            if len(login_form) > 0 or len(login_button) > 0:
                return False
            
            # Buscar elementos que indiquen que estamos en el dashboard
            dashboard_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Admin') or contains(text(), 'Tasks')]")
            if len(dashboard_elements) > 0:
                return True
            
            # Verificar la URL
            current_url = self.driver.current_url.lower()
            if "login" not in current_url and ("admin" in current_url or "dashboard" in current_url or "tasks" in current_url):
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error verificando login: {e}")
            return False
    
    def login(self):
        """Iniciar sesión con verificación"""
        try:
            print("🔐 Iniciando sesión...")
            
            # Ir a la página de login
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            
            # Verificar si ya estamos logueados
            if self.check_if_logged_in():
                print("✅ Ya estamos logueados")
                return True
            
            # Esperar a que aparezcan los campos de login
            wait = WebDriverWait(self.driver, 10)
            
            # Buscar campo de usuario
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "uid")))
            print("✅ Campo usuario encontrado")
            
            # Limpiar y llenar campo de usuario
            username_field.clear()
            time.sleep(1)
            username_field.send_keys(ADMIN_USERNAME)
            time.sleep(1)
            
            # Buscar campo de contraseña
            password_field = self.driver.find_element(By.NAME, "password")
            print("✅ Campo contraseña encontrado")
            
            # Limpiar y llenar campo de contraseña
            password_field.clear()
            time.sleep(1)
            password_field.send_keys(ADMIN_PASSWORD)
            time.sleep(1)
            
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
            
            # Estrategia 3: Buscar cualquier botón en el formulario
            if not login_success:
                try:
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    buttons = form.find_elements(By.TAG_NAME, "button")
                    if buttons:
                        buttons[0].click()
                        print("✅ Login con primer botón del formulario")
                        login_success = True
                except:
                    print("⚠️ No se encontraron botones en el formulario")
            
            if not login_success:
                print("❌ No se pudo realizar el login con ninguna estrategia")
                return False
            
            # Esperar a que se complete el login
            print("⏳ Esperando a que se complete el login...")
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            max_attempts = 10
            for attempt in range(max_attempts):
                if self.check_if_logged_in():
                    print("✅ Login exitoso")
                    return True
                else:
                    print(f"⚠️ Intento {attempt + 1}/{max_attempts}: Login no verificado, esperando...")
                    time.sleep(2)
            
            print("❌ Login no se pudo verificar después de múltiples intentos")
            return False
            
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
            time.sleep(10)
            
            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            if "tasks" in current_url.lower():
                print("✅ Página de tareas cargada")
                return True
            else:
                print(f"⚠️ URL actual: {current_url}")
                return False
                
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
            
            # Verificar si estamos logueados
            is_logged_in = self.check_if_logged_in()
            print(f"🔐 ¿Estamos logueados?: {is_logged_in}")
            
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
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
    
    def monitor_orders(self):
        """Monitorear órdenes continuamente"""
        try:
            print("🎯 MONITOR DE ÓRDENES CON SELENIUM - VERSIÓN LOGIN FIX")
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
    monitor = SeleniumMonitorLoginFix()
    monitor.monitor_orders()

if __name__ == "__main__":
    main() 