@echo off
REM Captura periodica del modulo 3 (Programador de tareas de Windows).
cd /d "%~dp0.."
".venv\Scripts\python.exe" "scripts\capturar_almacenamiento.py"
exit /b %ERRORLEVEL%
