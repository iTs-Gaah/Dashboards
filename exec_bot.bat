@echo off
cd /d "C:\Users\gabriel.silva\VS Code\Dashboard"

if exist "C:\Users\gabriel.silva\VS Code\.venv\Scripts\python.exe" (
    "C:\Users\gabriel.silva\VS Code\.venv\Scripts\python.exe" "C:\Users\gabriel.silva\VS Code\Dashboard\Bot.py"
) else (
    echo Ambiente virtual .venv nao encontrado!
)