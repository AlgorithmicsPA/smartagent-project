@echo off
title SmartAgent - Monitor de Pedidos en Tiempo Real
color 0E

echo.
echo ================================================
echo    🎯 Monitor de Pedidos en Tiempo Real
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

echo ✅ Todo listo para iniciar el monitor
echo.

REM Mostrar configuración del monitor
echo 🔧 Configuración del Monitor:
python config\monitor_config.py
echo.

REM Preguntar si continuar
set /p continue="¿Deseas iniciar el monitor de pedidos? (s/n): "
if /i "%continue%"=="s" (
    echo.
    echo 🚀 Iniciando monitor de pedidos...
    echo 💡 Presiona Ctrl+C para detener el monitor
    echo.
    python src\core\order_monitor.py
) else (
    echo.
    echo ⏹️ Monitor cancelado
)

echo.
echo ✅ Operación completada
pause 