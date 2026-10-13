@echo off
title start-all

start "backend-8000" cmd /k "cd /d %~dp0backend && %~dp0backend\.venv\Scripts\python.exe run.py"

start "frontend-5173" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
