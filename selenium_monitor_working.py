#!/usr/bin/env python3
"""
Monitor de Pedidos con Selenium - Versión Funcional
Versión que usa la implementación de login del smartagent_enhanced.py
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
ADMIN_PASSWORD = "***CONTRASEÑA_OCULTA***"

class SeleniumMonitorWorking:
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
        """Iniciar sesión usando la implementación del smartagent_enhanced.py"""
        try:
            print(f"🔐 Intentando login con usuario: {ADMIN_USERNAME}")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            
            # Guardar screenshot para debugging
            self.driver.save_screenshot("login_page.png")
            print("📸 Screenshot guardado como login_page.png")
            
            # Múltiples estrategias para encontrar elementos (copiado de smartagent_enhanced.py)
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
                (By.XPATH, "//input[@value='Login']"),
                (By.XPATH, "//button[@class='button login main']"),
                (By.CSS_SELECTOR, "button.button.login.main"),
                (By.XPATH, "//button[text()='Login']"),
                (By.XPATH, "//*[contains(@class, 'login')]"),
                (By.XPATH, "//*[contains(@class, 'button')]")
            ]
            
            # Buscar campo de usuario
            username_field = None
            for by, selector in selectors_username:
                try:
                    username_field = self.driver.find_element(by, selector)
                    print(f"✅ Campo de usuario encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                print("❌ No se pudo encontrar el campo de usuario")
                return False
            
            # Buscar campo de contraseña
            password_field = None
            for by, selector in selectors_password:
                try:
                    password_field = self.driver.find_element(by, selector)
                    print(f"✅ Campo de contraseña encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print("❌ No se pudo encontrar el campo de contraseña")
                return False
            
            # Buscar botón de login
            login_button = None
            for by, selector in selectors_login:
                try:
                    login_button = self.driver.find_element(by, selector)
                    print(f"✅ Botón de login encontrado con: {by} = {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                print("❌ No se pudo encontrar el botón de login")
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
            
            print("✅ Login exitoso")
            return True
            
        except Exception as e:
            print(f"❌ Error durante el login: {e}")
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
    
    def wait_for_content_to_load(self, max_wait=120):
        """Esperar a que se cargue el contenido dinámicamente"""
        print("⏳ Esperando a que se cargue el contenido...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
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
    
    def extract_orders(self):
        """Extraer órdenes de la tabla"""
        try:
            print("🔍 Extrayendo órdenes de la tabla...")
            
            # Buscar la tabla de órdenes
            wait = WebDriverWait(self.driver, 10)
            orders_table = wait.until(EC.presence_of_element_located((
                By.CLASS_NAME, "responsive-table"
            )))
            
            # Buscar filas de órdenes
            order_rows = orders_table.find_elements(By.CLASS_NAME, "orders-list-item")
            print(f"📊 Encontradas {len(order_rows)} órdenes en la tabla")
            
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
            
        except TimeoutException:
            print("⚠️ Tabla de órdenes no encontrada")
            return []
        except Exception as e:
            print(f"❌ Error extrayendo órdenes: {e}")
            return []
    
    def parse_order_row(self, row):
        """Parsear una fila de orden"""
        try:
            # Obtener todas las celdas
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 10:
                return None
            
            order_data = {
                'timestamp': datetime.now().isoformat(),
                'status': 'Desconocido'
            }
            
            # Columna 1: ID de orden
            if len(cells) > 0:
                try:
                    order_id_field = cells[0].find_element(By.CLASS_NAME, "order-id-field")
                    order_text = order_id_field.text.strip()
                    numbers = re.findall(r'\d+', order_text)
                    if numbers:
                        order_data['order_id'] = numbers[-1]
                except:
                    pass
            
            # Columna 2: Restaurante
            if len(cells) > 1:
                try:
                    vendor_field = cells[1].find_element(By.CLASS_NAME, "vendor-field")
                    vendor_link = vendor_field.find_element(By.CLASS_NAME, "link")
                    order_data['restaurant'] = vendor_link.text.strip()
                except:
                    pass
            
            # Columna 3: Cliente
            if len(cells) > 2:
                try:
                    customer_field = cells[2].find_element(By.CLASS_NAME, "customer-field")
                    customer_link = customer_field.find_element(By.CLASS_NAME, "link")
                    order_data['customer_name'] = customer_link.text.strip()
                except:
                    pass
            
            # Columna 4: Zona
            if len(cells) > 3:
                try:
                    zone_text = cells[3].text.strip()
                    if zone_text:
                        order_data['delivery_address'] = zone_text
                except:
                    pass
            
            # Columna 5: Total
            if len(cells) > 4:
                try:
                    price_span = cells[4].find_element(By.CLASS_NAME, "price")
                    price_text = price_span.text.strip()
                    numbers = re.findall(r'[\d,]+\.?\d*', price_text)
                    if numbers:
                        order_data['total_amount'] = numbers[0]
                except:
                    pass
            
            # Columna 6: Hora de creación
            if len(cells) > 5:
                try:
                    created_text = cells[5].text.strip()
                    if created_text:
                        order_data['created_at'] = created_text
                except:
                    pass
            
            # Columna 7: CT (Cooking time)
            if len(cells) > 6:
                try:
                    ct_text = cells[6].text.strip()
                    if ct_text:
                        order_data['cooking_time'] = ct_text
                except:
                    pass
            
            # Columna 8: DT (Delivery time)
            if len(cells) > 7:
                try:
                    dt_text = cells[7].text.strip()
                    if dt_text:
                        order_data['delivery_time'] = dt_text
                except:
                    pass
            
            # Columna 9: Rider
            if len(cells) > 8:
                try:
                    rider_text = cells[8].text.strip()
                    if rider_text:
                        order_data['rider'] = rider_text
                except:
                    pass
            
            # Estado basado en las clases de la fila
            row_classes = row.get_attribute("class")
            if 'processed' in row_classes:
                order_data['status'] = 'Procesado'
            elif 'inpreparation' in row_classes:
                order_data['status'] = 'En Preparación'
            elif 'readyforcollection' in row_classes:
                order_data['status'] = 'Listo para Recoger'
            elif 'ontheway' in row_classes:
                order_data['status'] = 'En Camino'
            elif 'atlocation' in row_classes:
                order_data['status'] = 'En Ubicación'
            else:
                order_data['status'] = 'Desconocido'
            
            return order_data
            
        except Exception as e:
            print(f"❌ Error parseando fila: {e}")
            return None
    
    def display_orders(self, orders):
        """Mostrar órdenes en consola"""
        if not orders:
            return
        
        print("\n" + "="*140)
        print("🚨 ¡NUEVAS ÓRDENES DETECTADAS! 🚨")
        print("="*140)
        print(f"{'ID':<8} {'Estado':<15} {'Restaurante':<25} {'Cliente':<20} {'Zona':<25} {'Total':<10} {'Hora':<8} {'CT':<8} {'DT':<8} {'Rider':<12}")
        print("-"*140)
        
        for order_data in orders:
            order_id = order_data.get('order_id', 'N/A')
            status = order_data.get('status', 'N/A')
            restaurant = order_data.get('restaurant', 'N/A')
            if len(restaurant) > 24:
                restaurant = restaurant[:24] + "..."
            customer = order_data.get('customer_name', 'N/A')
            if len(customer) > 19:
                customer = customer[:19] + "..."
            zone = order_data.get('delivery_address', 'N/A')
            if len(zone) > 24:
                zone = zone[:24] + "..."
            total = order_data.get('total_amount', 'N/A')
            created_at = order_data.get('created_at', 'N/A')
            cooking_time = order_data.get('cooking_time', 'N/A')
            delivery_time = order_data.get('delivery_time', 'N/A')
            rider = order_data.get('rider', 'N/A')
            if len(rider) > 11:
                rider = rider[:11] + "..."
            
            print(f"{order_id:<8} {status:<15} {restaurant:<25} {customer:<20} {zone:<25} {total:<10} {created_at:<8} {cooking_time:<8} {delivery_time:<8} {rider:<12}")
        
        print("-"*140)
        print(f"📊 Nuevas órdenes detectadas: {len(orders)}")
        print("="*140 + "\n")
    
    def monitor_orders(self):
        """Monitorear órdenes continuamente"""
        try:
            print("🎯 MONITOR DE ÓRDENES CON SELENIUM - VERSIÓN FUNCIONAL")
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
            
            check_interval = 10  # segundos
            
            while True:
                try:
                    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Verificando nuevas órdenes...")
                    
                    # Hacer clic en el botón Active orders
                    if self.click_active_orders_button():
                        # Extraer órdenes
                        new_orders = self.extract_orders()
                        
                        # Mostrar órdenes si hay nuevas
                        if new_orders:
                            self.display_orders(new_orders)
                        else:
                            print("ℹ️ No hay nuevas órdenes")
                    else:
                        print("⚠️ No se pudo activar el botón Active orders")
                    
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Esperando {check_interval} segundos...")
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Monitor detenido por el usuario")
                    break
                except Exception as e:
                    print(f"❌ Error en el monitoreo: {e}")
                    time.sleep(check_interval)
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        """Cerrar el WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver cerrado")

def main():
    monitor = SeleniumMonitorWorking()
    monitor.monitor_orders()

if __name__ == "__main__":
    main() 