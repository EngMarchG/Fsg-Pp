@echo off

REM If Python 3.10 and above is not found, try python3 --version
if "%HIGHEST_VERSION%"=="" (
    setlocal enabledelayedexpansion
    set "HIGHEST_VERSION="
    for /f "tokens=2 delims=." %%i in ('python3 --version 2^>^&1') do (
        set "PYTHON_VERSION=%%i"
        set "PYTHON_VERSION=!PYTHON_VERSION:~0,2!"
        if !PYTHON_VERSION! geq 10 (
            set "HIGHEST_VERSION=!PYTHON_VERSION!"
            set "HIGHEST_PYTHON=python3"
        )
    )
    endlocal & (
        set "HIGHEST_VERSION=%HIGHEST_VERSION%"
        set "PYTHON_CMD=%HIGHEST_PYTHON%"
    )
)

REM Search for Python 3.10 and above using python --version
setlocal enabledelayedexpansion
set "HIGHEST_VERSION="
for /f "tokens=2 delims=." %%i in ('python --version 2^>^&1') do (
    set "PYTHON_VERSION=%%i"
    set "PYTHON_VERSION=!PYTHON_VERSION:~0,2!"
    if !PYTHON_VERSION! geq 10 (
        set "HIGHEST_VERSION=!PYTHON_VERSION!"
        set "HIGHEST_PYTHON=python"
    )
)
endlocal & (
    set "HIGHEST_VERSION=%HIGHEST_VERSION%"
    set "PYTHON_CMD=%HIGHEST_PYTHON%"
)

REM If Python 3.10 and above is not found, try py --version
if "%HIGHEST_VERSION%"=="" (
    setlocal enabledelayedexpansion
    set "HIGHEST_VERSION="
    for /f "tokens=2 delims=." %%i in ('py --version 2^>^&1') do (
        set "PYTHON_VERSION=%%i"
        set "PYTHON_VERSION=!PYTHON_VERSION:~0,2!"
        if !PYTHON_VERSION! geq 10 (
            set "HIGHEST_VERSION=!PYTHON_VERSION!"
            set "HIGHEST_PYTHON=py"
        )
    )
    endlocal & (
        set "HIGHEST_VERSION=%HIGHEST_VERSION%"
        set "PYTHON_CMD=%HIGHEST_PYTHON%"
    )
)



REM Check if Python 3.10 and above is found
if "%HIGHEST_VERSION%"=="" (
    echo Python 3.10 or above is not installed.
    pause
    exit /b
)



REM Activate the Python environment
echo Creating the virtual environment...
echo Do you want to remove the venv folder if it exists? (y/n)
set /p confirm=
if /i "%confirm%"=="y" (
    %PYTHON_CMD% -m venv --upgrade-deps --clear venv
) else (
    %PYTHON_CMD% -m venv --upgrade-deps venv
)

REM Check if venv folder exists
if exist venv\Scripts\activate.bat (
    REM Activate the virtual environment
    call venv\Scripts\activate.bat
) else (
    echo The virtual environment was not created successfully. Creating it using an alternative method...

    REM Remove the existing venv folder
    if exist venv (
        rmdir /s /q venv
    )

    REM Create the virtual environment using virtualenv package
    %PYTHON_CMD% -m pip install virtualenv
    %PYTHON_CMD% -m virtualenv venv

    REM Check if venv folder was created successfully
    if not exist venv\Scripts\activate.bat (
        echo Failed to create the virtual environment.
        pause
        exit /b
    )

    REM Activate the virtual environment
    call venv\Scripts\activate.bat
)


REM Install dependencies from requirements.txt
venv\Scripts\python.exe -m pip install -r requirements.txt

REM Offer choice to install PyTorch with GPU or directly install Ultralytics
echo Do you want to install PyTorch with GPU support? (y/n)
set /p choice=

if /i "%choice%"=="y" (
    REM Install PyTorch with GPU support
    echo Running %PYTHON_CMD% script...
    venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    venv\Scripts\pip install ultralytics==8.3.28
) else (
    REM Install Ultralytics using pip
    venv\Scripts\pip install ultralytics==8.3.28
)

REM Check if cv_files folder exists, create if it doesn't
if not exist cv_files (
    mkdir cv_files
)

REM Install AniClassifier.pt and AniFaceDet.pt inside cv_files folder
cd cv_files

REM Check if AniClassifier.pt exists, download if it doesn't
if not exist AniClassifier.pt (
    echo Downloading AniClassifier.pt...
    curl -L -o AniClassifier.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniClassifier.pt
)

REM Check if AniFaceDet.pt exists, download if it doesn't
if not exist AniFaceDet.pt (
    echo Downloading AniFaceDet.pt...
    curl -L -o AniFaceDet.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniFaceDet.pt
)

REM Go back to the parent directory
cd ..

REM Check the exit code of the previous command
if %errorlevel% neq 0 (
    echo An error occurred while running the script.
    pause
) else (
    echo Installation is complete. 
    pause
)

exit /b

:activate_virtualenv
REM Activate the virtual environment
call venv\Scripts\activate.bat
exit /b
