"""
Module de benchmarks pour mesurer les performances de l'algorithme ACO.

Ce module permet de :
- Lancer des tests de performance avec différentes configurations
- Mesurer le temps d'exécution et la qualité des solutions
- Sauvegarder et charger les résultats de benchmarks au format CSV
- Exécuter les benchmarks en parallèle sur tous les cœurs disponibles
"""
import time
import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine


@dataclass
class RunConfig:
    """
    Configuration pour un run de benchmark.

    Attributes:
        n: Nombre de villes
        m: Nombre de fourmis
        cycles: Nombre de cycles à exécuter
        alpha: Paramètre d'influence des phéromones
        beta: Paramètre d'influence de la visibilité
        p: Facteur de persistance des phéromones (1 - taux d'évaporation)
        Q: Constante pour le dépôt de phéromones
        seed: Graine pour le générateur aléatoire
    """
    n: int
    m: int
    cycles: int
    alpha: float = 1.0
    beta: float = 5.0
    p: float = 0.5
    Q: float = 100.0
    seed: int = 42


def run_single_benchmark(config: RunConfig, verbose: bool = True) -> Optional[Dict[str, Any]]:
    """
    Exécute un seul run ACO pour une configuration donnée et retourne les métriques.

    Cette fonction est conçue pour être utilisable avec multiprocessing.Pool.map()
    pour paralléliser les benchmarks.

    Args:
        config: Configuration de benchmark à tester
        verbose: Si True, affiche les informations de progression

    Returns:
        Dictionnaire contenant les métriques du run, ou None en cas d'erreur :
        - n, m, cycles, alpha, beta, p, Q, seed: paramètres de la config
        - runtime_sec: temps total d'exécution en secondes
        - time_per_cycle: temps moyen par cycle en secondes
        - best_len_global: meilleure longueur de tour trouvée
        - mean_len_final: longueur moyenne au dernier cycle
        - improvement_pct: amélioration en % entre le premier et le dernier cycle
    """
    if verbose:
        print(f"  Début config: n={config.n}, m={config.m}, cycles={config.cycles}")

    try:
        # Générer les villes
        cities = generate_cities(config.n, seed=config.seed)

        # Initialiser le moteur ACO
        engine = ACOEngine(
            coords=cities,
            alpha=config.alpha,
            beta=config.beta,
            p=config.p,
            Q=config.Q,
            m=config.m,
            seed=config.seed
        )

        # Mesurer le temps d'exécution
        start_time = time.perf_counter()

        # Exécuter tous les cycles
        first_best_len = None
        last_mean_len = None

        for cycle_idx in range(1, config.cycles + 1):
            stats = engine.run_cycle()

            # Mémoriser les stats du premier cycle
            if cycle_idx == 1:
                first_best_len = stats['best_len_cycle']

            # Mémoriser les stats du dernier cycle
            if cycle_idx == config.cycles:
                last_mean_len = stats['mean_len_cycle']

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Calculer l'amélioration
        improvement_pct = 0.0
        if first_best_len and first_best_len > 0:
            improvement_pct = ((first_best_len - engine.best_len_global) /
                              first_best_len * 100.0)

        # Construire le résultat
        result = {
            'n': config.n,
            'm': config.m,
            'cycles': config.cycles,
            'alpha': config.alpha,
            'beta': config.beta,
            'p': config.p,
            'Q': config.Q,
            'seed': config.seed,
            'runtime_sec': total_time,
            'time_per_cycle': total_time / config.cycles,
            'best_len_global': engine.best_len_global,
            'mean_len_final': last_mean_len,
            'improvement_pct': improvement_pct
        }

        if verbose:
            print(f"  ✓ Terminé: n={config.n}, m={config.m} - "
                  f"Temps: {total_time:.2f}s - "
                  f"Meilleure: {engine.best_len_global:.2f}")

        return result

    except Exception as e:
        print(f"  ❌ Erreur config n={config.n}, m={config.m}: {e}")
        return None


def run_benchmarks(configs: List[RunConfig]) -> pd.DataFrame:
    """
    Exécute une série de runs ACO de manière séquentielle pour différentes configurations,
    mesure le temps d'exécution et la qualité de la solution.

    Args:
        configs: Liste de configurations à tester

    Returns:
        DataFrame avec une ligne par configuration testée, contenant :
        - n: nombre de villes
        - m: nombre de fourmis
        - cycles: nombre de cycles
        - alpha, beta, p, Q: paramètres ACO
        - seed: graine aléatoire
        - runtime_sec: temps total d'exécution en secondes
        - time_per_cycle: temps moyen par cycle en secondes
        - best_len_global: meilleure longueur de tour trouvée
        - mean_len_final: longueur moyenne au dernier cycle
        - improvement_pct: amélioration en % entre le premier et le dernier cycle
    """
    results = []

    print(f"Exécution séquentielle de {len(configs)} configurations...")

    for idx, config in enumerate(configs):
        print(f"\n{'='*70}")
        print(f"Benchmark {idx+1}/{len(configs)}: n={config.n}, m={config.m}, cycles={config.cycles}")
        print(f"{'='*70}")

        # Exécuter un seul benchmark
        result = run_single_benchmark(config, verbose=True)

        if result is not None:
            results.append(result)

            # Afficher le résumé
            print(f"✓ Terminé en {result['runtime_sec']:.2f}s - "
                  f"Meilleure: {result['best_len_global']:.2f} - "
                  f"Amélioration: {result['improvement_pct']:.1f}%")

    # Convertir en DataFrame
    df = pd.DataFrame(results)
    return df


def run_benchmarks_parallel(configs: List[RunConfig], n_processes: Optional[int] = None) -> pd.DataFrame:
    """
    Exécute une série de runs ACO en parallèle sur plusieurs cœurs pour différentes configurations,
    mesure le temps d'exécution et la qualité de la solution.

    Cette version utilise multiprocessing.Pool pour distribuer les benchmarks sur tous les cœurs
    disponibles, offrant un speedup significatif pour les grandes suites de tests.

    Args:
        configs: Liste de configurations à tester
        n_processes: Nombre de processus parallèles. Si None, utilise tous les cœurs disponibles.

    Returns:
        DataFrame avec une ligne par configuration testée, contenant les mêmes colonnes
        que run_benchmarks().
    """
    if n_processes is None:
        n_processes = cpu_count()

    print(f"Exécution parallèle de {len(configs)} configurations sur {n_processes} cœurs...")
    print(f"⚡ Mode multi-cœur activé!")

    # Exécuter les benchmarks en parallèle
    start_time = time.perf_counter()

    with Pool(processes=n_processes) as pool:
        # map() bloque jusqu'à ce que tous les jobs soient terminés
        results = pool.map(run_single_benchmark, configs)

    end_time = time.perf_counter()
    total_parallel_time = end_time - start_time

    # Filtrer les résultats None (erreurs)
    results = [r for r in results if r is not None]

    print(f"\n{'='*70}")
    print(f"✅ Benchmarks parallèles terminés!")
    print(f"  Temps total: {total_parallel_time:.2f}s")
    print(f"  Configurations réussies: {len(results)}/{len(configs)}")
    print(f"  Cœurs utilisés: {n_processes}")

    # Calculer le temps séquentiel estimé
    total_seq_time = sum(r['runtime_sec'] for r in results)
    speedup = total_seq_time / total_parallel_time if total_parallel_time > 0 else 1.0
    print(f"  Temps séquentiel estimé: {total_seq_time:.2f}s")
    print(f"  Speedup: {speedup:.2f}x")
    print(f"{'='*70}\n")

    # Convertir en DataFrame
    df = pd.DataFrame(results)
    return df


def save_benchmarks(df: pd.DataFrame, path: str) -> None:
    """
    Sauvegarde le DataFrame de benchmarks au format CSV dans le fichier indiqué.
    Crée le dossier cible si nécessaire.

    Args:
        df: DataFrame contenant les résultats de benchmarks
        path: Chemin du fichier CSV à créer/écraser
    """
    # Créer le dossier parent si nécessaire
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Dossier créé: {directory}")

    # Sauvegarder le CSV
    df.to_csv(path, index=False, encoding='utf-8')
    print(f"✓ Benchmarks sauvegardés: {path}")


def load_benchmarks(path: str) -> Optional[pd.DataFrame]:
    """
    Charge un CSV de benchmarks si le fichier existe.
    Retourne None si le fichier n'existe pas encore.

    Args:
        path: Chemin du fichier CSV à charger

    Returns:
        DataFrame avec les résultats de benchmarks, ou None si le fichier n'existe pas
    """
    if not os.path.exists(path):
        return None

    try:
        df = pd.read_csv(path, encoding='utf-8')
        print(f"✓ Benchmarks chargés: {path} ({len(df)} lignes)")
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement des benchmarks: {e}")
        return None


def append_benchmarks(df: pd.DataFrame, path: str) -> None:
    """
    Ajoute de nouveaux résultats de benchmarks à un fichier CSV existant.
    Si le fichier n'existe pas, le crée.

    Args:
        df: DataFrame contenant les nouveaux résultats
        path: Chemin du fichier CSV
    """
    existing_df = load_benchmarks(path)

    if existing_df is not None:
        # Fusionner les anciens et nouveaux résultats
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        save_benchmarks(combined_df, path)
        print(f"✓ {len(df)} nouveaux benchmarks ajoutés (total: {len(combined_df)})")
    else:
        # Créer un nouveau fichier
        save_benchmarks(df, path)
        print(f"✓ Nouveau fichier de benchmarks créé avec {len(df)} entrées")

