@echo off
chcp 65001 > nul
echo ========================================
echo  Python: первые программы — Сервер
echo ========================================
echo.
echo  Запуск Flask сервера...
echo  Откройте браузер: http://localhost:5000
echo.
echo  Данные администратора:
echo    Логин:  admin
echo    Пароль: admin123
echo.
echo  Нажмите Ctrl+C для остановки сервера.
echo ========================================
echo.
python app.py
pause
