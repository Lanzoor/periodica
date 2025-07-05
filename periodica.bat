@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run build.py.
    exit /b 1
)

call "venv\Scripts\activate.bat"

python "src\main.py" %*

deactivate
popd
endlocal
