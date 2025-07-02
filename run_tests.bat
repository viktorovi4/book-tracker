@echo off
start python app.py
timeout /t 5
pytest tests/ --alluredir=./allure-results
taskkill /im python.exe /f