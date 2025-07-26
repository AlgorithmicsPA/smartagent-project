@echo off
echo ========================================
echo ACTUALIZANDO GITHUB - SMARTAGENT PROJECT
echo ========================================
echo.

echo 1. Verificando estado de Git...
git status
echo.

echo 2. Agregando todos los archivos nuevos...
git add .
echo.

echo 3. Haciendo commit de los cambios...
git commit -m "FEAT: Monitor de Selenium funcionando correctamente

- Implementado monitor de Selenium funcional
- Login robusto con múltiples selectores
- Detección y extracción de órdenes activas
- Monitoreo continuo implementado
- Herramientas de debug y diagnóstico
- Múltiples versiones de desarrollo para referencia

Archivos principales:
- selenium_monitor_working.py (VERSION FINAL)
- selenium_monitor_debug.py
- quick_debug.py
- diagnostic_monitor.py

Estado: MONITOR FUNCIONANDO CORRECTAMENTE"
echo.

echo 4. Subiendo cambios a GitHub...
git push origin main
echo.

echo 5. Verificando estado final...
git status
echo.

echo ========================================
echo ACTUALIZACION COMPLETADA
echo ========================================
echo.
echo Archivos principales agregados:
echo - selenium_monitor_working.py (VERSION FINAL)
echo - selenium_monitor_debug.py
echo - quick_debug.py
echo - diagnostic_monitor.py
echo - SELENIUM_MONITOR_UPDATE.md
echo.
echo Para ejecutar el monitor:
echo python selenium_monitor_working.py
echo.
pause 