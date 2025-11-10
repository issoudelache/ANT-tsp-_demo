"""
Script en ligne de commande pour lancer les benchmarks ACO.
Utiliser ce script pour exécuter les benchmarks sans interface graphique.
"""
import argparse
import sys
import os

# Ajouter le répertoire courant au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller.benchmark_controller import run_and_save_benchmarks


def main():
    """
    Point d'entrée principal du script CLI.
    """
    parser = argparse.ArgumentParser(
        description="Lancer des benchmarks de performance pour l'algorithme ACO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run_benchmarks.py                           # Benchmarks complets
  python run_benchmarks.py --quick                   # Tests rapides
  python run_benchmarks.py --output results.csv      # Fichier de sortie personnalisé
  python run_benchmarks.py --append                  # Ajouter aux résultats existants
        """
    )

    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Mode rapide : teste seulement quelques configurations légères'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='exports/benchmarks.csv',
        help='Chemin du fichier CSV de sortie (défaut: exports/benchmarks.csv)'
    )

    parser.add_argument(
        '--append', '-a',
        action='store_true',
        help='Ajouter aux résultats existants au lieu de les écraser'
    )

    args = parser.parse_args()

    # Afficher les paramètres
    print("="*70)
    print(" BENCHMARKS ACO - Algorithme des Colonies de Fourmis")
    print("="*70)
    print(f"Mode: {'Rapide (tests légers)' if args.quick else 'Complet'}")
    print(f"Fichier de sortie: {args.output}")
    print(f"Mode d'écriture: {'Ajout' if args.append else 'Écrasement'}")
    print("="*70)
    print()

    # Exécuter les benchmarks
    try:
        df = run_and_save_benchmarks(
            output_path=args.output,
            quick_mode=args.quick,
            append=args.append
        )

        print("\n" + "="*70)
        print(" RÉSUMÉ DES RÉSULTATS")
        print("="*70)
        print(f"Nombre de configurations testées: {len(df)}")
        print(f"Temps moyen par configuration: {df['runtime_sec'].mean():.2f}s")
        print(f"Configuration la plus rapide: {df['runtime_sec'].min():.2f}s")
        print(f"Configuration la plus lente: {df['runtime_sec'].max():.2f}s")
        print(f"Meilleure solution trouvée: {df['best_len_global'].min():.2f}")
        print("="*70)
        print(f"\n✓ Résultats sauvegardés dans: {args.output}")

    except KeyboardInterrupt:
        print("\n\n⚠ Benchmarks interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution des benchmarks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

