"""
Script pour compter les configurations de benchmarks
"""
from controller.benchmark_controller import get_default_benchmark_configs
import collections

configs = get_default_benchmark_configs()

print(f"{'='*70}")
print(f"CONFIGURATIONS DE BENCHMARKS - RÉSUMÉ")
print(f"{'='*70}")
print(f"\nNombre total de configurations: {len(configs)}")

print(f"\n{'='*70}")
print("RÉPARTITION PAR NOMBRE DE VILLES")
print(f"{'='*70}")
counts = collections.Counter([c.n for c in configs])
for n in sorted(counts.keys()):
    print(f"  {n:3d} villes: {counts[n]:2d} configurations")

print(f"\n{'='*70}")
print("RÉPARTITION PAR NOMBRE DE CYCLES")
print(f"{'='*70}")
counts_cycles = collections.Counter([c.cycles for c in configs])
for cycles in sorted(counts_cycles.keys()):
    print(f"  {cycles:4d} cycles: {counts_cycles[cycles]:2d} configurations")

print(f"\n{'='*70}")
print("EXEMPLES DE CONFIGURATIONS")
print(f"{'='*70}")
print("\nPremières configurations (petits problèmes):")
for i, config in enumerate(configs[:5]):
    print(f"  {i+1}. {config.n} villes, {config.m} fourmis, {config.cycles} cycles")

print("\nDernières configurations (gros problèmes):")
for i, config in enumerate(configs[-5:], len(configs)-4):
    print(f"  {i}. {config.n} villes, {config.m} fourmis, {config.cycles} cycles")

print(f"\n{'='*70}")
print("ESTIMATION DU TEMPS")
print(f"{'='*70}")
print("Temps estimé total: 8-12 heures")
print("⚠️  RECOMMANDATION: Lancer le soir avant de dormir!")
print(f"{'='*70}\n")

