"""
Cliente HTTP para monitores de órdenes
Manejo de peticiones HTTP y sesiones para el monitor terminal
"""

import requests
import logging
from bs4 import BeautifulSoup
from .config import TERMINAL_MONITOR_CONFIG, LOGIN_URL, TASKS_URL, TASKS_URL_WITH_PARAMS, ADMIN_USERNAME, ADMIN_PASSWORD
from .utils import BaseLogger
import re

class HTTPClient:
    """Cliente HTTP para peticiones web"""
    
    def __init__(self):
        self.session = None
        self.csrf_token = None
        self.setup_session()
    
    def setup_session(self):
        """Configurar sesión HTTP con headers optimizados"""
        try:
            self.session = requests.Session()
            
            # Configurar headers para simular navegador real
            self.session.headers.update({
                'User-Agent': TERMINAL_MONITOR_CONFIG["user_agent"],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            })
            
            # Configurar timeout
            self.session.timeout = TERMINAL_MONITOR_CONFIG["request_timeout"]
            
            BaseLogger.success("Sesión HTTP configurada correctamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error configurando sesión HTTP: {e}")
            BaseLogger.error(f"Error configurando sesión HTTP: {e}")
            return False
    
    def login(self):
        """Iniciar sesión usando requests"""
        try:
            BaseLogger.info(f"Intentando login con usuario: {ADMIN_USERNAME}")
            
            # Obtener página de login para extraer CSRF token
            login_page_response = self.session.get(LOGIN_URL)
            login_page_response.raise_for_status()
            
            soup = BeautifulSoup(login_page_response.text, 'html.parser')
            
            # Buscar CSRF token
            csrf_token = self._extract_csrf_token(soup)
            if csrf_token:
                self.csrf_token = csrf_token
                BaseLogger.info(f"CSRF token encontrado: {csrf_token[:10]}...")
            
            # Preparar datos de login
            login_data = {
                'uid': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
            
            # Agregar CSRF token si existe
            if self.csrf_token:
                login_data['csrf_token'] = self.csrf_token
            
            # Intentar login
            login_response = self.session.post(
                LOGIN_URL,
                data=login_data,
                allow_redirects=True
            )
            
            # Verificar si el login fue exitoso
            if self._is_login_successful(login_response):
                BaseLogger.success("Login exitoso via HTTP")
                return True
            else:
                BaseLogger.warning("Login falló, intentando estrategia alternativa...")
                return self._try_alternative_login()
            
        except Exception as e:
            logging.error(f"❌ Error en login HTTP: {e}")
            BaseLogger.error(f"Error en login HTTP: {e}")
            return False
    
    def _extract_csrf_token(self, soup):
        """Extraer CSRF token de la página de login"""
        try:
            # Buscar CSRF token en diferentes formatos
            csrf_selectors = [
                'input[name="csrf_token"]',
                'input[name="_token"]',
                'input[name="csrf"]',
                'meta[name="csrf-token"]',
                'input[type="hidden"][name*="csrf"]'
            ]
            
            for selector in csrf_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get('value') or element.get('content')
            
            return None
            
        except Exception:
            return None
    
    def _is_login_successful(self, response):
        """Verificar si el login fue exitoso"""
        try:
            # Verificar redirección a página de admin
            if 'admin' in response.url.lower():
                return True
            
            # Verificar contenido de la página
            if 'dashboard' in response.text.lower() or 'admin' in response.text.lower():
                return True
            
            # Verificar cookies de sesión
            if any('session' in cookie.name.lower() for cookie in self.session.cookies):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _try_alternative_login(self):
        """Estrategia alternativa de login"""
        try:
            # Intentar con diferentes endpoints
            alternative_urls = [
                f"{LOGIN_URL.rstrip('/')}/login",
                f"{LOGIN_URL.rstrip('/')}/auth",
                f"{LOGIN_URL.rstrip('/')}/signin"
            ]
            
            for url in alternative_urls:
                try:
                    login_data = {
                        'username': ADMIN_USERNAME,
                        'password': ADMIN_PASSWORD,
                        'email': ADMIN_USERNAME,
                        'user': ADMIN_USERNAME
                    }
                    
                    response = self.session.post(url, data=login_data, allow_redirects=True)
                    
                    if self._is_login_successful(response):
                        BaseLogger.success(f"Login exitoso via {url}")
                        return True
                        
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"❌ Error en login alternativo: {e}")
            return False
    
    def get_orders_page(self):
        """Obtener página de órdenes y activar el botón Active orders"""
        try:
            BaseLogger.info("Obteniendo página de tareas...")
            
            # Headers para evitar caché
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # 1. Obtener página base de tareas
            import time
            timestamp = int(time.time())
            url_with_timestamp = f"{TASKS_URL}?_t={timestamp}"
            
            response = self.session.get(url_with_timestamp, headers=headers)
            response.raise_for_status()
            
            BaseLogger.success(f"Página base obtenida: {TASKS_URL}")
            
            # 2. Buscar el botón "Active orders"
            soup = BeautifulSoup(response.text, 'html.parser')
            active_orders_button = soup.find('div', class_='btn')
            
            if active_orders_button:
                active_orders_label = active_orders_button.find('span', class_='label')
                if active_orders_label and 'Active orders' in active_orders_label.get_text():
                    BaseLogger.info("Botón Active orders encontrado, activando...")
                    
                    # Extraer el valor del botón para verificar
                    value_span = active_orders_button.find('span', class_='value')
                    if value_span:
                        active_count = value_span.get_text().strip()
                        BaseLogger.info(f"Botón Active orders tiene {active_count} órdenes")
                    
                    # 3. Simular clic en el botón usando la URL con parámetros
                    try:
                        BaseLogger.info("Activando filtro de Active orders...")
                        
                        # Usar la URL con parámetros que simula el clic en el botón
                        active_timestamp = int(time.time())
                        active_url = f"{TASKS_URL_WITH_PARAMS}&_t={active_timestamp}"
                        
                        active_response = self.session.get(active_url, headers=headers)
                        active_response.raise_for_status()
                        
                        BaseLogger.success("Filtro Active orders activado")
                        return active_response.text
                        
                    except Exception as click_error:
                        BaseLogger.warning(f"No se pudo activar el filtro: {click_error}")
                        # Continuar con la página original
                        return response.text
                else:
                    BaseLogger.info("Botón encontrado pero no es Active orders")
            else:
                BaseLogger.info("Botón Active orders no encontrado")
            
            # 4. Si no se pudo activar, intentar con la URL con parámetros directamente
            try:
                BaseLogger.info("Intentando con URL con parámetros...")
                params_timestamp = int(time.time())
                params_url = f"{TASKS_URL_WITH_PARAMS}&_t={params_timestamp}"
                
                params_response = self.session.get(params_url, headers=headers)
                params_response.raise_for_status()
                
                BaseLogger.success("Página con parámetros obtenida")
                return params_response.text
                
            except Exception as params_error:
                BaseLogger.warning(f"No se pudo obtener página con parámetros: {params_error}")
                return response.text
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo página de órdenes: {e}")
            BaseLogger.error(f"Error obteniendo página de órdenes: {e}")
            return None
    
    def _page_contains_orders(self, html_content):
        """Verificar si la página contiene órdenes"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar indicadores de órdenes
            order_indicators = [
                'order',
                'pedido',
                'task',
                'tarea',
                'preparation',
                'preparación',
                'active_orders',
                'orders-list'
            ]
            
            text_content = soup.get_text().lower()
            
            for indicator in order_indicators:
                if indicator in text_content:
                    return True
            
            # Buscar elementos específicos
            order_elements = soup.find_all(['tr', 'div', 'li'], class_=re.compile(r'order|task|active', re.I))
            if order_elements:
                return True
            
            return False
            
        except Exception:
            return False
    
    def refresh_session(self):
        """Refrescar la sesión"""
        try:
            BaseLogger.info("Refrescando sesión...")
            return self.login()
        except Exception as e:
            logging.error(f"❌ Error refrescando sesión: {e}")
            return False
    
    def close_session(self):
        """Cerrar la sesión"""
        if self.session:
            self.session.close()
            BaseLogger.info("Sesión HTTP cerrada") 