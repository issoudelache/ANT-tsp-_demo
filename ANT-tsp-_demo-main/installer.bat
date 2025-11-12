@echo off
echo ============================================
echo Installation - Application ACO
echo ============================================
echo.

REM Vérification de Python
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis : https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Création de l'environnement virtuel
if not exist .venv (
    echo Creation de l'environnement virtuel...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERREUR] Impossible de creer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
) else (
    echo [OK] Environnement virtuel deja existant
)
echo.

REM Activation de l'environnement virtuel
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo [OK] Environnement virtuel active
echo.

REM Mise à jour de pip
echo Mise a jour de pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [ATTENTION] Erreur lors de la mise a jour de pip (non bloquant)
) else (
    echo [OK] pip mis a jour
)
echo.

REM Installation des dépendances
echo Installation des dependances (cela peut prendre quelques minutes)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] Erreur lors de l'installation des dependances
    pause
    exit /b 1
)
echo.
echo [OK] Toutes les dependances sont installees
echo.

echo ============================================
echo Installation terminee avec succes !
echo ============================================
echo.
echo Vous pouvez maintenant lancer l'application avec : lancer_app.bat
echo.
pause

