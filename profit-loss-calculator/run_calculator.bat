@echo off
REM MT5 Profit/Loss Calculator - Windows Batch Runner
REM This batch file provides an easy way to run the calculator on Windows

setlocal enabledelayedexpansion

echo ================================================================================
echo MT5 STANDALONE PROFIT/LOSS CALCULATOR
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if the main script exists
if not exist "profit_loss_calculator.py" (
    echo ERROR: profit_loss_calculator.py not found
    echo Please ensure you are running this batch file from the correct directory
    pause
    exit /b 1
)

REM Show menu options
echo Choose an option:
echo.
echo 1. Run Installation Test
echo 2. Validate Configuration Only
echo 3. Run Calculator (Default Settings)
echo 4. Run Calculator (Debug Mode)
echo 5. Run Calculator (JSON Output Only)
echo 6. Run Calculator (Specific Account)
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto validate
if "%choice%"=="3" goto run_default
if "%choice%"=="4" goto run_debug
if "%choice%"=="5" goto run_json
if "%choice%"=="6" goto run_account
if "%choice%"=="7" goto exit

echo Invalid choice. Please enter a number between 1 and 7.
pause
goto :eof

:test
echo.
echo Running installation test...
echo ================================================================================
python test_installation.py
echo ================================================================================
echo.
echo Test completed. Press any key to return to menu...
pause >nul
goto :eof

:validate
echo.
echo Validating configuration...
echo ================================================================================
python profit_loss_calculator.py --validate-only
echo ================================================================================
echo.
echo Validation completed. Press any key to return to menu...
pause >nul
goto :eof

:run_default
echo.
echo Running calculator with default settings...
echo ================================================================================
python profit_loss_calculator.py
echo ================================================================================
echo.
echo Calculator completed. Press any key to return to menu...
pause >nul
goto :eof

:run_debug
echo.
echo Running calculator in debug mode...
echo ================================================================================
python profit_loss_calculator.py --log-level DEBUG
echo ================================================================================
echo.
echo Calculator completed. Press any key to return to menu...
pause >nul
goto :eof

:run_json
echo.
echo Running calculator (JSON output only)...
echo ================================================================================
python profit_loss_calculator.py --json-only
echo ================================================================================
echo.
echo Calculator completed. Check the JSON output file.
echo Press any key to return to menu...
pause >nul
goto :eof

:run_account
echo.
set /p account_login="Enter account login number: "
echo.
echo Running calculator for account %account_login%...
echo ================================================================================
python profit_loss_calculator.py --account %account_login%
echo ================================================================================
echo.
echo Calculator completed. Press any key to return to menu...
pause >nul
goto :eof

:exit
echo.
echo Goodbye!
exit /b 0