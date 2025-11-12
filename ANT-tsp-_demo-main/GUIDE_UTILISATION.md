# 🐜 Guide d'Utilisation - Application ACO (Colonies de Fourmis)

## 🚀 Démarrage Rapide

### Installation
1. Double-cliquez sur `installer.bat` pour installer toutes les dépendances
2. Patientez pendant l'installation de Python, pip et des bibliothèques

### Lancement de l'Application
1. Double-cliquez sur `lancer_app.bat`
2. L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : http://localhost:8501

---

## 📊 Utilisation de l'Interface Streamlit

### Onglet 1 : Simulation Interactive

#### Configuration des Paramètres (Barre Latérale Gauche)

**Paramètres du Problème TSP :**
- **Nombre de villes** : 5 à 500 (slider)
- **Graine aléatoire (seed)** : pour reproduire les mêmes résultats

**Paramètres de l'Algorithme ACO :**
- **Nombre de fourmis** : 5 à 3000
- **Alpha (α)** : 0.1 à 5.0 — Influence des phéromones
- **Beta (β)** : 0.5 à 15.0 — Influence de la distance (visibilité)
- **Persistance (ρ)** : 0.1 à 0.95 — Taux de persistance des phéromones (1-évaporation)
- **Q** : 10 à 500 — Constante de dépôt de phéromones

**Paramètres d'Exécution :**
- **Nombre de cycles** : 1 à 5000
- **Mise à jour tous les X cycles** : 1 à 50 — Fréquence de rafraîchissement de l'affichage

#### Lancement de la Simulation
1. Ajustez les paramètres selon vos besoins
2. Cliquez sur **"🚀 Lancer l'optimisation"**
3. Observez en temps réel :
   - Le meilleur chemin trouvé
   - Les statistiques de convergence
   - La barre de progression

#### Résultats Affichés
- **Graphique du meilleur chemin** : visualisation du circuit optimal trouvé
- **Graphique de convergence** : évolution de la qualité de la solution au fil des cycles
- **Statistiques temps réel** : meilleure longueur du cycle, moyenne, meilleur global
- **Résumé final** avec 3 onglets :
  - Meilleur chemin final
  - Matrice des phéromones (heatmap)
  - Tableau récapitulatif de tous les cycles

---

### Onglet 2 : Benchmarks / Comparaison

#### Lancer des Benchmarks

**Configuration :**
1. Cochez **"🚀 Mode parallèle"** pour utiliser tous les cœurs de votre processeur (recommandé)
2. Le système affiche le nombre de cœurs disponibles et le speedup estimé
3. Cliquez sur **"🚀 Lancer les benchmarks"**

**Durée Estimée :**
- Mode séquentiel : 8 à 12 heures
- Mode parallèle (12 cœurs) : 1h30 à 3 heures

**Résultats :**
- Les résultats sont sauvegardés dans `exports/benchmarks.csv`
- 168 configurations testées organisées en 9 séries scientifiques

---

### Onglets 3 à 11 : Analyses Scientifiques (9 Séries)

Après avoir lancé les benchmarks, explorez les 9 séries d'analyses :

#### 1️⃣ Série 1 : Nombre de Villes (Scalabilité)
- **Question** : Comment le temps d'exécution évolue-t-il avec le nombre de villes ?
- **Variable testée** : Nombre de villes (10 → 500)
- **Variables fixes** : m=n, cycles=300, seed=42
- **Graphiques** :
  - Temps d'exécution vs Nombre de villes
  - Qualité de la solution vs Nombre de villes
- **Analyses** : Ratio de croissance, complexité observée

#### 2️⃣ Série 2 : Nombre de Fourmis (Rendements Décroissants)
- **Question** : Plus de fourmis = meilleure solution ? À quel coût ?
- **Variable testée** : Nombre de fourmis (10 → 3000)
- **Variables fixes** : n=300, cycles=300, seed=42
- **Graphiques** :
  - Coût du nombre de fourmis (temps linéaire)
  - Rendements décroissants (qualité)
- **Analyses** : Point d'inflexion, amélioration moyenne par doublement

#### 3️⃣ Série 3 : Nombre de Cycles (Convergence)
- **Question** : À partir de combien de cycles l'algorithme converge-t-il ?
- **Variable testée** : Nombre de cycles (50 → 2000)
- **Variables fixes** : n=200, m=200, seed=42
- **Graphiques** :
  - Courbe de convergence
  - Amélioration cumulée (%)
- **Analyses** : Amélioration après 100 cycles, plateau de convergence

#### 4️⃣ Série 4 : Alpha (Phéromones)
- **Question** : Quelle est l'influence des phéromones sur la qualité ?
- **Variable testée** : Alpha (0.1 → 5.0)
- **Variables fixes** : n=100, m=100, cycles=300, beta=5.0, seed=42
- **Graphiques** : Influence sur la qualité avec ligne de référence (alpha=1.0)
- **Analyses** : Alpha optimal observé, interprétation

#### 5️⃣ Série 5 : Beta (Visibilité)
- **Question** : Quelle est l'importance de la distance dans les choix ?
- **Variable testée** : Beta (0.5 → 15.0)
- **Variables fixes** : n=100, m=100, cycles=300, alpha=1.0, seed=42
- **Graphiques** : Influence sur la qualité avec ligne de référence (beta=5.0)
- **Analyses** : Beta optimal observé, comportement glouton vs explorateur

#### 6️⃣ Série 6 : Persistance p (Évaporation)
- **Question** : Mémoire longue ou courte ?
- **Variable testée** : Persistance p (0.1 → 0.95)
- **Variables fixes** : n=100, m=100, cycles=300, alpha=1.0, beta=5.0, seed=42
- **Graphiques** : Influence de l'évaporation avec ligne de référence (p=0.5)
- **Analyses** : p optimal observé, interprétation

#### 7️⃣ Série 7 : Ratio m/n (Fourmis/Villes)
- **Question** : Quel est le ratio optimal entre fourmis et villes ?
- **Variable testée** : Ratio m/n (0.1 → 5.0)
- **Variables fixes** : n=200, cycles=300, seed=42
- **Graphiques** :
  - Qualité vs Ratio
  - Coût vs Ratio
- **Analyses** : Ratio optimal, interprétation par plages

#### 8️⃣ Série 8 : Reproductibilité (Stabilité)
- **Question** : L'algorithme est-il stable et reproductible ?
- **Variables testées** : 5 graines aléatoires × 5 tailles
- **Variables fixes** : cycles=300
- **Graphiques** : Box plot de la distribution par taille
- **Analyses** : Variance, stabilité (mean, std, min, max)

#### 9️⃣ Série 9 : Configurations Extrêmes (Limites)
- **Question** : Quelles sont les limites du système ?
- **Configurations** : Top 10 les plus exigeantes (jusqu'à 500×500×300)
- **Graphiques** : Barres horizontales avec code couleur (rouge > 1000s)
- **Analyses** : Configuration la plus lourde, mémoire estimée

---

## ⚙️ Configurations Recommandées

### Pour Débuter (Démo Rapide - 5 secondes)
- Villes : 15
- Fourmis : 15
- Cycles : 50
- Alpha : 1.0
- Beta : 5.0
- Persistance : 0.5
- Q : 100

### Pour Analyse Scientifique (30 secondes)
- Villes : 100
- Fourmis : 100
- Cycles : 300
- Alpha : 1.0
- Beta : 5.0
- Persistance : 0.5
- Q : 100

### Pour Tests de Performance (2-3 minutes)
- Villes : 300
- Fourmis : 300
- Cycles : 300
- Alpha : 1.0
- Beta : 5.0
- Persistance : 0.5
- Q : 100

### Configuration Extrême (4-5 minutes)
- Villes : 500
- Fourmis : 500
- Cycles : 300
- Alpha : 1.0
- Beta : 5.0
- Persistance : 0.5
- Q : 100

---

## 🔧 Dépannage

### L'application ne démarre pas
1. Vérifiez que Python est installé : `python --version`
2. Réinstallez les dépendances : relancez `installer.bat`
3. Activez manuellement l'environnement virtuel :
   ```
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

### L'application est lente
1. Réduisez le nombre de villes ou de cycles
2. Augmentez le paramètre "Mise à jour tous les X cycles" à 10 ou 20
3. Utilisez le mode parallèle pour les benchmarks

### Les benchmarks ne se lancent pas
1. Vérifiez que le fichier `exports/benchmarks.csv` n'est pas ouvert dans Excel
2. Assurez-vous d'avoir suffisamment d'espace disque
3. Utilisez le mode séquentiel si le mode parallèle pose problème

### Erreur de mémoire
1. Réduisez le nombre de villes et de fourmis
2. Fermez les autres applications
3. Ne dépassez pas 500 villes / 500 fourmis simultanément

---

## 📚 Interprétation des Résultats

### Paramètres Alpha et Beta
- **Alpha élevé (> 2.0)** : L'algorithme suit fortement les phéromones (risque de convergence prématurée)
- **Alpha faible (< 0.5)** : L'algorithme explore plus, mais converge plus lentement
- **Beta élevé (> 10.0)** : Comportement glouton, privilégie les villes proches
- **Beta faible (< 2.0)** : Plus d'exploration, solutions potentiellement meilleures

### Paramètre de Persistance p
- **p élevé (> 0.8)** : Mémoire longue, phéromones persistent longtemps
- **p faible (< 0.3)** : Mémoire courte, oubli rapide des anciennes solutions

### Nombre de Cycles
- **Convergence rapide** : < 100 cycles pour petits problèmes (n < 50)
- **Convergence standard** : 200-300 cycles pour problèmes moyens (n = 100-300)
- **Convergence lente** : > 500 cycles pour grands problèmes (n > 300)

### Ratio Fourmis/Villes
- **Ratio < 1.0** : Peu de fourmis, exploration limitée
- **Ratio ≈ 1.0** : Optimal dans la plupart des cas
- **Ratio > 2.0** : Rendements décroissants, coût élevé

---

## 💡 Astuces et Bonnes Pratiques

1. **Utilisez toujours la même graine aléatoire (seed)** pour comparer différentes configurations
2. **Commencez avec des paramètres standards** (α=1.0, β=5.0, ρ=0.5) puis ajustez progressivement
3. **Pour des démos** : utilisez des petites instances (15 villes, 50 cycles)
4. **Pour des analyses scientifiques** : utilisez les 9 séries de benchmarks
5. **Mode parallèle** : activez-le systématiquement pour les benchmarks complets
6. **Patience** : les benchmarks complets prennent 1h30 à 3h en mode parallèle

---

## 📁 Fichiers Générés

- `exports/benchmarks.csv` : Résultats complets des 168 configurations testées
- `exports/benchmarks_aco.csv` : Benchmarks additionnels (si générés)

---

## 🎓 Pour Aller Plus Loin

### Commande CLI pour Benchmarks
Vous pouvez également lancer les benchmarks en ligne de commande :

```bash
# Mode séquentiel
python run_benchmarks.py

# Mode parallèle (tous les cœurs)
python run_benchmarks.py --parallel

# Mode parallèle (4 cœurs)
python run_benchmarks.py --parallel --jobs 4
```

### Architecture du Projet
```
model/          → Logique métier (ACO, benchmarks)
view/           → Interface utilisateur (Streamlit)
controller/     → Contrôleurs (orchestration)
exports/        → Résultats CSV
```

---

## ✨ Résumé

Cette application vous permet de :
- ✅ Visualiser l'algorithme ACO en temps réel
- ✅ Tester différentes configurations de paramètres
- ✅ Lancer des benchmarks scientifiques complets (168 configurations)
- ✅ Analyser les résultats avec 9 séries d'analyses graphiques
- ✅ Comprendre l'influence de chaque paramètre
- ✅ Optimiser les performances (mode parallèle, jusqu'à 12x plus rapide)

**Bon voyage dans le monde des colonies de fourmis ! 🐜**

