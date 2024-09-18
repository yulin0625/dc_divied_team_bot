@echo off
:: 設定 Conda 環境名稱
set CONDA_ENV_NAME=dc_bot
:: 啟動 Conda 環境
call conda activate %CONDA_ENV_NAME%

:: 如果啟動失敗，嘗試使用完整路徑
if %ERRORLEVEL% neq 0 (
    call C:\Users\%USERNAME%\Anaconda3\Scripts\activate %CONDA_ENV_NAME%
)

:: 檢查是否成功啟動環境
if %ERRORLEVEL% neq 0 (
    echo 無法啟動 Conda 環境。請檢查環境名稱是否正確。
    pause
    exit /b 1
)

:: 切換到腳本所在目錄
cd /d %~dp0

:: 運行機器人
python divide_team_bot.py

:: 暫停以查看輸出
pause