@echo off
echo Limpiando archivos del escritorio...
echo.

REM Navegar al escritorio
cd "C:\Users\ALGORITHMICS 05\OneDrive\Desktop"

REM Eliminar archivos Python (ya movidos al proyecto)
del *.py 2>nul
echo ✅ Archivos Python eliminados

REM Eliminar archivos de configuración (ya movidos)
del .env 2>nul
echo ✅ Archivo .env eliminado

REM Eliminar archivos de documentación (ya movidos)
del *.md 2>nul
echo ✅ Archivos de documentación eliminados

REM Eliminar archivos de datos (ya movidos)
del *.json 2>nul
del *.txt 2>nul
echo ✅ Archivos de datos eliminados

REM Eliminar archivos de instalación (ya movidos)
del *.bat 2>nul
echo ✅ Archivos de instalación eliminados

REM Eliminar archivos de logs (ya movidos)
del *.log 2>nul
echo ✅ Archivos de logs eliminados

REM Eliminar archivos de prueba (ya movidos)
del test_*.py 2>nul
echo ✅ Archivos de prueba eliminados

REM Eliminar archivos de imagen (ya no necesarios)
del *.png 2>nul
del *.html 2>nul
echo ✅ Archivos de imagen eliminados

REM Eliminar carpetas de perfil (ya no necesarias)
rmdir /s /q besmart_profile* 2>nul
echo ✅ Carpetas de perfil eliminadas

REM Eliminar carpeta logs (ya movida)
rmdir /s /q logs 2>nul
echo ✅ Carpeta logs eliminada

REM Eliminar carpeta __pycache__ (ya no necesaria)
rmdir /s /q __pycache__ 2>nul
echo ✅ Carpeta __pycache__ eliminada

echo.
echo 🎉 ¡Limpieza completada!
echo.
echo El proyecto ahora está organizado en:
echo C:\Users\ALGORITHMICS 05\OneDrive\Desktop\smartagent-project
echo.
echo Para ejecutar el sistema:
echo cd smartagent-project
echo python main.py
echo.
pause 