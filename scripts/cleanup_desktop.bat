@echo off
echo 🧹 LIMPIEZA DEL ESCRITORIO - SmartAgent Project
echo ================================================
echo.

cd /d "%~dp0.."
python scripts/cleanup_desktop.py

echo.
echo ✅ Limpieza completada
pause 