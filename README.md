# 🐜 Application d'Optimisation par Colonies de Fourmis (ACO)

Cette application permet de visualiser en temps réel l'algorithme d'optimisation par colonies de fourmis appliqué au problème du voyageur de commerce (TSP).

## ✨ Fonctionnalités

- ✅ **Visualisation en temps réel** du meilleur chemin trouvé
- 📊 **Graphiques de convergence** pour suivre l'amélioration
- 🎛️ **Contrôles interactifs** pour tous les paramètres
- 🔥 **Heatmap des phéromones** pour visualiser l'intensité des chemins
- 📈 **Statistiques détaillées** par cycle
- 💾 **Historique complet** de l'optimisation

## 🚀 Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 📱 Lancement de l'application

### Interface Graphique (Streamlit)

Pour lancer l'interface graphique interactive :

```bash
streamlit run app_streamlit.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

### Interface Console

Pour lancer la version console :

```bash
python controller/main_controller.py
```

## 🎮 Utilisation de l'interface Streamlit

### Paramètres disponibles :

#### Problème TSP
- **Nombre de villes** (5-50) : Le nombre de villes à visiter
- **Graine aléatoire (seed)** : Pour la reproductibilité des résultats

#### Paramètres ACO
- **Nombre de fourmis** : Le nombre de fourmis dans la colonie
- **Alpha (α)** : Influence des phéromones dans le choix du chemin (0.1-5.0)
- **Beta (β)** : Influence de la distance/visibilité dans le choix (0.1-10.0)
- **Rho (ρ)** : Taux d'évaporation des phéromones (0.1-0.9)
- **Q** : Constante de dépôt de phéromones (10-500)

#### Exécution
- **Nombre de cycles** : Nombre d'itérations de l'algorithme (1-200)
- **Mise à jour tous les X cycles** : Fréquence de rafraîchissement de l'affichage

### Fonctionnalités :

1. **Visualisation en temps réel** : Voir l'évolution du meilleur chemin au fur et à mesure des cycles
2. **Graphique de convergence** : Observer la progression de l'optimisation
3. **Statistiques détaillées** : Métriques de performance pour chaque cycle
4. **Matrice de phéromones** : Visualiser les niveaux de phéromones sur chaque arête
5. **Résumé final** : Tableau récapitulatif de tous les cycles

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
├── app_streamlit.py          # Application Streamlit (interface graphique)
├── requirements.txt          # Dépendances Python
├── controller/
│   └── main_controller.py   # Contrôleur principal (version console)
├── model/
│   ├── aco_core.py          # Moteur ACO
│   ├── ant_model.py         # Modèle de fourmi
│   └── tsp_model.py         # Modèle TSP
└── view/
    ├── console_view.py      # Vue console
    └── streamlit_view.py    # Vue Streamlit
```

## 🎯 Exemples de paramètres

### Configuration rapide (pour tests)
- Villes : 10
- Fourmis : 10
- Cycles : 20
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

### Configuration standard
- Villes : 20
- Fourmis : 20
- Cycles : 50
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

### Configuration intensive
- Villes : 50
- Fourmis : 50
- Cycles : 100
- Alpha : 1.0, Beta : 5.0, Rho : 0.5, Q : 100

## ⚠️ Notes

- Plus le nombre de villes et de cycles augmente, plus le calcul prend du temps
- Le paramètre "Mise à jour tous les X cycles" permet d'accélérer l'affichage pour les grandes exécutions
- La graine aléatoire permet de reproduire exactement les mêmes résultats

## 📝 Licence

Projet éducatif pour l'apprentissage de l'optimisation par colonies de fourmis.
