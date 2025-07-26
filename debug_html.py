#!/usr/bin/env python3
"""
Script de debug para verificar el HTML recibido
"""
import requests
from bs4 import BeautifulSoup
import time

# Configuración
LOGIN_URL = "https://admin.besmartdelivery.mx/"
TASKS_URL = "https://admin.besmartdelivery.mx/tasks?status=REQUIRES_CONFIRMATION&status=PROCESSED&status=INPREPARATION&status=READYFORCOLLECTION&status=ONTHEWAY&status=ATLOCATION"
ADMIN_USERNAME = "federico"
ADMIN_PASSWORD = "28ZwnPHQRC*H4BmfmEB-YHcC"

def debug_html():
    """Debug del HTML recibido"""
    print("🔍 DEBUG HTML - SmartAgent")
    print("=" * 50)
    
    # Configurar sesión
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })
    
    try:
        # 1. Login
        print("1️⃣ Intentando login...")
        login_data = {
            'uid': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        print(f"   Status: {login_response.status_code}")
        print(f"   URL final: {login_response.url}")
        
        # 2. Obtener página de tareas
        print("\n2️⃣ Obteniendo página de tareas...")
        timestamp = int(time.time())
        url_with_timestamp = f"{TASKS_URL}&_t={timestamp}"
        
        response = session.get(url_with_timestamp)
        print(f"   Status: {response.status_code}")
        print(f"   URL: {response.url}")
        print(f"   Tamaño HTML: {len(response.text)} caracteres")
        
        # 3. Analizar HTML
        print("\n3️⃣ Analizando HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar tabla
        tables = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"   Tabla {i+1}: clases = {table.get('class', [])}")
            
            # Buscar responsive-table
            if 'responsive-table' in table.get('class', []):
                print(f"   ✅ Tabla responsive-table encontrada!")
                
                # Buscar filas de órdenes
                tbody = table.find('tbody')
                if tbody:
                    order_rows = tbody.find_all('tr', class_='orders-list-item')
                    print(f"   📊 Filas de órdenes: {len(order_rows)}")
                    
                    for j, row in enumerate(order_rows):
                        print(f"   Orden {j+1}: {row.get('class', [])}")
                        
                        # Extraer datos básicos
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            # ID de orden
                            order_id_field = cells[0].find('div', class_='order-id-field')
                            if order_id_field:
                                order_text = order_id_field.get_text(strip=True)
                                print(f"     ID: {order_text}")
                            
                            # Restaurante
                            vendor_field = cells[1].find('div', class_='vendor-field')
                            if vendor_field:
                                vendor_link = vendor_field.find('a', class_='link')
                                if vendor_link:
                                    print(f"     Restaurante: {vendor_link.get_text(strip=True)}")
                            
                            # Cliente
                            customer_field = cells[2].find('div', class_='customer-field')
                            if customer_field:
                                customer_link = customer_field.find('a', class_='link')
                                if customer_link:
                                    print(f"     Cliente: {customer_link.get_text(strip=True)}")
                            
                            # Total
                            price_span = cells[4].find('span', class_='price')
                            if price_span:
                                print(f"     Total: {price_span.get_text(strip=True)}")
        
        # 4. Buscar botón Active orders
        print("\n4️⃣ Buscando botón Active orders...")
        active_orders_buttons = soup.find_all('div', class_='btn')
        print(f"   Botones encontrados: {len(active_orders_buttons)}")
        
        for i, btn in enumerate(active_orders_buttons):
            label = btn.find('span', class_='label')
            value = btn.find('span', class_='value')
            if label and value:
                print(f"   Botón {i+1}: {label.get_text(strip=True)} = {value.get_text(strip=True)}")
        
        # 5. Guardar HTML para inspección
        print("\n5️⃣ Guardando HTML para inspección...")
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("   HTML guardado en debug_page.html")
        
        # 6. Mostrar primeros 500 caracteres
        print("\n6️⃣ Primeros 500 caracteres del HTML:")
        print("-" * 50)
        print(response.text[:500])
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_html() 