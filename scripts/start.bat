@echo off
title SmartAgent Project - Sistema Completo
color 0A

echo.
echo ================================================
echo    🚀 SmartAgent Project - Sistema Completo
echo ================================================
echo.
echo 📁 Ubicación: %CD%
echo 📅 Fecha: %date%
echo ⏰ Hora: %time%
echo.
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
echo 🔍 Verificando dependencias...
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

REM Verificar archivo de configuración
if not exist "config\.env" (
    echo ❌ Error: Archivo de configuración no encontrado
    echo Por favor verifica que config\.env existe
    pause
    exit /b 1
)

echo ✅ Todo listo para ejecutar
echo.
echo 🎯 Opciones disponibles:
echo    1. Ejecutar sistema principal
echo    2. Configurar base de datos
echo    3. Mostrar estructura de BD
echo    4. Ejecutar pruebas
echo    5. Consultar base de datos
echo    6. Salir
echo.

set /p choice="Selecciona una opción (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🤖 Ejecutando sistema principal...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo 🗄️ Configurando base de datos...
    python src\database\database_enhancement.py
) else if "%choice%"=="3" (
    echo.
    echo 📊 Mostrando estructura de base de datos...
    python src\database\show_database_structure.py
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Ejecutando pruebas...
    python tests\test_smartagent.py
    python tests\test_orders.py
) else if "%choice%"=="5" (
    echo.
    echo 🔍 Consultando base de datos...
    python src\database\consultar_db.py
) else if "%choice%"=="6" (
    echo.
    echo 👋 ¡Hasta luego!
    exit /b 0
) else (
    echo.
    echo ❌ Opción no válida
    pause
    exit /b 1
)

echo.
echo ✅ Operación completada
pause 