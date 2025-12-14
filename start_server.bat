@echo off
chcp 65001 >nul
echo ========================================
echo   راه‌اندازی سرور احراز هویت
echo ========================================
echo.
cd backend
echo در حال اجرای سرور...
echo.
python server.py
pause

