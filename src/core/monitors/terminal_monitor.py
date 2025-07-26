"""
Monitor de Pedidos en Tiempo Real - Terminal Version
Versión modular que funciona completamente en terminal sin Selenium/WebDriver
"""

import sys
import os
from pathlib import Path
import time
import logging
from datetime import datetime
import threading
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Importar módulos locales
from .config import TERMINAL_MONITOR_CONFIG, DATABASE_URL
from .utils import BaseLogger, OrderAnalytics, NotificationManager, DatabaseManager
from .http_client import HTTPClient
from .order_parser import OrderExtractor

# Configuración de logging para consola
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, TERMINAL_MONITOR_CONFIG["log_level"]),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/order_monitor_terminal.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TerminalOrderMonitor:
    """Monitor de órdenes optimizado para terminal sin Selenium"""
    
    def __init__(self):
        self.http_client = None
        self.db_manager = None
        self.order_extractor = None
        self.analytics = OrderAnalytics()
        self.is_running = False
        self.last_check_time = None
        self.order_hashes = set()
        self.order_stats = defaultdict(int)
        self.performance_start_time = None
        self.last_refresh_time = None
        self.error_count = 0
        self.success_count = 0
        
        self.setup_database()
        self.setup_components()
        
    def setup_database(self):
        """Configurar conexión a la base de datos"""
        try:
            db_conn = psycopg2.connect(DATABASE_URL)
            db_cursor = db_conn.cursor(cursor_factory=RealDictCursor)
            
            self.db_manager = DatabaseManager(db_conn, db_cursor)
            self.db_manager.create_orders_table("terminal_orders")
            
            BaseLogger.success("Conexión a base de datos establecida")
            
        except Exception as e:
            logging.error(f"❌ Error conectando a la base de datos: {e}")
            BaseLogger.error(f"Error conectando a la base de datos: {e}")
    
    def setup_components(self):
        """Configurar componentes del monitor"""
        try:
            # Configurar cliente HTTP
            self.http_client = HTTPClient()
            
            # Configurar extractor de órdenes
            self.order_extractor = OrderExtractor(self.analytics)
            
            BaseLogger.success("Componentes del monitor configurados")
            
        except Exception as e:
            logging.error(f"❌ Error configurando componentes: {e}")
            BaseLogger.error(f"Error configurando componentes: {e}")
    
    def extract_new_orders(self):
        """Extraer nuevas órdenes de la página HTML"""
        try:
            start_time = time.time()
            
            # Auto-refresh de sesión si está habilitado
            if TERMINAL_MONITOR_CONFIG["enable_auto_refresh"]:
                current_time = time.time()
                if not self.last_refresh_time or (current_time - self.last_refresh_time) > TERMINAL_MONITOR_CONFIG["refresh_interval"]:
                    BaseLogger.info("Refrescando sesión automáticamente...")
                    self.http_client.refresh_session()
                    self.last_refresh_time = current_time
            
            # Obtener página de órdenes
            html_content = self.http_client.get_orders_page()
            if not html_content:
                BaseLogger.warning("No se pudo obtener contenido de la página")
                return []
            
            # Extraer nuevas órdenes
            new_orders = self.order_extractor.extract_new_orders(html_content, self.order_hashes)
            
            # Procesar órdenes
            for order_data in new_orders:
                # Limpiar y validar datos
                order_data = self.order_extractor.clean_order_data(order_data)
                if self.order_extractor.validate_order_data(order_data):
                    self.order_stats['new_orders'] += 1
                    
                    # Guardar en base de datos
                    if self.db_manager:
                        performance_metrics = {
                            'processing_time': time.time() - start_time,
                            'error_count': self.error_count,
                            'success_count': self.success_count
                        }
                        self.db_manager.save_order(
                            order_data, 
                            "terminal_orders", 
                            self.analytics, 
                            performance_metrics
                        )
                        self.success_count += 1
            
            # Limpiar hashes antiguos si excede el límite
            if len(self.order_hashes) > TERMINAL_MONITOR_CONFIG["max_known_orders"]:
                self.order_hashes.clear()
                BaseLogger.info("Limpieza de hashes antiguos completada")
            
            # Mostrar tabla de nuevas órdenes
            if new_orders:
                print("\n" + "🚨 ¡NUEVAS ÓRDENES DETECTADAS! 🚨")
                print("="*60)
                NotificationManager.display_orders_table(new_orders, "TERMINAL")
                NotificationManager.play_notification_sound()
                
                # Mostrar resumen de nuevas órdenes
                print(f"🎯 RESUMEN: Se detectaron {len(new_orders)} nuevas órdenes")
                for i, order in enumerate(new_orders, 1):
                    print(f"   {i}. Orden #{order.get('order_id', 'N/A')} - {order.get('customer_name', 'N/A')} - ${order.get('total_amount', 'N/A')}")
                print("="*60)
            else:
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - No hay nuevas órdenes")
            
            # Métricas de rendimiento
            if TERMINAL_MONITOR_CONFIG["enable_performance_monitoring"]:
                processing_time = time.time() - start_time
                BaseLogger.performance(f"Procesamiento completado en {processing_time:.2f}s")
            
            return new_orders
            
        except Exception as e:
            logging.error(f"❌ Error extrayendo órdenes: {e}")
            BaseLogger.error(f"Error extrayendo órdenes: {e}")
            self.error_count += 1
            return []
    
    def display_terminal_stats(self):
        """Mostrar estadísticas para terminal"""
        analytics_report = self.analytics.get_analytics_report()
        
        print(f"\n📊 ESTADÍSTICAS DEL MONITOR TERMINAL")
        print("="*60)
        print(f"   Verificaciones totales: {self.order_stats['total_checks']}")
        print(f"   Nuevas órdenes detectadas: {self.order_stats['new_orders']}")
        print(f"   Órdenes en memoria: {len(self.order_hashes)}")
        print(f"   Última verificación: {self.last_check_time.strftime('%H:%M:%S') if self.last_check_time else 'N/A'}")
        print(f"   Tasa de éxito: {(self.success_count / max(self.success_count + self.error_count, 1)) * 100:.1f}%")
        print(f"   Errores totales: {self.error_count}")
        
        if analytics_report['total_orders'] > 0:
            print(f"\n📈 ANÁLISIS DE ÓRDENES:")
            print(f"   Total de órdenes procesadas: {analytics_report['total_orders']}")
            print(f"   Promedio por hora: {analytics_report['avg_orders_per_hour']:.1f}")
            
            if analytics_report['top_restaurants']:
                print(f"   Restaurante más activo: {analytics_report['top_restaurants'][0][0]}")
            
            if analytics_report['peak_hours']:
                print(f"   Hora pico: {analytics_report['peak_hours'][0][0]}:00")
    
    def monitor_orders(self):
        """Función principal de monitoreo"""
        BaseLogger.monitor("Iniciando monitoreo de órdenes en terminal...")
        
        while self.is_running:
            try:
                self.performance_start_time = time.time()
                current_time = datetime.now()
                
                            # Extraer nuevas órdenes
            new_orders = self.extract_new_orders()
            
            # Debug: Mostrar información de la extracción
            if new_orders:
                BaseLogger.success(f"✅ Extraídas {len(new_orders)} nuevas órdenes")
            else:
                BaseLogger.info("ℹ️ No se encontraron nuevas órdenes en esta verificación")
                
                # Actualizar estadísticas
                self.order_stats['total_checks'] += 1
                self.last_check_time = current_time
                
                # Mostrar estadísticas cada 30 verificaciones
                if self.order_stats['total_checks'] % 30 == 0:
                    self.display_terminal_stats()
                
                # Esperar antes de la siguiente verificación
                time.sleep(TERMINAL_MONITOR_CONFIG["check_interval"])
                
            except Exception as e:
                logging.error(f"❌ Error en monitoreo: {e}")
                BaseLogger.error(f"Error en monitoreo: {e}")
                self.error_count += 1
                time.sleep(TERMINAL_MONITOR_CONFIG["check_interval"])
    
    def start_monitoring(self):
        """Iniciar el monitoreo"""
        try:
            BaseLogger.monitor("🚀 Iniciando Monitor de Órdenes Terminal")
            
            if not self.http_client.setup_session():
                return False
            
            if not self.http_client.login():
                return False
            
            self.is_running = True
            self.last_check_time = datetime.now()
            self.last_refresh_time = time.time()
            
            print("\n" + "="*80)
            print("🎯 MONITOR DE ÓRDENES TERMINAL - SMARTAGENT")
            print("="*80)
            print("✅ Sistema iniciado correctamente")
            print(f"⏱️  Intervalo de verificación: {TERMINAL_MONITOR_CONFIG['check_interval']} segundos")
            print(f"🔄 Auto-refresh: {'Activado' if TERMINAL_MONITOR_CONFIG['enable_auto_refresh'] else 'Desactivado'}")
            print(f"🔔 Notificaciones: {'Activadas' if TERMINAL_MONITOR_CONFIG['notification_sound'] else 'Desactivadas'}")
            print(f"📊 Analytics: {'Activado' if TERMINAL_MONITOR_CONFIG['enable_order_analytics'] else 'Desactivado'}")
            print(f"⚡ Performance monitoring: {'Activado' if TERMINAL_MONITOR_CONFIG['enable_performance_monitoring'] else 'Desactivado'}")
            print("="*80)
            print("💡 Presiona Ctrl+C para detener el monitoreo")
            print("="*80)
            
            # Iniciar monitoreo en hilo separado
            monitor_thread = threading.Thread(target=self.monitor_orders)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Mantener el hilo principal vivo
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                BaseLogger.info("⏹️ Detención solicitada por el usuario")
                self.stop_monitoring()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error iniciando monitoreo: {e}")
            BaseLogger.error(f"Error iniciando monitoreo: {e}")
            return False
    
    def stop_monitoring(self):
        """Detener el monitoreo"""
        BaseLogger.info("🛑 Deteniendo monitoreo...")
        self.is_running = False
        
        if self.http_client:
            self.http_client.close_session()
        
        if self.db_manager and self.db_manager.db_cursor:
            self.db_manager.db_cursor.close()
        
        if self.db_manager and self.db_manager.db_conn:
            self.db_manager.db_conn.close()
        
        self.display_terminal_stats()
        BaseLogger.success("✅ Monitoreo detenido correctamente")

def main():
    """Función principal del monitor terminal"""
    monitor = TerminalOrderMonitor()
    
    try:
        success = monitor.start_monitoring()
        if not success:
            BaseLogger.error("❌ No se pudo iniciar el monitoreo")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Error general en monitor: {e}")
        BaseLogger.error(f"Error general en monitor: {e}")
        monitor.stop_monitoring()
        sys.exit(1)

if __name__ == "__main__":
    main() 