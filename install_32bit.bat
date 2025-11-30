@echo off
REM Installation script for 32-bit Python 3.12
echo Installing packages for 32-bit Python 3.12...

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install packages one by one with --only-binary to avoid compilation
echo.
echo Installing requests...
pip install requests>=2.31.0

echo.
echo Installing beautifulsoup4...
pip install beautifulsoup4>=4.12.0

echo.
echo Installing pandas (this may take a moment)...
pip install pandas==2.1.4 --only-binary=:all:

echo.
echo Installing lxml...
pip install lxml>=4.9.0 --only-binary=:all:

echo.
echo Installing mysql-connector-python...
pip install mysql-connector-python>=8.0.0

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Verifying installation...
python -c "import pandas; print('pandas version:', pandas.__version__)"
python -c "import mysql.connector; print('MySQL connector: OK')"
python -c "import requests; print('requests: OK')"
python -c "import bs4; print('beautifulsoup4: OK')"
python -c "import lxml; print('lxml: OK')"

echo.
echo All packages installed successfully!
pause
