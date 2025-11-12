# 🐜 Application ACO - Optimisation par Colonies de Fourmis

Démonstrateur interactif et scientifique de l'algorithme d'optimisation par colonies de fourmis (ACO) appliqué au problème du voyageur de commerce (TSP).

## 🚀 Installation et Lancement

### 1. Installation
Double-cliquez sur **`installer.bat`** pour installer toutes les dépendances.

### 2. Lancement
Double-cliquez sur **`lancer_app.bat`** pour démarrer l'application.

L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse : http://localhost:8501

---

## 📚 Documentation

- **[GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)** : Guide complet d'utilisation de l'application
- **[DESCRIPTION_DEMONSTRATEUR.md](DESCRIPTION_DEMONSTRATEUR.md)** : Description détaillée du démonstrateur et de ses fonctionnalités

---

## ⚡ Démarrage Rapide

**Configuration recommandée pour une démo rapide (5 secondes) :**
- Villes : 15
- Fourmis : 15
- Cycles : 50
- Alpha : 1.0, Beta : 5.0, Persistance : 0.5

---

## 🎯 Principales Fonctionnalités

✅ **Simulation interactive** avec visualisation temps réel  
✅ **Système de benchmarks** (168 configurations scientifiques)  
✅ **Mode parallèle** (jusqu'à 12x plus rapide)  
✅ **9 séries d'analyses** graphiques automatisées  
✅ **Optimisations NumPy** (25-30x speedup)  
✅ **Interface Streamlit** professionnelle  

---

## 📊 Capacités

- Jusqu'à **500 villes** et **500 fourmis**
- Jusqu'à **5000 cycles** d'optimisation
- Benchmarks complets en **1h30-3h** (mode parallèle)
- Export CSV des résultats

---

## 🛠️ Technologies

Python 3.x · NumPy · Streamlit · Plotly · Pandas · Multiprocessing

---

## 🖥️ Utilisation en Ligne de Commande (Optionnel)

Pour lancer les benchmarks sans interface graphique :

```bash
# Activation de l'environnement virtuel
.venv\Scripts\activate

# Benchmarks complets (mode parallèle recommandé)
python run_benchmarks.py --parallel

# Tests rapides
python run_benchmarks.py --quick

# Utiliser 4 cœurs spécifiquement
python run_benchmarks.py --parallel --jobs 4
```

---

## 📁 Structure du Projet

```
├── installer.bat                    # Installation des dépendances
├── lancer_app.bat                   # Lancement de l'application
├── app_streamlit.py                 # Point d'entrée de l'application
├── run_benchmarks.py                # CLI pour benchmarks (optionnel)
├── requirements.txt                 # Dépendances Python
├── README.md                        # Ce fichier
├── GUIDE_UTILISATION.md             # Guide utilisateur complet
├── DESCRIPTION_DEMONSTRATEUR.md     # Description technique
├── model/                           # Logique métier (ACO, TSP, Benchmarks)
├── view/                            # Interface utilisateur (Streamlit)
├── controller/                      # Contrôleurs (orchestration)
└── exports/                         # Résultats CSV
```

---

**Pour toute information complémentaire, consultez les fichiers de documentation.**

