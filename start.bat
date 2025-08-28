@echo off
REM Check if .venv directory exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Activating virtual environment...
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Virtual environment already exists.
    echo Activating virtual environment...
    call .venv\Scripts\activate
)

echo Starting enbraille_main.py...
python enbraille_main.py

echo Script execution finished.
pause
