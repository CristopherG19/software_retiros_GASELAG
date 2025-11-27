@echo off
echo ==========================================
echo      CONSTRUYENDO QR MASTER v2.0
echo ==========================================

echo 1. Limpiando versiones anteriores...
rmdir /s /q build dist

echo.
echo 2. Instalando dependencias...
pip install -r requirements.txt

echo.
echo 3. Creando ejecutable...
pyinstaller --noconfirm --onedir --windowed --name "QR Master" --add-data "modulos;modulos" --hidden-import "PIL._tkinter_finder" --hidden-import "ttkbootstrap" --hidden-import "utils" --hidden-import "utils.generar_qr_batch" main.py

echo.
echo 4. Copiando librerias faltantes...
echo   - pyzbar...
xcopy /E /I /Y "C:\Users\CRISTOPHER\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyzbar" "dist\QR Master\_internal\pyzbar"
echo   - utils...
xcopy /E /I /Y "utils" "dist\QR Master\_internal\utils"
echo   - poppler...
xcopy /E /I /Y "C:\poppler" "dist\QR Master\_internal\poppler"

echo.
echo ==========================================
echo      CONSTRUCCION COMPLETADA
echo ==========================================
echo El ejecutable esta en la carpeta 'dist/QR Master'
pause
