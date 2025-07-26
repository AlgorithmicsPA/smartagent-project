@echo off
echo 🎯 MONITOR DE ÓRDENES MEJORADO - SmartAgent Enhanced
echo ====================================================
echo.

cd /d "%~dp0.."
python src/core/order_monitor_enhanced.py

echo.
echo ✅ Monitor detenido
pause 