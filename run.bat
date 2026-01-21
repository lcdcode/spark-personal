@echo off
REM SPARK Personal launcher script for Windows with virtual environment support

SET VENV_DIR=venv

REM Check if virtual environment exists
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv %VENV_DIR%

    IF ERRORLEVEL 1 (
        echo Error: Failed to create virtual environment
        echo Please ensure Python 3.8+ is installed
        pause
        exit /b 1
    )

    echo Installing dependencies...
    call %VENV_DIR%\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    IF ERRORLEVEL 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )

    echo Setup complete!
) ELSE (
    REM Activate existing virtual environment
    call %VENV_DIR%\Scripts\activate.bat
)

echo Starting SPARK Personal...
python -m spark.main
pause
