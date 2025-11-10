# 🐜 Application d'Optimisation par Colonies de Fourmis (ACO)

Cette application permet de visualiser en temps réel l'algorithme d'optimisation par colonies de fourmis appliqué au problème du voyageur de commerce (TSP).

## ⚡ OPTIMISATIONS DE PERFORMANCE

**Cette version est hautement optimisée avec NumPy vectorisé** et peut gérer efficacement :
- ✅ **500+ villes**
- ✅ **500+ fourmis**  
- ✅ **5000+ cycles**

**Speedup : ~25-30x** par rapport à la version avec boucles Python

### Optimisations principales :
1. **Vectorisation complète** des calculs de matrices (distances, visibilité)
2. **Précalcul** des matrices tau^alpha et eta^beta par cycle
3. **Dépôt de phéromones vectorisé** avec `np.add.at`
4. **Affichage périodique** au lieu de chaque cycle
5. **Broadcasting NumPy** pour opérations massivement parallèles

Voir [OPTIMISATIONS_COMPLETES.md](OPTIMISATIONS_COMPLETES.md) pour les détails complets.

## ✨ Fonctionnalités

### Interface Streamlit Interactive
- 🔬 **Onglet Simulation ACO** : Visualisation en temps réel du meilleur chemin trouvé
- 📊 **Onglet Benchmarks / Comparaison** : Tests de performance automatisés
- 📈 **Graphiques de convergence** pour suivre l'amélioration
- 🎛️ **Contrôles interactifs** pour tous les paramètres
- 🔥 **Heatmap des phéromones** pour visualiser l'intensité des chemins
- 📉 **Statistiques détaillées** par cycle
- 💾 **Historique complet** de l'optimisation
- 📥 **Export CSV** des résultats de benchmarks

### Système de Benchmarks
- ✅ **100+ configurations de test** (du plus petit au très grand)
- ✅ **Tests nocturnes** : Suite exhaustive de 8-12 heures
- ✅ **Visualisation graphique** : 4 types de graphiques de comparaison
- ✅ **CLI incluse** : `python run_benchmarks.py`
- ✅ **Mode rapide** : Tests en 3 minutes
- ✅ **Mode complet** : Tests exhaustifs toute la nuit

## 🚀 Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 📱 Lancement de l'application

### Interface Graphique (Streamlit) - RECOMMANDÉ

Pour lancer l'interface graphique interactive :

```bash
streamlit run app_streamlit.py
```

Ou double-cliquez sur `lancer_app.bat` (Windows)

L'application s'ouvrira automatiquement dans votre navigateur avec **2 onglets** :

#### 🔬 Onglet "Simulation ACO"
- Configurez vos paramètres (villes, fourmis, cycles, alpha, beta, rho, Q)
- Lancez l'optimisation et visualisez en temps réel
- Consultez les résultats finaux (meilleur chemin, phéromones, statistiques)

#### 📊 Onglet "Benchmarks / Comparaison"
- Lancez des tests de performance automatisés
- **Mode rapide** (3 min) : 3 configurations légères
- **Mode complet** (8-12h) : 100+ configurations du plus petit au très grand
- Comparez différentes configurations
- Visualisez l'impact de chaque paramètre (4 types de graphiques)
- Exportez les résultats en CSV

### Benchmarks en Ligne de Commande

```bash
# Tests rapides (3 minutes)
python run_benchmarks.py --quick

# Tests exhaustifs COMPLETS (8-12 heures) - PARFAIT POUR LA NUIT !
python run_benchmarks.py

# Fichier de sortie personnalisé
python run_benchmarks.py --output mes_resultats.csv

# Ajouter aux résultats existants
python run_benchmarks.py --append
```

### Interface Console (Legacy)

Pour lancer la version console basique :

```bash
python controller/main_controller.py
```

## 🎮 Utilisation de l'interface Streamlit

### Paramètres disponibles :

#### Problème TSP
- **Nombre de villes** (5-500) : Le nombre de villes à visiter
- **Graine aléatoire (seed)** : Pour la reproductibilité des résultats

#### Paramètres ACO
- **Nombre de fourmis** (5-500) : Le nombre de fourmis dans la colonie
- **Alpha (α)** : Influence des phéromones dans le choix du chemin (0.1-5.0)
- **Beta (β)** : Influence de la distance/visibilité dans le choix (0.1-10.0)
- **Rho (ρ)** : Taux d'évaporation des phéromones (0.1-0.9)
- **Q** : Constante de dépôt de phéromones (10-500)

#### Exécution
- **Nombre de cycles** (1-5000) : Nombre d'itérations de l'algorithme
- **Mise à jour tous les X cycles** : Fréquence de rafraîchissement de l'affichage

### Fonctionnalités :

1. **Visualisation en temps réel** : Voir l'évolution du meilleur chemin au fur et à mesure des cycles
2. **Graphique de convergence** : Observer la progression de l'optimisation
3. **Statistiques détaillées** : Métriques de performance pour chaque cycle
4. **Matrice de phéromones** : Visualiser les niveaux de phéromones sur chaque arête
5. **Résumé final** : Tableau récapitulatif de tous les cycles
6. **Benchmarks automatisés** : Testez 100+ configurations en une nuit

## 📊 Système de Benchmarks (NOUVEAU !)

### Configurations de Test

Le mode complet teste **100+ configurations** réparties en 7 phases :

#### Phase 1: Petits problèmes (10-30 villes)
- 12 configurations
- Temps: ~1-5 minutes par config
- Idéal pour tester rapidement les paramètres

#### Phase 2: Problèmes moyens (50-75 villes)
- 9 configurations
- Temps: ~2-10 minutes par config
- Sweet spot performance/qualité

#### Phase 3: Grands problèmes (100-150 villes)
- 11 configurations
- Temps: ~10-30 minutes par config
- Problèmes réalistes

#### Phase 4: Très grands problèmes (200-300 villes)
- 11 configurations
- Temps: ~30 min - 2h par config
- Stress test

#### Phase 5: Problèmes massifs (400-500 villes)
- 11 configurations incluant test ULTIME : 500 villes, 500 fourmis, 1000 cycles !
- Temps: ~1-4 heures par config
- Limite machine

#### Phase 6: Tests alpha/beta
- 12 configurations (4 alpha × 3 beta sur 100 villes)
- Temps: ~15 minutes par config
- Étude d'impact des paramètres

#### Phase 7: Tests de robustesse
- 15 configurations (5 seeds × 3 tailles)
- Temps: ~5-30 minutes par config
- Vérification reproductibilité

### Métriques Collectées

Pour chaque configuration :
- ⏱️ **runtime_sec** : Temps total d'exécution
- 🔄 **time_per_cycle** : Temps moyen par cycle
- 🏆 **best_len_global** : Meilleure solution trouvée
- 📊 **mean_len_final** : Qualité moyenne finale
- 📈 **improvement_pct** : Pourcentage d'amélioration
- 🎯 Tous les paramètres (n, m, cycles, alpha, beta, p, Q, seed)

### Graphiques Générés

L'onglet Benchmarks génère automatiquement :
1. **Temps d'exécution par configuration** (barres horizontales)
2. **Qualité des solutions** (barres horizontales)
3. **Impact du nombre de fourmis** (2 graphiques: temps + qualité)
4. **Impact du nombre de villes** (2 graphiques: temps + temps/cycle)

### Temps Estimés

| Mode | Configurations | Temps Estimé | Quand Utiliser |
|------|---------------|--------------|----------------|
| **Rapide** | 3 configs | ~3 minutes | Test rapide avant grosse exécution |
| **Complet** | 100+ configs | **8-12 heures** | **LAISSER TOURNER LA NUIT !** |

## 📊 Comprendre les résultats

- **Meilleur du cycle** : La meilleure solution trouvée dans le cycle actuel
- **Moyenne du cycle** : La longueur moyenne de tous les tours du cycle
- **Meilleur global** : La meilleure solution trouvée depuis le début
- **Amélioration** : Le pourcentage d'amélioration par rapport à la solution initiale

## 🔬 Algorithme ACO

L'algorithme ACO s'inspire du comportement des fourmis réelles :

1. Les fourmis construisent des solutions de manière probabiliste
2. Elles déposent des phéromones sur leur chemin
3. Les meilleures solutions accumulent plus de phéromones
4. Les fourmis suivent préférentiellement les chemins avec plus de phéromones

## 📁 Structure du projet

```
ant_demo/
├── app_streamlit.py          # Application Streamlit avec 2 onglets
├── run_benchmarks.py         # CLI pour benchmarks nocturnes
├── test_benchmark_system.py  # Script de test rapide
├── requirements.txt          # Dépendances Python
├── controller/
│   ├── main_controller.py        # Contrôleur principal (console)
│   └── benchmark_controller.py   # Contrôleur de benchmarks
├── model/
│   ├── aco_core.py          # Moteur ACO optimisé NumPy
│   ├── ant_model.py         # Modèle de fourmi
│   ├── tsp_model.py         # Modèle TSP
│   └── benchmark.py         # Système de benchmarks
├── view/
│   ├── console_view.py      # Vue console
│   └── streamlit_view.py    # Vue Streamlit
├── exports/                  # Résultats des benchmarks (CSV)
└── docs/                     # Documentation complète
    ├── GUIDE_BENCHMARKS.md
    ├── README_COMPLET.md
    └── DEMARRAGE_RAPIDE.md
```

## 🎯 Exemples de paramètres

### Pour Simulation Interactive

#### Configuration rapide (pour tests)
- Villes : 20
- Fourmis : 20
- Cycles : 50
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

#### Configuration standard
- Villes : 50
- Fourmis : 50
- Cycles : 100
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

#### Configuration intensive
- Villes : 100
- Fourmis : 100
- Cycles : 200
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

#### Configuration extrême (plusieurs minutes)
- Villes : 300
- Fourmis : 300
- Cycles : 500
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

#### Configuration ULTIME (30+ minutes)
- Villes : 500
- Fourmis : 500
- Cycles : 1000
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

### Pour Benchmarks Nocturnes

```bash
# Lancer les benchmarks complets (8-12h)
# ⚠️ À faire avant de dormir !
python run_benchmarks.py

# Le matin, consultez les résultats dans:
# - exports/benchmarks.csv
# - Ou via l'onglet Benchmarks de Streamlit
```

Les 100+ configurations testeront automatiquement :
- Toutes les tailles (10 → 500 villes)
- Différents ratios fourmis/villes
- Impact du nombre de cycles (100 → 1000)
- Variations alpha/beta
- Reproductibilité (différents seeds)

## 💡 Conseils d'Utilisation

### Pour l'onglet Simulation
- **Débutant** : Commencez avec 20-30 villes
- **Exploration** : Essayez différents alpha/beta
- **Visualisation** : Réglez l'intervalle de mise à jour pour l'animation
- **Performance** : Désactivez la mise à jour fréquente pour grandes instances

### Pour l'onglet Benchmarks
- **Test rapide** : Cochez "Mode rapide" (3 min)
- **Analyse complète** : Lancez le mode complet **le soir avant de dormir**
- **Export** : Téléchargez le CSV pour analyses externes (Excel, Python, R)
- **Comparaison** : Relancez avec --append pour comparer différentes optimisations du code

## ⚠️ Notes

- Plus le nombre de villes et de cycles augmente, plus le calcul prend du temps
- Le paramètre "Mise à jour tous les X cycles" permet d'accélérer l'affichage pour les grandes exécutions
- La graine aléatoire permet de reproduire exactement les mêmes résultats

## 📝 Licence

Projet éducatif pour l'apprentissage de l'optimisation par colonies de fourmis.
