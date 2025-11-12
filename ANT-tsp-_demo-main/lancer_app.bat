@echo off
cd /d "%~dp0"
echo ============================================
echo Application ACO - Colonies de Fourmis
echo ============================================
echo.

REM Vérification de l'environnement virtuel
if not exist .venv (
    echo [ERREUR] Environnement virtuel non trouve
    echo Veuillez d'abord executer : installer.bat
    echo.
    pause
    exit /b 1
)

echo Activation de l'environnement virtuel...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo [OK] Environnement virtuel active
echo.

echo Lancement de l'interface graphique Streamlit...
echo L'application va s'ouvrir dans votre navigateur...
echo.
streamlit run app_streamlit.py

echo.
pause

