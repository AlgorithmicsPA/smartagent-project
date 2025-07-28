# 🚀 SmartAgent Project

## 📁 Estructura del Proyecto

```
smartagent-project/
├── 📄 main.py                    # Punto de entrada principal
├── 📄 requirements.txt           # Dependencias Python
├── 📁 src/                       # Código fuente principal
│   ├── 📁 core/                  # Funcionalidad principal
│   │   ├── 📄 smartagent_enhanced.py
│   │   └── 📄 recuperar_datos.py
│   ├── 📁 database/              # Gestión de base de datos
│   │   ├── 📄 database_setup.py
│   │   ├── 📄 database_enhancement.py
│   │   ├── 📄 show_database_structure.py
│   │   └── 📄 consultar_db.py
│   ├── 📁 web_scraping/          # Exploración web
│   │   └── 📄 smartagent.py
│   └── 📁 order_system/          # Sistema de pedidos
│       └── 📄 smartagent_orders.py
├── 📁 config/                    # Configuración
│   └── 📄 .env                   # Variables de entorno
├── 📁 logs/                      # Logs del sistema
├── 📁 data/                      # Datos y archivos JSON
├── 📁 docs/                      # Documentación
│   └── 📄 README_ENHANCED.md
├── 📁 tests/                     # Pruebas
│   ├── 📄 test_smartagent.py
│   ├── 📄 test_orders.py
│   └── 📄 test_login.py
└── 📁 scripts/                   # Scripts de utilidad
    └── 📄 install.bat
```

## 🚀 Inicio Rápido

### 1. **Instalación**
```bash
# Navegar al proyecto
cd smartagent-project

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Configuración**
```bash
# Verificar archivo de configuración
type config\.env
```

### 3. **Ejecutar Sistema**
```bash
# Ejecutar sistema principal
python main.py
```

## 🎯 Funcionalidades

### **Sistema Principal (main.py)**
- **Opción 1**: Ejecutar sistema completo
- **Opción 2**: Configurar base de datos
- **Opción 3**: Mostrar estructura de BD
- **Opción 4**: Ejecutar pruebas
- **Opción 5**: Consultar base de datos
- **Opción 6**: Salir

### **Módulos Específicos**

#### **Core (Funcionalidad Principal)**
- `smartagent_enhanced.py` - Sistema completo integrado
- `recuperar_datos.py` - Recuperación de datos

#### **Database (Gestión de Base de Datos)**
- `database_setup.py` - Configuración inicial
- `database_enhancement.py` - Mejoras de BD
- `show_database_structure.py` - Visualización de estructura
- `consultar_db.py` - Consultas avanzadas

#### **Web Scraping (Exploración Web)**
- `smartagent.py` - Exploración web básica

#### **Order System (Sistema de Pedidos)**
- `smartagent_orders.py` - Gestión de pedidos

## 🔧 Configuración

### **Variables de Entorno (.env)**
```env
ADMIN_USERNAME=federico
ADMIN_PASSWORD=***CONTRASEÑA_OCULTA***
START_URL=https://admin.besmartdelivery.mx/
LOGIN_URL=https://admin.besmartdelivery.mx/
DATABASE_URL=postgresql://***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***/***DB_OCULTA***?sslmode=require&channel_binding=require
```

## 📊 Base de Datos

### **28 Tablas Organizadas**
- **8 tablas** de exploración web
- **7 tablas** del sistema de pedidos
- **13 tablas** complementarias mejoradas

### **Funcionalidades de BD**
- Gestión de clientes
- Sistema de pedidos
- Control de inventario
- Métodos de pago
- Notificaciones
- Analytics y reportes

## 🧪 Pruebas

### **Ejecutar Pruebas**
```bash
# Pruebas del sistema
python tests/test_smartagent.py

# Pruebas de pedidos
python tests/test_orders.py

# Pruebas de login
python tests/test_login.py
```

## 📝 Logs

### **Ubicación de Logs**
- `logs/main.log` - Logs principales
- `logs/smartagent_enhanced.log` - Logs del sistema
- `logs/smartagent_orders.log` - Logs de pedidos

## 🔍 Consultas

### **Consultar Base de Datos**
```bash
python src/database/consultar_db.py
```

### **Mostrar Estructura**
```bash
python src/database/show_database_structure.py
```

## 🚀 Despliegue

### **Requisitos del Sistema**
- Python 3.8+
- PostgreSQL (Neon DB)
- Chrome/Chromium
- Conexión a internet

### **Dependencias Principales**
- selenium
- beautifulsoup4
- psycopg2-binary
- python-dotenv
- webdriver-manager

## 📈 Estadísticas

### **Datos Actuales**
- **736 páginas** exploradas
- **736 botones** detectados
- **113 inputs** encontrados
- **593 links** extraídos
- **28 formularios** detectados
- **17 tablas HTML** extraídas

## 🔒 Seguridad

### **Características de Seguridad**
- Credenciales en variables de entorno
- Conexión SSL a base de datos
- Logs de auditoría
- User-Agent personalizado
- Pausas aleatorias en exploración

## 🎉 Beneficios de la Nueva Estructura

### **Organización Profesional**
- ✅ Separación clara de responsabilidades
- ✅ Módulos organizados por función
- ✅ Configuración centralizada
- ✅ Logs organizados
- ✅ Pruebas separadas
- ✅ Documentación estructurada

### **Facilidad de Mantenimiento**
- ✅ Código modular y reutilizable
- ✅ Configuración centralizada
- ✅ Logs detallados
- ✅ Pruebas automatizadas
- ✅ Documentación completa

### **Escalabilidad**
- ✅ Estructura preparada para crecimiento
- ✅ Módulos independientes
- ✅ Base de datos optimizada
- ✅ Sistema de logging robusto

## 🚀 Próximos Pasos

1. **Ejecutar el sistema principal**
2. **Revisar logs y estadísticas**
3. **Personalizar configuración según necesidades**
4. **Agregar nuevas funcionalidades**
5. **Optimizar rendimiento**

---

**¡El proyecto está listo para usar con una estructura profesional y organizada!** 🎉 