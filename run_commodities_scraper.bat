@echo off
REM Commodities Scraper Batch File
REM This file runs the commodities scraper and logs output

cd /d "%~dp0"

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the script and log output with timestamp
echo Running Commodities Scraper at %date% %time%
python commodities_scraper.py >> logs\commodities_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

echo Completed at %date% %time%
