"""
Contrôleur pour gérer les scénarios de benchmark de l'algorithme ACO.

Ce module définit les configurations par défaut à tester et orchestre
l'exécution des benchmarks en mode séquentiel ou parallèle.
"""
from typing import List, Optional
import pandas as pd
from multiprocessing import cpu_count

from model.benchmark import (
    RunConfig,
    run_benchmarks,
    run_benchmarks_parallel,
    save_benchmarks,
    load_benchmarks
)


def get_default_benchmark_configs() -> List[RunConfig]:
    """
    Retourne une liste EXHAUSTIVE de configurations de test SCIENTIFIQUES pour les benchmarks.

    Approche méthodique : variation d'UN SEUL PARAMÈTRE à la fois pour isoler son impact.
    IMPORTANT : Minimum 300 cycles pour toutes les séries (sauf série 3 qui teste les cycles).

    Séries incluses :
    1. Impact du NOMBRE DE VILLES (20 configs: 10→500, m=n, cycles=300)
    2. Impact du NOMBRE DE FOURMIS (25 configs: 300 villes, m=10→3000, cycles=300)
    3. Impact du NOMBRE DE CYCLES (15 configs: 200 villes, m=200, cycles=50→2000)
    4. Impact du paramètre ALPHA (20 configs: 100 villes, m=100, cycles=300, alpha=0.1→5.0)
    5. Impact du paramètre BETA (20 configs: 100 villes, m=100, cycles=300, beta=0.5→15.0)
    6. Impact de la PERSISTANCE p (15 configs: 100 villes, m=100, cycles=300, p=0.1→0.95)
    7. Impact du ratio M/N (20 configs: 200 villes, cycles=300, m/n=0.1→5.0)
    8. Tests de REPRODUCTIBILITÉ (25 configs: seeds multiples sur configs variées)
    9. Configurations EXTRÊMES (10 configs: stress tests)

    Total : ~170 configurations
    Temps estimé en mode parallèle (12 cœurs) : ~4-6 heures

    Returns:
        Liste de configurations RunConfig
    """
    configs = []

    # ========== SÉRIE 1: IMPACT DU NOMBRE DE VILLES (20 configs) ==========
    # Question : Scalabilité de l'algorithme - comment le temps évolue avec n ?
    # Variables fixes : m = n (ratio 1:1), cycles = 300, seed = 42
    # Variable testée : n (nombre de villes)

    print("\n📊 Série 1 : Impact du nombre de villes (20 configs)")
    print("    Variables fixes: m=n, cycles=300, seed=42")
    villes_serie1 = [10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500]
    for n in villes_serie1:
        configs.append(RunConfig(n=n, m=n, cycles=300, seed=42))

    # ========== SÉRIE 2: IMPACT DU NOMBRE DE FOURMIS (25 configs) ==========
    # Question : Quelle est l'influence du nombre de fourmis sur qualité et temps ?
    # Variables fixes : n = 300, cycles = 300, seed = 42
    # Variable testée : m (nombre de fourmis)

    print("📊 Série 2 : Impact du nombre de fourmis (25 configs)")
    print("    Variables fixes: n=300, cycles=300, seed=42")
    fourmis_serie2 = [10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 750, 900,
                      1000, 1200, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
    for m in fourmis_serie2:
        configs.append(RunConfig(n=300, m=m, cycles=300, seed=42))

    # ========== SÉRIE 3: IMPACT DU NOMBRE DE CYCLES (15 configs) ==========
    # Question : Convergence - combien de cycles pour atteindre le plateau ?
    # Variables fixes : n = 200, m = 200, seed = 42
    # Variable testée : cycles
    # NOTE : Cette série teste les cycles, donc on va de 50 à 2000

    print("📊 Série 3 : Impact du nombre de cycles (15 configs)")
    print("    Variables fixes: n=200, m=200, seed=42")
    cycles_serie3 = [50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500, 2000]
    for cycles in cycles_serie3:
        configs.append(RunConfig(n=200, m=200, cycles=cycles, seed=42))

    # ========== SÉRIE 4: IMPACT DU PARAMÈTRE ALPHA (20 configs) ==========
    # Question : Importance des phéromones - quel alpha optimal ?
    # Variables fixes : n = 100, m = 100, cycles = 300, beta = 5.0, seed = 42
    # Variable testée : alpha (influence des phéromones)

    print("📊 Série 4 : Impact du paramètre alpha (20 configs)")
    print("    Variables fixes: n=100, m=100, cycles=300, beta=5.0, seed=42")
    alpha_serie4 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                    1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    for alpha in alpha_serie4:
        configs.append(RunConfig(n=100, m=100, cycles=300, alpha=alpha, beta=5.0, seed=42))

    # ========== SÉRIE 5: IMPACT DU PARAMÈTRE BETA (20 configs) ==========
    # Question : Importance de la visibilité (distance) - quel beta optimal ?
    # Variables fixes : n = 100, m = 100, cycles = 300, alpha = 1.0, seed = 42
    # Variable testée : beta (influence de la visibilité)

    print("📊 Série 5 : Impact du paramètre beta (20 configs)")
    print("    Variables fixes: n=100, m=100, cycles=300, alpha=1.0, seed=42")
    beta_serie5 = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                   5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 15.0]
    for beta in beta_serie5:
        configs.append(RunConfig(n=100, m=100, cycles=300, alpha=1.0, beta=beta, seed=42))

    # ========== SÉRIE 6: IMPACT DE LA PERSISTANCE p (15 configs) ==========
    # Question : Taux d'évaporation - combien de mémoire garder ?
    # Variables fixes : n = 100, m = 100, cycles = 300, seed = 42
    # Variable testée : p (facteur de persistance, 1-taux d'évaporation)

    print("📊 Série 6 : Impact de la persistance p (15 configs)")
    print("    Variables fixes: n=100, m=100, cycles=300, seed=42")
    p_serie6 = [0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.95]
    for p in p_serie6:
        configs.append(RunConfig(n=100, m=100, cycles=300, p=p, seed=42))

    # ========== SÉRIE 7: IMPACT DU RATIO FOURMIS/VILLES (20 configs) ==========
    # Question : Quel ratio m/n est optimal ? Exploration vs exploitation
    # Variables fixes : n = 200, cycles = 300, seed = 42
    # Variable testée : ratio m/n

    print("📊 Série 7 : Impact du ratio fourmis/villes (20 configs)")
    print("    Variables fixes: n=200, cycles=300, seed=42")
    ratios_serie7 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                     1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    for ratio in ratios_serie7:
        m = int(200 * ratio)
        configs.append(RunConfig(n=200, m=m, cycles=300, seed=42))

    # ========== SÉRIE 8: TESTS DE REPRODUCTIBILITÉ (25 configs) ==========
    # Question : Stabilité et variance des résultats
    # Variables fixes : cycles = 300
    # Variable testée : seed (graine aléatoire)

    print("📊 Série 8 : Tests de reproductibilité (25 configs)")
    print("    Variables fixes: cycles=300")
    seeds_serie8 = [42, 123, 456, 789, 2025]
    tailles_serie8 = [(30, 30), (50, 50), (100, 100), (200, 200), (300, 300)]
    for seed in seeds_serie8:
        for n, m in tailles_serie8:
            configs.append(RunConfig(n=n, m=m, cycles=300, seed=seed))

    # ========== SÉRIE 9: CONFIGURATIONS EXTRÊMES (9 configs) ==========
    # Question : Limites du système - où sont les frontières ?

    print("📊 Série 9 : Configurations extrêmes (9 configs)")
    configs.extend([
        # Beaucoup de villes, peu de fourmis, beaucoup de cycles
        RunConfig(n=500, m=50, cycles=300, seed=42),
        RunConfig(n=500, m=100, cycles=300, seed=42),

        # Peu de villes, énormément de fourmis
        RunConfig(n=100, m=1000, cycles=300, seed=42),
        RunConfig(n=100, m=2000, cycles=300, seed=42),
        RunConfig(n=150, m=1500, cycles=300, seed=42),

        # Configurations équilibrées grandes
        RunConfig(n=300, m=300, cycles=500, seed=42),
        RunConfig(n=400, m=400, cycles=300, seed=42),
        RunConfig(n=450, m=450, cycles=300, seed=42),

        # Configuration ultime (la plus grosse)
        RunConfig(n=500, m=500, cycles=300, seed=42),
        # RunConfig(n=500, m=500, cycles=500, seed=42),  # Retiré : trop long (~30 min)
    ])

    print(f"\n✅ Total : {len(configs)} configurations générées")
    print("📈 Approche scientifique exhaustive : UN paramètre varie à la fois")
    print("⚡ Minimum 300 cycles partout (sauf série 3)")
    print(f"⏱️  Temps estimé en parallèle (12 cœurs) : ~4-6 heures\n")

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


def run_default_benchmarks(quick_mode: bool = False, parallel: bool = False,
                          n_processes: Optional[int] = None) -> pd.DataFrame:
    """
    Construit une liste de RunConfig à partir des scénarios par défaut
    et appelle run_benchmarks(configs) ou run_benchmarks_parallel(configs).

    Args:
        quick_mode: Si True, utilise des configurations rapides pour tests
        parallel: Si True, exécute les benchmarks en parallèle sur tous les cœurs
        n_processes: Nombre de processus parallèles (None = tous les cœurs disponibles)

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

    # Choisir le mode d'exécution
    if parallel:
        n_cores = n_processes if n_processes else cpu_count()
        print(f"🚀 Mode parallèle activé - Utilisation de {n_cores} cœurs\n")
        df = run_benchmarks_parallel(configs, n_processes=n_processes)
    else:
        print("⏳ Mode séquentiel\n")
        df = run_benchmarks(configs)

    return df


def run_and_save_benchmarks(output_path: str = "exports/benchmarks.csv",
                            quick_mode: bool = False,
                            append: bool = False,
                            parallel: bool = False,
                            n_processes: Optional[int] = None) -> pd.DataFrame:
    """
    Lance les benchmarks par défaut et sauvegarde les résultats.

    Args:
        output_path: Chemin du fichier CSV de sortie
        quick_mode: Si True, utilise des tests rapides
        append: Si True, ajoute aux résultats existants au lieu de les écraser
        parallel: Si True, exécute en parallèle sur tous les cœurs
        n_processes: Nombre de processus parallèles (None = tous les cœurs)

    Returns:
        DataFrame avec les résultats
    """
    # Exécuter les benchmarks
    df = run_default_benchmarks(quick_mode=quick_mode, parallel=parallel, n_processes=n_processes)

    # Sauvegarder
    if append:
        from model.benchmark import append_benchmarks
        append_benchmarks(df, output_path)
    else:
        save_benchmarks(df, output_path)

    return df

