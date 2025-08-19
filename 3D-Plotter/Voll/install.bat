@echo off
echo ==========================================
echo Python und Pakete Auto-Installation
echo ==========================================
echo.

:: Prüfen ob Python bereits installiert ist
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python ist bereits installiert.
    python --version
    goto :install_packages
)

echo Python wird installiert...
echo.

:: Python 3.12 herunterladen und installieren
echo Lade Python 3.12 herunter...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile 'python-installer.exe'"

if not exist "python-installer.exe" (
    echo Fehler: Python-Installer konnte nicht heruntergeladen werden.
    pause
    exit /b 1
)

echo Installiere Python...
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Warten bis Installation abgeschlossen ist
timeout /t 10 /nobreak >nul

:: Python-Installer löschen
del python-installer.exe

:: Umgebungsvariablen neu laden
call refreshenv >nul 2>&1

echo.
echo Python Installation abgeschlossen.

:install_packages
echo.
echo ==========================================
echo Installiere erforderliche Python-Pakete...
echo ==========================================
echo.

:: pip aktualisieren
echo Aktualisiere pip...
python -m pip install --upgrade pip

:: Pakete installieren
echo Installiere tkinter (bereits in Python enthalten)...
echo tkinter ist bereits in der Standard-Python-Installation enthalten.

echo.
echo Installiere Pillow (PIL)...
python -m pip install Pillow

echo.
echo Installiere numpy...
python -m pip install numpy

echo.
echo Installiere threading und time...
echo threading und time sind bereits in der Standard-Python-Installation enthalten.

echo.
echo ==========================================
echo Installation abgeschlossen!
echo ==========================================
echo.
echo Folgende Pakete wurden installiert:
echo - Python (mit tkinter, threading, time)
echo - Pillow (PIL)
echo - numpy
echo.

:: Prüfen ob alle Pakete korrekt installiert wurden
echo Prüfe Installation...
python -c "import tkinter; print('✓ tkinter erfolgreich importiert')"
python -c "import PIL; print('✓ Pillow erfolgreich importiert')"
python -c "import numpy; print('✓ numpy erfolgreich importiert')"
python -c "from threading import Thread; print('✓ threading erfolgreich importiert')"
python -c "import time; print('✓ time erfolgreich importiert')"

echo.
echo Alle Pakete sind bereit für Ihr Python-Skript!
echo Sie können nun Ihr Skript ausführen.
echo.
pause