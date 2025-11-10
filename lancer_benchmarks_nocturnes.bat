@echo off
echo ============================================================
echo    LANCEMENT DES BENCHMARKS NOCTURNES ACO
echo    81 configurations - 8-12 heures
echo ============================================================
echo.
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo.
echo Lancement des benchmarks...
echo Vous pouvez minimiser cette fenetre et aller dormir !
echo.
echo Les resultats seront dans: exports\benchmarks.csv
echo.
echo ============================================================
echo.

python run_benchmarks.py

echo.
echo ============================================================
echo    BENCHMARKS TERMINES !
echo ============================================================
echo.
echo Consultez les resultats dans exports\benchmarks.csv
echo Ou lancez: streamlit run app_streamlit.py
echo.
pause

