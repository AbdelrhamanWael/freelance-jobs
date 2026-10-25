@echo off
echo =======================================================
echo     Installing Requirements and PyInstaller
echo =======================================================
pip install -r requirements.txt
pip install pyinstaller

echo.
echo =======================================================
echo     Building Executable (Gulf_Data_Filter.exe)
echo =======================================================
:: --noconfirm overwrites existing build
:: --log-level=WARN makes the output cleaner
pyinstaller --noconfirm --log-level=WARN ^
    --name "Gulf_Data_Filter" ^
    --onefile ^
    --add-data "templates;templates" ^
    app.py

echo.
echo =======================================================
echo     Build Complete!
echo     Your executable is ready in the 'dist' folder.
echo =======================================================
pause
