@echo off
title Mis Gastos
cd /d "%~dp0"
echo ============================================
echo   Iniciando la app "Mis Gastos"...
echo   Se abrira el navegador en http://localhost:8501
echo   Para detener la app, cierra esta ventana.
echo ============================================
streamlit run app.py
pause
