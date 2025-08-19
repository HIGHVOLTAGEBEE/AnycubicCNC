
@echo off
chcp 65001 >nul
cls

echo ============================================
echo PNG zu G-Code Konverter für Anycubic i3 Mega S 
echo ============================================
echo.

REM Überprüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo Bitte installieren Sie Python von https://python.org
    echo.
    pause
    exit /b 1
)

REM Überprüfen ob PIL/Pillow installiert ist
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo PIL/Pillow wird installiert...
    pip install Pillow
    if errorlevel 1 (
        echo FEHLER: Konnte PIL/Pillow nicht installieren.
        echo Versuchen Sie es manuell mit: pip install Pillow
        echo.
        pause
        exit /b 1
    )
    echo PIL/Pillow erfolgreich installiert!
    echo.
)

echo.
echo Alles Installiert.
pause