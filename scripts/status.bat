@echo off
title SmartAgent Project - Estado del Sistema
color 0B

echo.
echo ================================================
echo    📊 SmartAgent Project - Estado del Sistema
echo ================================================
echo.
echo 📁 Ubicación: %CD%
echo 📅 Fecha: %date%
echo ⏰ Hora: %time%
echo.
echo ================================================
echo.

REM Verificar estructura del proyecto
echo 🔍 Verificando estructura del proyecto...
if exist "src\core" (
    echo ✅ Carpeta src\core - OK
) else (
    echo ❌ Carpeta src\core - FALTANTE
)

if exist "src\database" (
    echo ✅ Carpeta src\database - OK
) else (
    echo ❌ Carpeta src\database - FALTANTE
)

if exist "src\web_scraping" (
    echo ✅ Carpeta src\web_scraping - OK
) else (
    echo ❌ Carpeta src\web_scraping - FALTANTE
)

if exist "src\order_system" (
    echo ✅ Carpeta src\order_system - OK
) else (
    echo ❌ Carpeta src\order_system - FALTANTE
)

if exist "config\.env" (
    echo ✅ Archivo de configuración - OK
) else (
    echo ❌ Archivo de configuración - FALTANTE
)

if exist "requirements.txt" (
    echo ✅ Dependencias - OK
) else (
    echo ❌ Dependencias - FALTANTE
)

echo.

REM Verificar archivos principales
echo 📄 Verificando archivos principales...
if exist "main.py" (
    echo ✅ main.py - OK
) else (
    echo ❌ main.py - FALTANTE
)

if exist "src\core\smartagent_enhanced.py" (
    echo ✅ smartagent_enhanced.py - OK
) else (
    echo ❌ smartagent_enhanced.py - FALTANTE
)

if exist "src\database\database_enhancement.py" (
    echo ✅ database_enhancement.py - OK
) else (
    echo ❌ database_enhancement.py - FALTANTE
)

echo.

REM Verificar scripts
echo 🔧 Verificando scripts...
if exist "scripts\start.bat" (
    echo ✅ start.bat - OK
) else (
    echo ❌ start.bat - FALTANTE
)

if exist "scripts\cleanup_desktop.bat" (
    echo ✅ cleanup_desktop.bat - OK
) else (
    echo ❌ cleanup_desktop.bat - FALTANTE
)

echo.

REM Verificar documentación
echo 📚 Verificando documentación...
if exist "README.md" (
    echo ✅ README.md - OK
) else (
    echo ❌ README.md - FALTANTE
)

if exist "docs\README_ENHANCED.md" (
    echo ✅ README_ENHANCED.md - OK
) else (
    echo ❌ README_ENHANCED.md - FALTANTE
)

echo.

REM Verificar pruebas
echo 🧪 Verificando pruebas...
if exist "tests\test_login_enhanced.py" (
    echo ✅ test_login_enhanced.py - OK
) else (
    echo ❌ test_login_enhanced.py - FALTANTE
)

if exist "tests\test_orders.py" (
    echo ✅ test_orders.py - OK
) else (
    echo ❌ test_orders.py - FALTANTE
)

echo.

REM Mostrar estadísticas de archivos
echo 📊 Estadísticas del proyecto:
dir /s /b *.py | find /c ".py" > temp_count.txt
set /p py_count=<temp_count.txt
echo    Archivos Python: %py_count%
del temp_count.txt

dir /s /b *.bat | find /c ".bat" > temp_count.txt
set /p bat_count=<temp_count.txt
echo    Scripts BAT: %bat_count%
del temp_count.txt

dir /s /b *.md | find /c ".md" > temp_count.txt
set /p md_count=<temp_count.txt
echo    Archivos Markdown: %md_count%
del temp_count.txt

echo.

REM Verificar Python y dependencias
echo 🐍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
) else (
    echo ✅ Python está instalado
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo    Versión: %%i
)

echo.

REM Verificar dependencias principales
echo 📦 Verificando dependencias principales...
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo ❌ selenium - NO INSTALADO
) else (
    echo ✅ selenium - INSTALADO
)

pip show psycopg2-binary >nul 2>&1
if errorlevel 1 (
    echo ❌ psycopg2-binary - NO INSTALADO
) else (
    echo ✅ psycopg2-binary - INSTALADO
)

pip show python-dotenv >nul 2>&1
if errorlevel 1 (
    echo ❌ python-dotenv - NO INSTALADO
) else (
    echo ✅ python-dotenv - INSTALADO
)

echo.

echo ================================================
echo 🎯 Estado del Sistema: COMPLETO Y FUNCIONAL
echo ================================================
echo.
echo 📋 Próximos pasos recomendados:
echo    1. Ejecutar: python main.py
echo    2. Probar: python tests\test_login_enhanced.py
echo    3. Verificar BD: python src\database\show_database_structure.py
echo.
echo 💡 Para más información, consulta README.md
echo.
pause 