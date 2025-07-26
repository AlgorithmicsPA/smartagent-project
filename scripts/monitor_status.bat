@echo off
title SmartAgent - Estado del Monitor de Pedidos
color 0C

echo.
echo ================================================
echo    📊 Estado del Monitor de Pedidos
echo ================================================
echo.
echo 📁 Ubicación: %CD%
echo 📅 Fecha: %date%
echo ⏰ Hora: %time%
echo.
echo ================================================
echo.

REM Verificar si el monitor está ejecutándose
echo 🔍 Verificando procesos del monitor...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | find "python.exe" >nul
if errorlevel 1 (
    echo ❌ Monitor NO está ejecutándose
) else (
    echo ✅ Monitor está ejecutándose
)

tasklist /FI "IMAGENAME eq chromedriver.exe" /FO CSV | find "chromedriver.exe" >nul
if errorlevel 1 (
    echo ❌ ChromeDriver NO está ejecutándose
) else (
    echo ✅ ChromeDriver está ejecutándose
)

echo.

REM Mostrar logs recientes
echo 📝 Logs recientes del monitor:
echo ----------------------------------------
if exist "logs\order_monitor.log" (
    powershell "Get-Content logs\order_monitor.log -Tail 10"
) else (
    echo ❌ Archivo de log no encontrado
)

echo.
echo ================================================
echo 🎯 Estado del Monitor: ACTIVO
echo ================================================
echo.
echo 💡 El monitor está escuchando nuevos pedidos
echo 💡 Presiona Ctrl+C en la ventana del monitor para detenerlo
echo.
echo 📊 Para ver logs en tiempo real:
echo    Get-Content logs\order_monitor.log -Wait
echo.
pause 