"""
Contrôleur pour gérer les scénarios de benchmark de l'algorithme ACO.

Ce module définit les configurations par défaut à tester et orchestre
l'exécution des benchmarks.
"""
from typing import List
import pandas as pd

from model.benchmark import RunConfig, run_benchmarks, save_benchmarks, load_benchmarks


def get_default_benchmark_configs() -> List[RunConfig]:
    """
    Retourne une liste exhaustive de configurations de test pour les benchmarks.

    Suite complète du plus petit au très grand, idéale pour tests nocturnes.
    Progression: 10 → 20 → 30 → 50 → 75 → 100 → 150 → 200 → 300 → 400 → 500 villes

    Ces scénarios permettent d'évaluer l'impact de différents paramètres :
    - Variation du nombre de villes (n)
    - Variation du nombre de fourmis (m)
    - Variation du nombre de cycles
    - Variation des paramètres alpha/beta

    Temps estimé total: 8-12 heures

    Returns:
        Liste de configurations RunConfig
    """
    configs = []

    # ========== PHASE 1: PETITS PROBLÈMES (10-30 villes) ==========
    # Exploration rapide avec beaucoup de cycles pour convergence fine

    # Série 10 villes
    configs.extend([
        RunConfig(n=10, m=10, cycles=100, seed=42),
        RunConfig(n=10, m=20, cycles=100, seed=42),
        RunConfig(n=10, m=5, cycles=100, seed=42),
    ])

    # Série 20 villes
    configs.extend([
        RunConfig(n=20, m=10, cycles=100, seed=42),
        RunConfig(n=20, m=20, cycles=100, seed=42),
        RunConfig(n=20, m=40, cycles=100, seed=42),
        RunConfig(n=20, m=20, cycles=200, seed=42),
    ])

    # Série 30 villes - tests variés
    configs.extend([
        RunConfig(n=30, m=15, cycles=100, seed=42),
        RunConfig(n=30, m=30, cycles=100, seed=42),
        RunConfig(n=30, m=60, cycles=100, seed=42),
        RunConfig(n=30, m=30, cycles=200, seed=42),
        RunConfig(n=30, m=30, cycles=500, seed=42),
    ])

    # ========== PHASE 2: PROBLÈMES MOYENS (50-75 villes) ==========

    # Série 50 villes
    configs.extend([
        RunConfig(n=50, m=25, cycles=100, seed=42),
        RunConfig(n=50, m=50, cycles=100, seed=42),
        RunConfig(n=50, m=100, cycles=100, seed=42),
        RunConfig(n=50, m=50, cycles=200, seed=42),
        RunConfig(n=50, m=50, cycles=500, seed=42),
    ])

    # Série 75 villes
    configs.extend([
        RunConfig(n=75, m=50, cycles=100, seed=42),
        RunConfig(n=75, m=75, cycles=100, seed=42),
        RunConfig(n=75, m=100, cycles=100, seed=42),
        RunConfig(n=75, m=75, cycles=200, seed=42),
    ])

    # ========== PHASE 3: GRANDS PROBLÈMES (100-150 villes) ==========

    # Série 100 villes
    configs.extend([
        RunConfig(n=100, m=50, cycles=100, seed=42),
        RunConfig(n=100, m=100, cycles=100, seed=42),
        RunConfig(n=100, m=150, cycles=100, seed=42),
        RunConfig(n=100, m=100, cycles=200, seed=42),
        RunConfig(n=100, m=100, cycles=500, seed=42),
        RunConfig(n=100, m=100, cycles=1000, seed=42),
    ])

    # Série 150 villes
    configs.extend([
        RunConfig(n=150, m=100, cycles=100, seed=42),
        RunConfig(n=150, m=150, cycles=100, seed=42),
        RunConfig(n=150, m=200, cycles=100, seed=42),
        RunConfig(n=150, m=150, cycles=200, seed=42),
        RunConfig(n=150, m=150, cycles=500, seed=42),
    ])

    # ========== PHASE 4: TRÈS GRANDS PROBLÈMES (200-300 villes) ==========

    # Série 200 villes
    configs.extend([
        RunConfig(n=200, m=100, cycles=100, seed=42),
        RunConfig(n=200, m=150, cycles=100, seed=42),
        RunConfig(n=200, m=200, cycles=100, seed=42),
        RunConfig(n=200, m=200, cycles=200, seed=42),
        RunConfig(n=200, m=200, cycles=500, seed=42),
        RunConfig(n=200, m=200, cycles=1000, seed=42),
    ])

    # Série 300 villes
    configs.extend([
        RunConfig(n=300, m=150, cycles=100, seed=42),
        RunConfig(n=300, m=200, cycles=100, seed=42),
        RunConfig(n=300, m=300, cycles=100, seed=42),
        RunConfig(n=300, m=300, cycles=200, seed=42),
        RunConfig(n=300, m=300, cycles=500, seed=42),
    ])

    # ========== PHASE 5: PROBLÈMES MASSIFS (400-500 villes) ==========
    # STRESS TEST - Ces tests vont prendre plusieurs heures chacun

    # Série 400 villes
    configs.extend([
        RunConfig(n=400, m=200, cycles=100, seed=42),
        RunConfig(n=400, m=300, cycles=100, seed=42),
        RunConfig(n=400, m=400, cycles=100, seed=42),
        RunConfig(n=400, m=400, cycles=200, seed=42),
        RunConfig(n=400, m=400, cycles=500, seed=42),
    ])

    # Série 500 villes - ULTIME STRESS TEST
    configs.extend([
        RunConfig(n=500, m=250, cycles=100, seed=42),
        RunConfig(n=500, m=400, cycles=100, seed=42),
        RunConfig(n=500, m=500, cycles=100, seed=42),
        RunConfig(n=500, m=500, cycles=200, seed=42),
        RunConfig(n=500, m=500, cycles=500, seed=42),
        RunConfig(n=500, m=500, cycles=1000, seed=42),  # Test ultime !
    ])

    # ========== PHASE 6: TESTS DE PARAMÈTRES alpha/beta ==========
    # Tests avec différentes valeurs de paramètres sur problème moyen

    for alpha in [0.5, 1.0, 1.5, 2.0]:
        for beta in [3.0, 5.0, 7.0]:
            configs.append(RunConfig(n=100, m=100, cycles=100, alpha=alpha, beta=beta, seed=42))

    # ========== PHASE 7: TESTS DE ROBUSTESSE (différents seeds) ==========
    # Vérifier la reproductibilité et la variance

    for seed in [42, 123, 456, 789, 2025]:
        configs.extend([
            RunConfig(n=50, m=50, cycles=100, seed=seed),
            RunConfig(n=100, m=100, cycles=100, seed=seed),
            RunConfig(n=200, m=200, cycles=100, seed=seed),
        ])

    return configs


def get_quick_benchmark_configs() -> List[RunConfig]:
    """
    Retourne une liste de configurations pour des tests rapides.
    Utile pour vérifier que tout fonctionne avant de lancer les vrais benchmarks.

    Returns:
        Liste de configurations RunConfig rapides
    """
    configs = [
        RunConfig(n=20, m=20, cycles=20, seed=42),
        RunConfig(n=30, m=30, cycles=20, seed=42),
        RunConfig(n=40, m=40, cycles=20, seed=42),
    ]

    return configs


def run_default_benchmarks(quick_mode: bool = False) -> pd.DataFrame:
    """
    Construit une liste de RunConfig à partir des scénarios par défaut
    et appelle run_benchmarks(configs).

    Args:
        quick_mode: Si True, utilise des configurations rapides pour tests

    Returns:
        DataFrame avec les résultats des benchmarks
    """
    if quick_mode:
        print("Mode rapide activé - Tests légers")
        configs = get_quick_benchmark_configs()
    else:
        print("Lancement des benchmarks complets")
        configs = get_default_benchmark_configs()

    print(f"\n{len(configs)} configurations à tester\n")

    # Exécuter les benchmarks
    df = run_benchmarks(configs)

    return df


def run_and_save_benchmarks(output_path: str = "exports/benchmarks.csv",
                            quick_mode: bool = False,
                            append: bool = False) -> pd.DataFrame:
    """
    Lance les benchmarks par défaut et sauvegarde les résultats.

    Args:
        output_path: Chemin du fichier CSV de sortie
        quick_mode: Si True, utilise des tests rapides
        append: Si True, ajoute aux résultats existants au lieu de les écraser

    Returns:
        DataFrame avec les résultats
    """
    # Exécuter les benchmarks
    df = run_default_benchmarks(quick_mode=quick_mode)

    # Sauvegarder
    if append:
        from model.benchmark import append_benchmarks
        append_benchmarks(df, output_path)
    else:
        save_benchmarks(df, output_path)

    return df

