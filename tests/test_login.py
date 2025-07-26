#!/usr/bin/env python3
"""
Script de prueba simple para verificar la página de login
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_login_page():
    print("🔍 Probando página de login...")
    
    # Configurar navegador
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Instalar ChromeDriver automáticamente
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Navegador configurado")
        
        # Ir a la página de login
        url = "https://admin.besmartdelivery.mx/"
        print(f"🌐 Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que cargue
        time.sleep(5)
        
        # Tomar screenshot
        driver.save_screenshot("test_login.png")
        print("📸 Screenshot guardado como test_login.png")
        
        # Guardar HTML
        with open("test_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML guardado como test_login.html")
        
        # Analizar elementos de la página
        print("\n🔍 Analizando elementos de la página:")
        
        # Título
        title = driver.title
        print(f"📋 Título: {title}")
        
        # Inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Inputs encontrados: {len(inputs)}")
        for i, inp in enumerate(inputs):
            input_type = inp.get_attribute("type")
            input_name = inp.get_attribute("name")
            input_id = inp.get_attribute("id")
            input_placeholder = inp.get_attribute("placeholder")
            print(f"  Input {i+1}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
        
        # Botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Botones encontrados: {len(buttons)}")
        for i, btn in enumerate(buttons):
            btn_text = btn.text
            btn_type = btn.get_attribute("type")
            btn_id = btn.get_attribute("id")
            print(f"  Botón {i+1}: text='{btn_text}', type={btn_type}, id={btn_id}")
        
        # Formularios
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"📋 Formularios encontrados: {len(forms)}")
        for i, form in enumerate(forms):
            form_action = form.get_attribute("action")
            form_method = form.get_attribute("method")
            form_id = form.get_attribute("id")
            print(f"  Form {i+1}: action={form_action}, method={form_method}, id={form_id}")
        
        # URLs actuales
        current_url = driver.current_url
        print(f"📍 URL actual: {current_url}")
        
        driver.quit()
        print("✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_login_page() 