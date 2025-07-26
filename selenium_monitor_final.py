#!/usr/bin/env python3
"""
Monitor de Pedidos con Selenium - Versión Final
Versión con selectores flexibles y mejor manejo de errores
"""
import time
import hashlib
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuración
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks"
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "28ZwnPHQRC*H4BmfmEB-YHcC"

class SeleniumMonitorFinal:
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
        """Iniciar sesión con selectores flexibles"""
        try:
            print("🔐 Iniciando sesión...")
            
            # Ir a la página de login
            self.driver.get(LOGIN_URL)
            time.sleep(2)
            
            # Esperar a que aparezcan los campos de login
            wait = WebDriverWait(self.driver, 10)
            
            # Buscar campo de usuario con diferentes selectores
            username_field = None
            username_selectors = [
                (By.NAME, "uid"),
                (By.NAME, "username"),
                (By.NAME, "email"),
                (By.ID, "username"),
                (By.ID, "email"),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@placeholder*='user' or @placeholder*='email']")
            ]
            
            for selector_type, selector_value in username_selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    print(f"✅ Campo usuario encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not username_field:
                print("❌ No se pudo encontrar el campo de usuario")
                return False
            
            # Limpiar y llenar campo de usuario
            username_field.clear()
            username_field.send_keys(ADMIN_USERNAME)
            
            # Buscar campo de contraseña
            password_field = None
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.driver.find_element(selector_type, selector_value)
                    print(f"✅ Campo contraseña encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not password_field:
                print("❌ No se pudo encontrar el campo de contraseña")
                return False
            
            # Limpiar y llenar campo de contraseña
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Buscar botón de login con diferentes selectores
            login_button = None
            login_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//button[contains(text(), 'Entrar')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CLASS_NAME, "login-button"),
                (By.CLASS_NAME, "submit-button"),
                (By.XPATH, "//button[contains(@class, 'btn')]")
            ]
            
            for selector_type, selector_value in login_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    print(f"✅ Botón login encontrado con: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not login_button:
                print("❌ No se pudo encontrar el botón de login")
                # Intentar hacer clic en el campo de contraseña y presionar Enter
                try:
                    password_field.send_keys(webdriver.Keys.RETURN)
                    print("✅ Login intentado con Enter")
                except:
                    return False
            else:
                # Hacer clic en el botón de login
                login_button.click()
                print("✅ Botón de login presionado")
            
            # Esperar a que se complete el login
            time.sleep(3)
            
            # Verificar si el login fue exitoso
            if "admin" in self.driver.current_url.lower() or "dashboard" in self.driver.current_url.lower():
                print("✅ Login exitoso")
                return True
            else:
                print("⚠️ Login puede no haber sido exitoso, continuando...")
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
    
    def click_active_orders_button(self):
        """Hacer clic en el botón Active orders"""
        try:
            print("🎯 Buscando botón Active orders...")
            
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
                time.sleep(2)
                
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
            print("🎯 MONITOR DE ÓRDENES CON SELENIUM - VERSIÓN FINAL")
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
    monitor = SeleniumMonitorFinal()
    monitor.monitor_orders()

if __name__ == "__main__":
    main() 