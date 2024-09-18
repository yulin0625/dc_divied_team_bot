@echo off
cd /d %~dp0
call venv\Scripts\activate
python divide_team_bot.py
pause