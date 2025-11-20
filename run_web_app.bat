@echo off
echo ===================================================
echo      SALUD CONTROL - SERVIDOR WEB (PWA)
echo ===================================================
echo.
echo [1] Obteniendo tu direccion IP local...
for /f "tokens=14" %%a in ('ipconfig ^| findstr IPv4') do set IP=%%a
echo Tu IP es: %IP%
echo.
echo [2] INSTRUCCIONES PARA CELULAR:
echo    a) Conecta tu celular al Wi-Fi.
echo    b) Abre Chrome o Safari.
echo    c) Ingresa a: http://%IP%:5000
echo.
echo [3] Iniciando servidor...
echo    (Si Windows pide permiso del Firewall, dale a "Permitir")
echo.
cd desktop_app
python app.py
pause
