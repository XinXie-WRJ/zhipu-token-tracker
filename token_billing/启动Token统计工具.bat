@echo off
chcp 65001 >nul
title 智谱AI Token使用量统计工具
echo.
echo ========================================
echo   智谱AI Token使用量统计工具
echo ========================================
echo.
echo 正在启动服务...
echo.
cd /d "%~dp0"
python app.py
pause
