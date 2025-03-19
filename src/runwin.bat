@echo off
setlocal EnableDelayedExpansion

echo Legal Analysis Simulation System
echo ================================

REM PARSE COMMAND LINE ARGUMENTS. EDIT HERE 
set MODEL=deepseek-chat
set QUESTION=How has the principle of 'duty of care' evolved over time? Focus specifically on the legal frameworks used.

REM UNUSED! flag for potential Q&A based on result
set INTERACTIVE=

:parse_args
if "%~1"=="" goto end_parse_args
if /i "%~1"=="--model" (
    set MODEL=%~2
    shift
) else if /i "%~1"=="--interactive" (
    set INTERACTIVE=--interactive
) else if /i "%~1"=="--question" (
    set QUESTION=%~2
    shift
)
shift
goto parse_args
:end_parse_args

REM If model not provided via command line, prompt the user
if "!MODEL!"=="" (
    echo.
    echo Select a model:
    echo 1. gpt-4o-mini
    echo 2. gpt-4o
    echo 3. claude-3-opus
    echo 4. claude-3-sonnet
    echo 5. command-r-plus
    echo.
    set /p MODEL_CHOICE="Enter your choice (1-5, or enter a custom model name): "
    
    if "!MODEL_CHOICE!"=="1" set MODEL=gpt-4o-mini
    if "!MODEL_CHOICE!"=="2" set MODEL=gpt-4o
    if "!MODEL_CHOICE!"=="3" set MODEL=claude-3-opus
    if "!MODEL_CHOICE!"=="4" set MODEL=claude-3-sonnet
    if "!MODEL_CHOICE!"=="5" set MODEL=command-r-plus
    
    REM If not a number 1-5, assume it's a custom model name
    echo !MODEL_CHOICE! | findstr /r "^[1-5]$" >nul
    if errorlevel 1 if not "!MODEL_CHOICE!"=="" set MODEL=!MODEL_CHOICE!
)

REM If question not provided via command line and we're not in interactive mode, prompt for it
if "!QUESTION!"=="" (
    echo.
    echo You can provide your legal question now, or leave it blank to be prompted later.
    echo.
    set /p QUESTION="Enter your legal question (or press Enter to be prompted during execution): "
)

REM Build the command
set CMD=python main.py

REM Add model if specified
if not "!MODEL!"=="" (
    set CMD=!CMD! --model "!MODEL!"
)

REM Add interactive flag if specified
if not "!INTERACTIVE!"=="" (
    set CMD=!CMD! !INTERACTIVE!
)

REM Add question if specified
if not "!QUESTION!"=="" (
    set CMD=!CMD! --question "!QUESTION!"
)

echo.
echo Running command: !CMD!
echo.

REM Execute the command
!CMD!

REM Pause at the end so results can be viewed
echo.
echo Analysis completed. Press any key to exit...
pause >nul
endlocal
