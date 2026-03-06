@echo off
cd /d "C:\Users\gabriel.silva\VS Code\Dashboard"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" Bot.py
) else (
    echo Ambiente virtual .venv nao encontrado!
)

