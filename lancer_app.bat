@echo off
echo ========================================
echo Application ACO - Colonies de Fourmis
echo ========================================
echo.
echo Lancement de l'interface graphique...
echo.
cd /d "%~dp0"
streamlit run app_streamlit.py
pause

