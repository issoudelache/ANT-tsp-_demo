@echo off
cd /d "%~dp0"
echo ============================================
echo Application ACO - Colonies de Fourmis
echo ============================================

echo.
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate

echo.
echo Lancement de l'interface graphique...
python -m streamlit run app_streamlit.py

echo.
pause

