"""
Documentation des fonctionnalités de l'application Streamlit ACO
"""

# FONCTIONNALITÉS IMPLÉMENTÉES

## 1. PARAMÈTRES CONFIGURABLES

### Paramètres du problème TSP
- Nombre de villes (slider 5-50)
- Graine aléatoire pour la reproductibilité

### Paramètres de l'algorithme ACO
- Nombre de fourmis (slider 5-100)
- Alpha : influence des phéromones (slider 0.1-5.0)
- Beta : influence de la visibilité/distance (slider 0.1-10.0)
- Rho : taux d'évaporation des phéromones (slider 0.1-0.9)
- Q : constante de dépôt de phéromones (slider 10-500)

### Paramètres d'exécution
- Nombre de cycles (slider 1-200)
- Intervalle de mise à jour de l'affichage (slider 1-20)

## 2. VISUALISATIONS EN TEMPS RÉEL

### A. Graphique du meilleur chemin
- Affichage des villes avec numéros
- Tracé du meilleur chemin trouvé
- Flèche indiquant le point de départ
- Longueur du tour affichée dans le titre
- Mise à jour en temps réel pendant l'optimisation

### B. Graphique de convergence
- Meilleur tour de chaque cycle (vert)
- Longueur moyenne de chaque cycle (orange)
- Meilleur tour global historique (rouge)
- Légende et grille pour faciliter la lecture

### C. Statistiques en temps réel
- Meilleur du cycle (carte métrique)
- Moyenne du cycle (carte métrique)
- Meilleur global (carte métrique avec delta)
- Statistiques détaillées (min, max, écart-type)

## 3. BARRE DE PROGRESSION

- Barre de progression visuelle (0-100%)
- Texte de statut indiquant le cycle actuel
- Meilleure longueur affichée en temps réel

## 4. RÉSULTATS FINAUX (3 ONGLETS)

### Onglet 1 : Meilleur chemin
- Visualisation finale du meilleur chemin trouvé
- Couleur distinctive (vert foncé)
- Longueur affichée
- Tour complet consultable dans un expander

### Onglet 2 : Phéromones
- Heatmap de la matrice des phéromones
- Colormap rouge-jaune pour visualiser l'intensité
- Barre de couleur avec légende
- Aide textuelle pour interpréter la heatmap

### Onglet 3 : Résumé
- Métriques clés (meilleure solution, initiale, amélioration%)
- Tableau DataFrame avec tous les cycles
- Affichage des 10 premiers et 10 derniers cycles

## 5. INTERFACE UTILISATEUR

### Design
- Layout large pour plus d'espace
- Icône de fourmi 🐜
- Titre et sous-titre descriptifs
- Barre latérale pour tous les contrôles

### Feedback utilisateur
- Messages de succès/info/warning
- Spinners pendant les calculs
- Indicateurs de progression
- Instructions claires avant le lancement

### Organisation
- Colonnes pour affichage côte à côte
- Expandeurs pour détails supplémentaires
- Onglets pour organiser les résultats finaux

## 6. PAGE D'ACCUEIL (AVANT LANCEMENT)

- Message d'instructions
- Section "À propos" avec explication de l'algorithme
- Description des paramètres clés
- Mise en page en 2 colonnes

## 7. FONCTIONNALITÉS TECHNIQUES

### Performance
- Mise à jour configurable pour éviter les ralentissements
- Fermeture des figures matplotlib pour libérer la mémoire
- Utilisation de placeholders pour mise à jour in-place

### Données
- Utilisation de pandas DataFrame pour tableaux
- Conservation de l'historique complet
- Statistiques calculées à chaque cycle

### Graphiques
- Matplotlib pour tous les graphiques
- Style cohérent (couleurs, tailles de police)
- Aspect ratio préservé pour le graphique de chemin
- Marges automatiques autour des points

## 8. GESTION D'ERREURS ET CAS LIMITES

- Validation des paramètres via sliders
- Gestion des tours vides
- Gestion des scores nuls dans l'algorithme
- Délais pour animation fluide

## 9. AMÉLIORATIONS POSSIBLES (NON IMPLÉMENTÉES)

- Export des résultats en CSV/JSON
- Comparaison de plusieurs exécutions
- Animation du parcours des fourmis
- Graphique 3D des phéromones
- Sauvegarde/chargement de configurations
- Mode batch pour tests multiples
- Statistiques de variance entre cycles
- Graphique de distribution des longueurs

