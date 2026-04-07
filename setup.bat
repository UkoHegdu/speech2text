@echo off
echo ============================================================
echo  Speech2Text Setup
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install faster-whisper sounddevice numpy pynput pyperclip pystray Pillow requests
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Ollama not found. Install it from https://ollama.com
    echo  After installing, run:
    echo    ollama pull phi3:mini
    echo.
) else (
    echo  Ollama found. Pulling phi3:mini model ^(~2GB, once only^)...
    ollama pull phi3:mini
)

echo.
echo [3/3] Done!
echo.
echo  To run:   python main.py
echo  To run without a console window:  pythonw main.py
echo  Hotkey:   Ctrl+Shift+Space  ^(press once to start, again to stop^)
echo  Quit:     Right-click the tray icon -> Quit
echo.
pause
