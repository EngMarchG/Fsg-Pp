@echo off

set ERROR_REPORTING=FALSE

<nul (
    set /p "="
)

echo Running the script...

cd /d "%~dp0"
call venv\Scripts\activate

set OPEN_IN_BROWSER=-o
python Fsg_pp.py 

rem Check the exit code of the previous command
if %errorlevel% neq 0 (
    echo An error occurred while running the script.
    pause
)