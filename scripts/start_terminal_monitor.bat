@echo off
echo 🎯 MONITOR DE ÓRDENES TERMINAL - SmartAgent
echo ============================================
echo.

cd /d "%~dp0.."
python src/core/order_monitor_terminal.py

echo.
echo ✅ Monitor terminal detenido
pause 