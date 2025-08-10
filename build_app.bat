@echo off
echo ================================================
echo PDF Dark Mode Converter - Build Script
echo ================================================
echo.

echo Step 1: Converting favicon to app icon...
python convert_favicon.py
if not exist app_icon.ico (
    echo Warning: No favicon found, creating default icon...
    python create_icon.py
)
echo.

echo Step 2: Installing required packages...
pip install PyMuPDF==1.23.14 Pillow==10.1.0 pyinstaller
echo.

echo Step 3: Building standalone executable...
pyinstaller --onefile --windowed --name="PDF-DarkMode-Converter" --icon="app_icon.ico" app.py
echo.

echo Step 4: Cleaning up build files...
rmdir /s /q build
rmdir /s /q __pycache__
del PDF-DarkMode-Converter.spec
echo.

echo ================================================
echo BUILD COMPLETE!
echo ================================================
echo Your app is ready in the 'dist' folder:
echo - PDF-DarkMode-Converter.exe
echo.
echo Icon used: app_icon.ico
echo You can now run the .exe file directly!
echo ================================================
pause