@echo off
echo ========================================
echo    SmartAgent - Instalador Automático
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.8+ desde python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [2/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo [3/4] Verificando Chrome...
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Chrome no encontrado en el registro. Verifica que esté instalado.
) else (
    echo ✅ Chrome encontrado
)

echo.
echo [4/4] Creando directorios...
if not exist "logs" mkdir logs
if not exist "besmart_profile" mkdir besmart_profile
echo ✅ Directorios creados

echo.
echo ========================================
echo    ✅ Instalación completada
echo ========================================
echo.
echo Para ejecutar el SmartAgent:
echo    python smartagent.py
echo.
echo Para ver la documentación:
echo    type README.md
echo.
pause 