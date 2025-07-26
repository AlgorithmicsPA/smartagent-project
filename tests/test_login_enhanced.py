#!/usr/bin/env python3
"""
Test de Login Mejorado para SmartAgent
Prueba múltiples estrategias de detección de elementos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(project_root / "config" / ".env")

# Configuración
LOGIN_URL = os.getenv("LOGIN_URL", "https://admin.besmartdelivery.mx/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "federico")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "28ZwnPHQRC*H4BmfmEB-YHcC")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Configurar ChromeDriver"""
    try:
        chrome_path = ChromeDriverManager().install()
        service = Service(chrome_path)
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("✅ ChromeDriver configurado")
        return driver
    except Exception as e:
        logging.error(f"❌ Error configurando ChromeDriver: {e}")
        return None

def find_login_elements(driver):
    """Encontrar elementos de login con múltiples estrategias"""
    elements = {
        'username_field': None,
        'password_field': None,
        'login_button': None
    }
    
    # Estrategias para campo de usuario
    username_selectors = [
        (By.NAME, "uid"),
        (By.NAME, "username"),
        (By.NAME, "user"),
        (By.ID, "username"),
        (By.ID, "user"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.CSS_SELECTOR, "input[placeholder*='Username']"),
        (By.CSS_SELECTOR, "input[placeholder*='Usuario']"),
        (By.CSS_SELECTOR, "input[placeholder*='Email']"),
        (By.XPATH, "//input[@type='text']"),
        (By.XPATH, "//input[contains(@placeholder, 'Username')]"),
        (By.XPATH, "//input[contains(@placeholder, 'Usuario')]")
    ]
    
    # Estrategias para campo de contraseña
    password_selectors = [
        (By.NAME, "password"),
        (By.NAME, "pass"),
        (By.ID, "password"),
        (By.ID, "pass"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.XPATH, "//input[@type='password']")
    ]
    
    # Estrategias para botón de login
    login_button_selectors = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.CSS_SELECTOR, "button:contains('Login')"),
        (By.CSS_SELECTOR, "button:contains('Iniciar')"),
        (By.CSS_SELECTOR, "button:contains('Entrar')"),
        (By.XPATH, "//button[contains(text(), 'Login')]"),
        (By.XPATH, "//button[contains(text(), 'Iniciar')]"),
        (By.XPATH, "//button[contains(text(), 'Entrar')]"),
        (By.XPATH, "//input[@value='Login']"),
        (By.XPATH, "//input[@value='Iniciar']"),
        (By.XPATH, "//input[@value='Entrar']"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//input[@type='submit']"),
        (By.XPATH, "//*[contains(@class, 'login')]"),
        (By.XPATH, "//*[contains(@class, 'btn')]"),
        (By.XPATH, "//*[contains(@class, 'button')]")
    ]
    
    # Buscar campo de usuario
    for by, selector in username_selectors:
        try:
            element = driver.find_element(by, selector)
            elements['username_field'] = (by, selector, element)
            logging.info(f"✅ Campo de usuario encontrado: {by} = {selector}")
            break
        except NoSuchElementException:
            continue
    
    # Buscar campo de contraseña
    for by, selector in password_selectors:
        try:
            element = driver.find_element(by, selector)
            elements['password_field'] = (by, selector, element)
            logging.info(f"✅ Campo de contraseña encontrado: {by} = {selector}")
            break
        except NoSuchElementException:
            continue
    
    # Buscar botón de login
    for by, selector in login_button_selectors:
        try:
            element = driver.find_element(by, selector)
            elements['login_button'] = (by, selector, element)
            logging.info(f"✅ Botón de login encontrado: {by} = {selector}")
            break
        except NoSuchElementException:
            continue
    
    return elements

def analyze_page_structure(driver):
    """Analizar estructura de la página de login"""
    logging.info("🔍 Analizando estructura de la página...")
    
    # Obtener HTML de la página
    page_source = driver.page_source
    
    # Guardar HTML para análisis
    with open("login_page_analysis.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    
    # Buscar todos los inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")
    logging.info(f"📝 Encontrados {len(inputs)} elementos input:")
    
    for i, input_elem in enumerate(inputs):
        input_type = input_elem.get_attribute("type")
        input_name = input_elem.get_attribute("name")
        input_id = input_elem.get_attribute("id")
        input_placeholder = input_elem.get_attribute("placeholder")
        
        logging.info(f"   Input {i+1}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
    
    # Buscar todos los botones
    buttons = driver.find_elements(By.TAG_NAME, "button")
    logging.info(f"🔘 Encontrados {len(buttons)} elementos button:")
    
    for i, button in enumerate(buttons):
        button_text = button.text
        button_type = button.get_attribute("type")
        button_class = button.get_attribute("class")
        
        logging.info(f"   Button {i+1}: text='{button_text}', type={button_type}, class={button_class}")
    
    # Buscar formularios
    forms = driver.find_elements(By.TAG_NAME, "form")
    logging.info(f"📋 Encontrados {len(forms)} formularios:")
    
    for i, form in enumerate(forms):
        form_action = form.get_attribute("action")
        form_method = form.get_attribute("method")
        form_id = form.get_attribute("id")
        
        logging.info(f"   Form {i+1}: action={form_action}, method={form_method}, id={form_id}")

def test_login():
    """Probar el proceso de login"""
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        logging.info(f"🌐 Navegando a: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        time.sleep(5)
        
        # Guardar screenshot
        driver.save_screenshot("login_page_enhanced.png")
        logging.info("📸 Screenshot guardado: login_page_enhanced.png")
        
        # Analizar estructura de la página
        analyze_page_structure(driver)
        
        # Encontrar elementos de login
        elements = find_login_elements(driver)
        
        # Verificar si se encontraron todos los elementos
        if not elements['username_field']:
            logging.error("❌ No se pudo encontrar el campo de usuario")
            return False
        
        if not elements['password_field']:
            logging.error("❌ No se pudo encontrar el campo de contraseña")
            return False
        
        if not elements['login_button']:
            logging.error("❌ No se pudo encontrar el botón de login")
            return False
        
        # Realizar login
        logging.info("🔐 Realizando login...")
        
        # Limpiar y llenar campo de usuario
        username_by, username_selector, username_element = elements['username_field']
        username_element.clear()
        username_element.send_keys(ADMIN_USERNAME)
        logging.info(f"✅ Usuario ingresado: {ADMIN_USERNAME}")
        
        time.sleep(1)
        
        # Limpiar y llenar campo de contraseña
        password_by, password_selector, password_element = elements['password_field']
        password_element.clear()
        password_element.send_keys(ADMIN_PASSWORD)
        logging.info("✅ Contraseña ingresada")
        
        time.sleep(1)
        
        # Hacer clic en el botón de login
        login_by, login_selector, login_element = elements['login_button']
        login_element.click()
        logging.info("✅ Botón de login clickeado")
        
        # Esperar y verificar si el login fue exitoso
        time.sleep(5)
        
        # Guardar screenshot después del login
        driver.save_screenshot("after_login_enhanced.png")
        logging.info("📸 Screenshot después del login guardado: after_login_enhanced.png")
        
        # Verificar si estamos en una página diferente
        current_url = driver.current_url
        if current_url != LOGIN_URL:
            logging.info(f"✅ Login exitoso! Redirigido a: {current_url}")
            return True
        else:
            logging.warning("⚠️  Posible fallo en login - aún en la misma URL")
            return False
        
    except Exception as e:
        logging.error(f"❌ Error durante el test de login: {e}")
        return False
    finally:
        driver.quit()
        logging.info("🔌 Driver cerrado")

def main():
    """Función principal"""
    logging.info("🧪 Iniciando Test de Login Mejorado")
    logging.info("=" * 50)
    
    success = test_login()
    
    if success:
        logging.info("🎉 Test de login completado exitosamente")
    else:
        logging.error("❌ Test de login falló")
    
    logging.info("=" * 50)

if __name__ == "__main__":
    main() 