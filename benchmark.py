"""
Script de benchmark pour tester les performances de l'algorithme ACO optimisé.
"""
import time
import sys
import os

# Ajouter le répertoire parent au chemin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine


def benchmark_config(n_cities, n_ants, n_cycles, seed=42):
    """
    Teste une configuration spécifique et retourne les statistiques de performance.

    Args:
        n_cities (int): Nombre de villes
        n_ants (int): Nombre de fourmis
        n_cycles (int): Nombre de cycles
        seed (int): Graine aléatoire

    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*70}")
    print(f"Configuration: {n_cities} villes, {n_ants} fourmis, {n_cycles} cycles")
    print(f"{'='*70}")

    # Génération des villes
    start_time = time.perf_counter()
    cities = generate_cities(n_cities, seed=seed)
    gen_time = time.perf_counter() - start_time
    print(f"✓ Génération des villes: {gen_time:.4f}s")

    # Initialisation du moteur ACO
    start_time = time.perf_counter()
    engine = ACOEngine(
        coords=cities,
        alpha=1.0,
        beta=5.0,
        p=0.5,
        Q=100.0,
        m=n_ants,
        seed=seed
    )
    init_time = time.perf_counter() - start_time
    print(f"✓ Initialisation du moteur: {init_time:.4f}s")

    # Exécution des cycles
    print(f"\nExécution de {n_cycles} cycles...")
    start_time = time.perf_counter()

    total_construction_time = 0
    total_evaporation_time = 0
    total_deposit_time = 0

    progress_interval = max(n_cycles // 10, 1)

    for cycle_idx in range(1, n_cycles + 1):
        stats = engine.run_cycle()

        total_construction_time += stats['time_construction']
        total_evaporation_time += stats['time_evaporation']
        total_deposit_time += stats['time_deposit']

        if cycle_idx % progress_interval == 0 or cycle_idx == n_cycles:
            print(f"  Cycle {cycle_idx}/{n_cycles} - "
                  f"Meilleure: {engine.best_len_global:.2f}")

    total_time = time.perf_counter() - start_time

    # Affichage des résultats
    print(f"\n{'='*70}")
    print(f"RÉSULTATS")
    print(f"{'='*70}")
    print(f"Temps total d'exécution:    {total_time:.4f}s")
    print(f"Temps moyen par cycle:      {total_time/n_cycles:.4f}s")
    print(f"\nDétails par phase:")
    print(f"  - Construction de tours:  {total_construction_time:.4f}s ({total_construction_time/total_time*100:.1f}%)")
    print(f"  - Évaporation:            {total_evaporation_time:.4f}s ({total_evaporation_time/total_time*100:.1f}%)")
    print(f"  - Dépôt de phéromones:    {total_deposit_time:.4f}s ({total_deposit_time/total_time*100:.1f}%)")
    print(f"\nMeilleure solution trouvée: {engine.best_len_global:.2f}")
    print(f"Tour: {engine.best_tour_global}")

    return {
        'n_cities': n_cities,
        'n_ants': n_ants,
        'n_cycles': n_cycles,
        'gen_time': gen_time,
        'init_time': init_time,
        'total_time': total_time,
        'time_per_cycle': total_time / n_cycles,
        'construction_time': total_construction_time,
        'evaporation_time': total_evaporation_time,
        'deposit_time': total_deposit_time,
        'best_length': engine.best_len_global,
        'best_tour': engine.best_tour_global
    }


def run_benchmarks():
    """
    Exécute une série de benchmarks avec différentes configurations.
    """
    print("="*70)
    print(" BENCHMARK ACO - Algorithme optimisé avec NumPy vectorisé")
    print("="*70)

    # Configurations à tester
    configs = [
        # (n_cities, n_ants, n_cycles)
        (20, 20, 100),      # Petit problème
        (50, 50, 500),      # Problème moyen
        (100, 100, 1000),   # Grand problème
        (200, 100, 500),    # Très grand problème
    ]

    results = []

    for n_cities, n_ants, n_cycles in configs:
        try:
            result = benchmark_config(n_cities, n_ants, n_cycles)
            results.append(result)
        except KeyboardInterrupt:
            print("\n\n⚠ Benchmark interrompu par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            continue

    # Résumé final
    if results:
        print(f"\n\n{'='*70}")
        print(" RÉSUMÉ DES BENCHMARKS")
        print(f"{'='*70}")
        print(f"{'Villes':<10} {'Fourmis':<10} {'Cycles':<10} {'Temps total':<15} {'Temps/cycle':<15}")
        print(f"{'-'*70}")
        for r in results:
            print(f"{r['n_cities']:<10} {r['n_ants']:<10} {r['n_cycles']:<10} "
                  f"{r['total_time']:.4f}s{' '*8} {r['time_per_cycle']:.6f}s")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark de l'algorithme ACO")
    parser.add_argument('--cities', type=int, help='Nombre de villes')
    parser.add_argument('--ants', type=int, help='Nombre de fourmis')
    parser.add_argument('--cycles', type=int, help='Nombre de cycles')
    parser.add_argument('--seed', type=int, default=42, help='Graine aléatoire')

    args = parser.parse_args()

    if args.cities and args.ants and args.cycles:
        # Benchmark d'une configuration spécifique
        benchmark_config(args.cities, args.ants, args.cycles, args.seed)
    else:
        # Exécuter la série de benchmarks
        run_benchmarks()

