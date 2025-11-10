"""
Test rapide pour vérifier que le système de benchmarks fonctionne correctement.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.benchmark import RunConfig, run_benchmarks, save_benchmarks

print("="*70)
print("TEST RAPIDE DU SYSTÈME DE BENCHMARKS")
print("="*70)
print()

# Créer une configuration de test très simple
configs = [
    RunConfig(n=10, m=10, cycles=5, seed=42),
    RunConfig(n=15, m=15, cycles=5, seed=42),
]

print(f"Exécution de {len(configs)} configurations de test...")
print()

# Exécuter les benchmarks
df = run_benchmarks(configs)

print()
print("="*70)
print("RÉSULTATS")
print("="*70)
print(df)
print()

# Sauvegarder
save_benchmarks(df, "exports/test_benchmarks.csv")

print()
print("✓ Test réussi ! Le système de benchmarks fonctionne correctement.")
print()

