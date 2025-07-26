@echo off
echo 🔍 SEGUIMIENTO DE ERRORES - SmartAgent Project
echo ================================================
echo.

cd /d "%~dp0.."
python scripts/error_tracker.py

echo.
echo ✅ Seguimiento completado
pause 